"""Plant Doctor - Crop Disease Detection, Severity Grading & Expert Finder (Streamlit)

Run:  streamlit run app.py
"""
import csv
import hashlib
import io
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.help_finder import INDIA_STATES, get_help
from utils.knowledge import SAFETY_NOTE, action_plan, all_entries, find_entry
from utils.model_loader import Predictor, load_class_names, model_files_present, pretty
from utils.preprocess import load_image, to_model_input
from utils.report import build_html_report
from utils.severity import estimate_severity

st.set_page_config(page_title="Plant Doctor", page_icon="🌿", layout="wide")
st.session_state.setdefault("history", [])
st.session_state.setdefault("seen", set())


@st.cache_resource(show_spinner="Loading model...")
def get_predictor():
    return Predictor()


def urgency_box(container, urgency, text):
    {"High": container.error, "Medium": container.warning}.get(urgency, container.success)(text)


def render_entry(entry, key_prefix=""):
    """Full disease card: facts + how to deal with it."""
    c1, c2, c3 = st.columns(3)
    c1.metric("Type", entry["type"])
    c2.metric("Cause", entry["pathogen"])
    c3.metric("Urgency", entry["urgency"])
    st.markdown(f"**Symptoms:** {entry['symptoms']}")
    st.markdown(f"**Favoured by:** {entry['favours']}")
    with st.expander("Field practices (cultural control)", expanded=True):
        st.markdown("\n".join(f"- {x}" for x in entry["cultural"]) or "-")
    with st.expander("Organic / biological options"):
        st.markdown("\n".join(f"- {x}" for x in entry["organic"]) or "No effective organic option; focus on field practices.")
    with st.expander("Chemical options (confirm locally)"):
        st.markdown("\n".join(f"- {x}" for x in entry["chemical"]) or "No chemical cure; prevention and removal are the main tools.")
        st.caption(SAFETY_NOTE)
    with st.expander("Prevention for next season"):
        st.markdown("\n".join(f"- {x}" for x in entry["prevention"]) or "-")


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("🌿 Plant Doctor")
    st.caption("Lightweight MobileNetV2 + OpenCV. Runs on CPU, no cloud.")
    st.header("1. Image")
    mode = st.radio("Image source", ["Upload image", "Use camera"])
    show_masks = st.checkbox("Show severity masks", value=False)
    conf_threshold = st.slider("Minimum confidence to trust a diagnosis", 0.30, 0.95, 0.60, 0.05)

    st.header("2. Your location")
    country = st.selectbox("Country", ["India", "Other country"])
    state, district = "", ""
    if country == "India":
        state = st.selectbox("State / UT", ["-- select --"] + INDIA_STATES)
    district = st.text_input("District / town", placeholder="e.g. your district name")
    crop_hint = st.text_input("Crop (optional)", placeholder="e.g. tomato")

    if model_files_present():
        names = [n for n in load_class_names() if not n.startswith("Unknown")]
        groups = {}
        for n in names:
            c, d = pretty(n)
            groups.setdefault(c, []).append(d)
        with st.expander(f"Model supports {len(groups)} plants / {len(names)} conditions"):
            for c in sorted(groups):
                st.markdown(f"**{c}**: " + ", ".join(sorted(groups[c])))
    st.markdown("---")
    st.markdown("**Photo tips**\n- One leaf, filling the frame\n- Plain background\n- Even daylight, no flash")

# ------------------------------------------------------------------ scan
def run_scan(file):
    raw = file.getvalue()
    rgb = load_image(io.BytesIO(raw))
    sev = estimate_severity(rgb)

    top, status, err = [], "nomodel", None
    if model_files_present():
        try:
            top = get_predictor().top_k(to_model_input(rgb), k=5)
            best_label, best_p = top[0]
            if best_label.startswith("Unknown"):
                status = "unknown"
            elif best_p < conf_threshold:
                status = "uncertain"
            else:
                status = "confident"
        except Exception as e:  # noqa: BLE001
            status, err = "error", str(e)

    crop = disease = ""
    entry = plan = None
    if status in ("confident", "uncertain"):
        crop, disease = pretty(top[0][0])
        entry = find_entry(crop, disease)
        plan = action_plan(entry, sev.percent, sev.grade)

    help_ = get_help(country, state if not state.startswith("--") else "", district, crop or crop_hint)

    # history (once per distinct image)
    h = hashlib.md5(raw).hexdigest()
    if h not in st.session_state["seen"]:
        st.session_state["seen"].add(h)
        st.session_state["history"].append({
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Plant": crop or "-", "Condition": disease or ("Not a leaf" if status == "unknown" else "-"),
            "Confidence %": round(top[0][1] * 100, 1) if top else None,
            "Severity %": sev.percent, "Grade": sev.grade,
        })

    t_diag, t_treat, t_help, t_report = st.tabs(
        ["🩺 Diagnosis", "💊 How to deal with it", "📍 Who to contact", "📄 Report"])

    # ---- Diagnosis
    with t_diag:
        c1, c2 = st.columns([1, 1.2])
        c1.image(rgb, caption="Your image", width=380)
        if status == "nomodel":
            c2.warning("No trained model in `model/` yet. Train it with `notebooks/kaggle_train.ipynb`, "
                       "then add `leaf_model.keras` and `class_names.json`. Severity grading and the Disease "
                       "library already work.")
        elif status == "error":
            c2.error(f"Could not run the model: {err}")
        elif status == "unknown":
            c2.error("This does not look like a leaf from a supported plant. Try a close, well-lit photo of a single leaf.")
        else:
            if status == "uncertain":
                c2.warning(f"Not sure: best guess is below your {conf_threshold*100:.0f}% confidence threshold. "
                           "Treat the results below as possibilities and confirm with an expert.")
            m1, m2, m3 = c2.columns(3)
            m1.metric("Plant", crop)
            m2.metric("Condition", disease)
            m3.metric("Confidence", f"{top[0][1]*100:.1f}%")
            urgency_box(c2, entry["urgency"], f"Urgency: **{entry['urgency']}** - {plan['headline']}")

        if top:
            st.subheader("Possible diseases (ranked)")
            rows = []
            for lab, p in top:
                if lab.startswith("Unknown"):
                    rows.append(("Not a supported leaf", p * 100))
                else:
                    c, d = pretty(lab)
                    rows.append((f"{c} - {d}", p * 100))
            df = pd.DataFrame(rows, columns=["Possibility", "Probability %"]).set_index("Possibility")
            st.bar_chart(df)
            for lab, p in top[1:3]:
                if lab.startswith("Unknown") or p < 0.03:
                    continue
                c, d = pretty(lab)
                e2 = find_entry(c, d)
                with st.expander(f"Also possible: {c} - {d} ({p*100:.1f}%)"):
                    st.markdown(f"**{e2['title']}** ({e2['type']}). {e2['symptoms']}")
                    if e2["cultural"]:
                        st.markdown(f"**First step:** {e2['cultural'][0]}")

        st.subheader("Severity estimate")
        s1, s2, s3 = st.columns(3)
        s1.metric("Affected leaf area", f"{sev.percent:.1f}%")
        s2.metric("Grade", sev.grade)
        s3.metric("Leaf health score", f"{max(0, 100 - sev.percent):.0f}/100")
        st.progress(min(sev.percent / 100.0, 1.0))
        st.image(sev.overlay, caption="Red = area flagged as diseased, yellow outline = detected leaf", width=380)
        if show_masks:
            a, b = st.columns(2)
            a.image(sev.leaf_mask, caption="Leaf mask", width=300)
            b.image(sev.disease_mask, caption="Disease mask", width=300)

    # ---- Treatment
    with t_treat:
        if entry is None:
            st.info("Run a scan with the trained model to get a treatment plan, or browse the "
                    "**Disease library** tab for any condition.")
        else:
            if status == "uncertain":
                st.warning("Low-confidence diagnosis: the plan below is for the best guess only.")
            st.subheader(f"{entry['title']} on {crop}")
            st.markdown(f"### Action plan: {plan['headline']}")
            st.caption(f"Timeframe: {plan['timeframe']}")
            st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(plan["steps"], 1)))
            st.markdown("---")
            render_entry(entry)

    # ---- Help
    with t_help:
        st.subheader("Get expert help" + (f" near {help_['place']}" if help_["place"] else ""))
        if not help_["place"]:
            st.info("Enter your state and district in the sidebar to get map links for the nearest offices.")
        st.markdown("**Contacts and official resources**")
        for c in help_["contacts"]:
            line = f"**{c['name']}**"
            if c.get("phone"):
                line += f" - 📞 **{c['phone']}**"
            st.markdown(line)
            st.caption(c["detail"])
            if c.get("url"):
                st.link_button("Open website", c["url"])
        st.markdown("**Find the nearest on the map**")
        cols = st.columns(2)
        for i, (label, url) in enumerate(help_["searches"]):
            cols[i % 2].link_button(f"🗺️ {label}", url)
        st.caption("Tip: take your leaf photos, this report and the crop's age/stage when you visit or call.")

    # ---- Report
    with t_report:
        conf_text = f"{top[0][1]*100:.1f}%" if top else "-"
        report = build_html_report(dict(
            plant=crop or crop_hint or "-", condition=disease or "-", confidence_text=conf_text,
            top=[(" - ".join(pretty(l)) if not l.startswith("Unknown") else "Not a leaf", p) for l, p in top],
            severity=sev.percent, grade=sev.grade, place=help_["place"], entry=entry, plan=plan,
            contacts=help_["contacts"], rgb=rgb, overlay=sev.overlay, safety=SAFETY_NOTE))
        st.subheader("Shareable plant health report")
        st.write("Download it, open in a browser and use Print -> Save as PDF to share with an expert or keep for records.")
        st.download_button("⬇️ Download report (HTML)", report, file_name="plant_health_report.html", mime="text/html")


# ------------------------------------------------------------------ pages
st.title("🌿 Plant Doctor")
st.caption("Detect the disease, measure severity, learn how to deal with it and find the nearest expert.")

tab_scan, tab_lib, tab_hist = st.tabs(["🔍 Scan a leaf", "📚 Disease library", "🕒 Scan history"])

with tab_scan:
    if mode == "Upload image":
        file = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])
    else:
        file = st.camera_input("Take a photo of a leaf")
    if file is None:
        st.info("Upload or capture a leaf image to begin.")
    else:
        run_scan(file)

with tab_lib:
    st.subheader("Disease library")
    st.write("Read about any condition without scanning: symptoms, how to deal with it and prevention.")
    entries = [e for e in all_entries() if e["id"] != "healthy"]
    titles = sorted(e["title"] for e in entries)
    pick = st.selectbox("Choose a disease or pest", titles)
    sel = next(e for e in entries if e["title"] == pick)
    st.markdown(f"### {sel['title']}")
    render_entry(sel)

with tab_hist:
    st.subheader("Scan history (this session)")
    hist = st.session_state["history"]
    if not hist:
        st.info("No scans yet.")
    else:
        st.dataframe(pd.DataFrame(hist), use_container_width=True)
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(hist[0].keys()))
        w.writeheader()
        w.writerows(hist)
        st.download_button("⬇️ Download history (CSV)", buf.getvalue(), file_name="scan_history.csv", mime="text/csv")
        if st.button("Clear history"):
            st.session_state["history"], st.session_state["seen"] = [], set()
            st.rerun()

st.markdown("---")
st.caption("AI-assisted estimate. Severity is a colour-based heuristic. This tool supports, but does not replace, "
           "diagnosis by a qualified agriculture expert. " + SAFETY_NOTE)
