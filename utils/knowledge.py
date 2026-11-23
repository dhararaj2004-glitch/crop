"""Disease knowledge base: what the disease is, how to deal with it, and how urgent it is.

General, widely published agronomy guidance (university-extension style). It is NOT a
prescription: pesticide products, doses and legality differ by country/state, so the app
always tells users to confirm with a local agriculture officer and follow the product label.
"""
import re

SAFETY_NOTE = (
    "Use only pesticides registered for your crop and region, follow the label (dose, interval before "
    "harvest, protective gear), never mix products unless the label allows it, and confirm the plan "
    "with a local agriculture / extension officer first."
)

URGENCY_ORDER = {"None": 0, "Low": 1, "Medium": 2, "High": 3}


def _e(id_, title, keywords, type_, pathogen, urgency, symptoms, favours,
       cultural, organic, chemical, prevention, incurable=False):
    return dict(id=id_, title=title, keywords=keywords, type=type_, pathogen=pathogen,
                urgency=urgency, symptoms=symptoms, favours=favours, cultural=cultural,
                organic=organic, chemical=chemical, prevention=prevention, incurable=incurable)


ENTRIES = [
    _e("healthy", "Healthy leaf", ["healthy"], "None", "-", "None",
       "No visible disease symptoms.", "-",
       ["Keep scouting the field once a week, especially after rain or humid spells."],
       [], [],
       ["Use clean seed/seedlings, balanced fertiliser, good spacing and drainage, and rotate crops."]),

    _e("late_blight", "Late blight", ["lateblight"], "Fungus-like (oomycete)", "Phytophthora infestans", "High",
       "Dark, water-soaked patches on leaves and stems that spread fast; white fuzzy growth on the underside in humid weather; brown rot on tomato fruit and potato tubers.",
       "Cool, cloudy, wet or very humid weather; long leaf-wetness periods.",
       ["Remove and destroy (bag or bury, do not compost) infected plants or leaves immediately.",
        "Avoid overhead irrigation; water at the base in the morning.",
        "Improve spacing and airflow; destroy volunteer plants and cull piles."],
       ["Copper-based fungicides used as a preventive protectant spray (follow label)."],
       ["Protectant fungicides such as mancozeb or chlorothalonil; systemic/curative options (for example metalaxyl or cymoxanil mixtures) where locally recommended. Rotate modes of action to avoid resistance."],
       ["Plant certified disease-free seed tubers/seedlings and resistant varieties.", "Scout often in cool, wet weather and spray preventively when forecasts favour disease."]),

    _e("early_blight", "Early blight", ["earlyblight"], "Fungus", "Alternaria solani", "Medium",
       "Brown spots with concentric rings (target-like) and a yellow halo, starting on older lower leaves; leaves yellow and drop; dark sunken spots on stems or fruit.",
       "Warm weather with alternating wet and dry spells; stressed or nutrient-poor plants.",
       ["Remove affected lower leaves and crop debris.", "Mulch the soil to stop splash; water at the base.",
        "Keep plants well fed (balanced nitrogen and potassium) and avoid drought stress."],
       ["Copper fungicides or Bacillus subtilis-based biofungicides as protectants."],
       ["Fungicides such as mancozeb, chlorothalonil or strobilurins (for example azoxystrobin), rotated per label."],
       ["Rotate crops for 2-3 years away from tomato/potato family.", "Use clean seed and resistant or tolerant varieties."]),

    _e("bacterial_spot", "Bacterial spot", ["bacterialspot"], "Bacteria", "Xanthomonas species", "Medium",
       "Small water-soaked spots that turn dark brown/black, often with a yellow halo; leaves may look ragged; raised scabby spots on fruit.",
       "Warm, wet, windy weather; splashing rain or overhead irrigation.",
       ["Avoid working in wet fields; disinfect tools.", "Remove and destroy badly infected plants and debris.",
        "Use drip or base watering."],
       ["Copper-based bactericides can slow spread (preventive, repeat per label)."],
       ["Copper products, often mixed with mancozeb in tomato/pepper where locally advised; antibiotics are restricted in many places."],
       ["Use certified disease-free seed (hot-water seed treatment where recommended).", "Rotate away from host crops for 1-2 years."]),

    _e("leaf_mold", "Leaf mold", ["leafmold"], "Fungus", "Passalora fulva (Fulvia fulva)", "Medium",
       "Pale green/yellow patches on the upper leaf surface with olive-green to brown velvety mold underneath; leaves curl and dry.",
       "High humidity (above ~85%) and poor ventilation, common in greenhouses and polyhouses.",
       ["Increase ventilation and lower humidity; space and prune plants.", "Water at the base, early in the day.",
        "Remove infected leaves."],
       ["Copper or biofungicide sprays as protectants."],
       ["Fungicides such as chlorothalonil or mancozeb where locally recommended."],
       ["Use resistant varieties and clean the structure between crops."]),

    _e("septoria", "Septoria leaf spot", ["septoria"], "Fungus", "Septoria lycopersici", "Medium",
       "Many small round spots with dark borders and grey-white centres (tiny black dots inside) on lower leaves; heavy leaf drop.",
       "Warm, wet, humid weather; splashing water.",
       ["Remove infected lower leaves; avoid wetting foliage.", "Mulch and stake plants for airflow.", "Clear debris after harvest."],
       ["Copper-based sprays as protectants."],
       ["Fungicides such as chlorothalonil or mancozeb, per label."],
       ["Rotate crops for 2-3 years; use clean seed."]),

    _e("target_spot", "Target spot", ["targetspot"], "Fungus", "Corynespora cassiicola", "Medium",
       "Brown spots with concentric rings and a light centre on leaves, sometimes on stems and fruit; can cause defoliation.",
       "Warm, humid weather with long leaf wetness.",
       ["Remove infected leaves and debris.", "Improve airflow and avoid overhead watering."],
       ["Copper or biofungicide protectants."],
       ["Protectant or strobilurin/triazole fungicides where locally recommended."],
       ["Rotate crops and use drip irrigation."]),

    _e("spider_mites", "Spider mites (two-spotted)", ["spidermite"], "Pest (mite)", "Tetranychus urticae", "Medium",
       "Fine yellow stippling on leaves, fine webbing, bronzed and dry leaves; tiny moving dots on the underside.",
       "Hot, dry, dusty conditions; plants under water stress.",
       ["Spray the underside of leaves with a strong jet of water.", "Remove heavily infested leaves; keep plants watered.",
        "Reduce dust and avoid sprays that kill natural enemies."],
       ["Neem oil, insecticidal soap or horticultural oil; release predatory mites where available."],
       ["Miticides (for example abamectin or sulfur-based) only if locally registered and recommended; rotate chemistries."],
       ["Scout weekly in hot dry spells; encourage natural predators."]),

    _e("yellow_leaf_curl", "Yellow leaf curl virus", ["yellowleafcurl", "tylcv"], "Virus (spread by whitefly)", "Tomato yellow leaf curl virus", "High",
       "Leaves curl upward and turn yellow at the edges, plants are stunted, few or no fruit.",
       "Whitefly populations, warm weather, nearby infected plants or weeds.",
       ["Remove and destroy infected plants early; there is no cure.", "Control whiteflies: yellow sticky traps, insect-proof nets in nurseries, reflective mulch.",
        "Weed out nearby hosts."],
       ["Neem oil or insecticidal soap to reduce whiteflies."],
       ["Whitefly insecticides only as locally recommended (they protect healthy plants, they do not cure infected ones)."],
       ["Plant resistant or tolerant varieties and raise seedlings under nets.", "Avoid planting next to older infected crops."], incurable=True),

    _e("cassava_mosaic", "Cassava mosaic / brown streak", ["cassavamosaic", "cassavabrownstreak", "cassavamosaicdisease"], "Virus (whitefly)", "Cassava mosaic / brown streak viruses", "High",
       "Yellow-green mosaic and distorted small leaves, stunted plants, poor roots.",
       "Infected cuttings and whiteflies.",
       ["Remove and destroy infected plants (rogue early).", "Use only healthy cuttings."],
       [], [], ["Plant resistant varieties and certified clean cuttings."], incurable=True),

    _e("mosaic_virus", "Mosaic virus", ["mosaicvirus", "mosaic"], "Virus", "Tomato/Tobacco mosaic virus (and relatives)", "High",
       "Light and dark green mottling, distorted or fern-like leaves, stunted growth, uneven fruit ripening.",
       "Spreads by hands, tools, infected seed and plant debris.",
       ["Remove and destroy infected plants (no cure).", "Disinfect tools and wash hands between plants; avoid handling tobacco before touching plants.",
        "Control weeds that host the virus."],
       [], [],
       ["Use certified virus-free seed and resistant varieties.", "Rotate crops and clean up debris."], incurable=True),

    _e("apple_scab", "Apple scab", ["applescab"], "Fungus", "Venturia inaequalis", "Medium",
       "Olive-green to dark velvety spots on leaves and fruit that become scabby and cracked; early leaf drop.",
       "Cool, wet spring weather.",
       ["Rake and destroy fallen leaves in autumn.", "Prune for open canopy and airflow."],
       ["Sulfur or copper-based protectant sprays (timing per local advice)."],
       ["Protectant fungicides such as captan or mancozeb on a local spray schedule."],
       ["Plant scab-resistant varieties."]),

    _e("black_rot", "Black rot", ["blackrot"], "Fungus", "Botryosphaeria obtusa (apple) / Guignardia bidwellii (grape)", "Medium",
       "Purple-brown leaf spots (frog-eye), shrivelled black mummified fruit, cankers on branches or canes.",
       "Warm, wet weather; infected mummies and cankers left in the plant.",
       ["Remove mummified fruit, cankers and infected canes and destroy them.", "Prune for sunlight and airflow."],
       ["Copper or sulfur-based sprays as protectants where permitted."],
       ["Protectant fungicides (for example mancozeb or captan) on a local schedule."],
       ["Good sanitation every winter; avoid overcrowded canopies."]),

    _e("cedar_apple_rust", "Cedar apple rust", ["cedarapplerust"], "Fungus", "Gymnosporangium juniperi-virginianae", "Low",
       "Bright yellow-orange spots on leaves, sometimes with small tube-like growths underneath; can spot fruit.",
       "Wet spring weather near juniper/cedar trees (alternate host).",
       ["Remove nearby junipers/cedars or their galls if practical.", "Pick off affected leaves."],
       ["Sulfur-based protectant sprays."],
       ["Preventive fungicides starting at early growth, as recommended locally."],
       ["Plant resistant apple varieties."]),

    _e("powdery_mildew", "Powdery mildew", ["powderymildew", "mildew"], "Fungus", "Various Erysiphales fungi", "Medium",
       "White powdery coating on leaves and shoots, leaves curl, yellow and dry; reduced yield.",
       "Warm dry days with humid nights; crowded canopies.",
       ["Remove badly infected leaves; thin plants for airflow.", "Avoid excess nitrogen."],
       ["Sulfur, potassium bicarbonate, neem oil or milk spray (diluted) at first signs."],
       ["Sulfur or systemic fungicides (for example triazoles) per label."],
       ["Use resistant varieties; scout early because it spreads fast."]),

    _e("gray_leaf_spot", "Gray leaf spot (Cercospora)", ["cercospora", "grayleafspot"], "Fungus", "Cercospora zeae-maydis", "Medium",
       "Narrow rectangular tan to grey lesions between leaf veins, merging in severe cases.",
       "Warm, humid weather and maize residue left on the field.",
       ["Rotate away from maize and manage crop residue (tillage/removal).", "Avoid very dense planting."],
       [], ["Foliar fungicide (strobilurin/triazole) only for severe, early outbreaks, as locally advised."],
       ["Plant tolerant hybrids."]),

    _e("common_rust", "Common rust", ["commonrust"], "Fungus", "Puccinia sorghi", "Low",
       "Small, round, orange-brown powdery pustules on both leaf surfaces.",
       "Cool, moist weather.",
       ["Scout; usually mild on resistant hybrids.", "Remove severely affected plants in small plots."],
       [], ["Fungicide only if severe on susceptible hybrids and advised locally."],
       ["Plant resistant hybrids."]),

    _e("northern_leaf_blight", "Northern leaf blight", ["northernleafblight"], "Fungus", "Exserohilum turcicum", "Medium",
       "Long, cigar-shaped grey-green to tan lesions on leaves; leaves can die early.",
       "Moderate temperatures with heavy dew or frequent rain.",
       ["Rotate crops and manage residue.", "Avoid late, dense planting."],
       [], ["Foliar fungicide if disease appears before tasselling on susceptible hybrids, as advised locally."],
       ["Plant resistant hybrids."]),

    _e("esca", "Esca (black measles)", ["esca", "blackmeasles"], "Fungal trunk disease", "Complex of wood-decay fungi", "High",
       "Tiger-stripe pattern of yellow/red-brown leaf tissue between veins, dark spots on berries, internal wood decay.",
       "Large pruning wounds, older vines, stressed vines.",
       ["Prune out affected wood in dry weather and destroy it.", "Protect large pruning wounds; remove dead vines."],
       [], [], ["Avoid heavy pruning wounds; use clean planting material."], incurable=True),

    _e("isariopsis", "Grape leaf blight (Isariopsis leaf spot)", ["isariopsis", "grapeleafblight"], "Fungus", "Pseudocercospora vitis", "Medium",
       "Dark brown to black angular spots on leaves, leaf yellowing and early fall.",
       "Warm, humid, wet weather.",
       ["Remove infected leaves; open the canopy.", "Avoid overhead irrigation."],
       ["Copper or sulfur-based protectants."],
       ["Protectant fungicides (for example mancozeb) per local schedule."],
       ["Good canopy management and sanitation."]),

    _e("citrus_greening", "Citrus greening (Huanglongbing)", ["haunglongbing", "huanglongbing", "citrusgreening"], "Bacteria (spread by psyllid)", "Candidatus Liberibacter asiaticus", "High",
       "Blotchy yellow mottling of leaves, small lopsided bitter fruit, twig dieback, tree decline.",
       "Asian citrus psyllid insects; infected nursery plants.",
       ["Remove and destroy infected trees (no cure) after confirmation by authorities.", "Control psyllids with scouting and locally recommended sprays.",
        "Report suspected cases to the agriculture department."],
       [], ["Psyllid insecticides as locally recommended; they protect healthy trees, they do not cure infected ones."],
       ["Plant only certified disease-free nursery stock."], incurable=True),

    _e("leaf_scorch", "Leaf scorch", ["leafscorch"], "Fungus", "Diplocarpon earlianum", "Medium",
       "Many small purple spots that enlarge and give leaves a scorched look; leaves dry up.",
       "Warm, wet weather and dense foliage.",
       ["Remove and destroy old infected leaves; renovate beds after harvest.", "Use drip irrigation."],
       ["Copper-based protectants."],
       ["Protectant fungicides as recommended locally."],
       ["Use resistant varieties and certified plants."]),

    _e("rice_blast", "Rice blast", ["riceblast", "blast"], "Fungus", "Magnaporthe oryzae", "High",
       "Diamond or spindle-shaped spots with grey centres on leaves, neck rot and empty panicles in severe cases.",
       "High humidity, cool nights, excess nitrogen.",
       ["Avoid excess nitrogen; use split fertiliser doses.", "Maintain proper water management and timely sowing."],
       ["Seed treatment with biocontrol agents (for example Trichoderma or Pseudomonas) where available."],
       ["Fungicides such as tricyclazole where locally recommended."],
       ["Use resistant varieties and clean seed."]),

    _e("rice_bacterial_blight", "Bacterial leaf blight (rice)", ["bacterialblight", "bacterialleafblight"], "Bacteria", "Xanthomonas oryzae pv. oryzae", "High",
       "Yellow to white wavy lesions starting at leaf tips and edges, leaves dry and look scorched.",
       "Warm, humid weather, heavy rain, flooded fields, high nitrogen.",
       ["Avoid excess nitrogen; drain the field when infected.", "Clean field bunds and remove weeds."],
       [], ["Copper-based sprays or locally recommended options."],
       ["Use resistant varieties and healthy seed."]),

    _e("rice_brown_spot", "Brown spot (rice)", ["brownspot"], "Fungus", "Bipolaris oryzae", "Medium",
       "Oval brown spots with grey centres on leaves and grains; seedlings can be killed.",
       "Nutrient-poor soils (especially low potassium), drought stress, warm humid weather.",
       ["Apply balanced fertiliser including potassium.", "Avoid water stress."],
       ["Seed treatment with biocontrol agents or hot-water seed treatment."],
       ["Fungicides such as mancozeb where locally recommended."],
       ["Use healthy seed and resistant varieties."]),

    _e("rice_leaf_smut", "Leaf smut (rice)", ["leafsmut"], "Fungus", "Entyloma oryzae", "Low",
       "Small raised black angular spots on leaves; usually a minor disease.",
       "High nitrogen and humid weather.",
       ["Balanced fertiliser and clean fields.", "Remove crop stubble."],
       [], ["Rarely needs fungicide; ask local advice if severe."],
       ["Use clean seed."]),

    _e("wheat_rust", "Wheat rust (yellow / brown / black)", ["wheatrust", "yellowrust", "brownrust", "blackrust", "stemrust"], "Fungus", "Puccinia species", "High",
       "Orange, yellow or black powdery pustules on leaves and stems; can spread over large areas quickly.",
       "Cool, moist weather (yellow rust), warm moist weather (brown/black rust).",
       ["Scout early and report outbreaks to the local extension service.", "Destroy volunteer wheat and alternate hosts where known."],
       [], ["Triazole or strobilurin fungicides sprayed promptly as locally recommended."],
       ["Plant rust-resistant varieties and sow on time."]),
]

# --- generic fallbacks (used when the exact disease is not in the list above) ---
GENERIC = [
    _e("g_blight", "Blight (general)", ["blight"], "Fungus or bacteria", "Varies", "Medium",
       "Large irregular brown/black patches that spread quickly and kill leaf tissue.", "Warm or cool wet weather depending on the pathogen.",
       ["Remove and destroy infected leaves.", "Avoid overhead watering and improve airflow."],
       ["Copper-based protectants where permitted."], ["Protectant fungicide recommended locally for your crop."],
       ["Use resistant varieties, certified seed and crop rotation."]),
    _e("g_rust", "Rust (general)", ["rust"], "Fungus", "Rust fungi", "Medium",
       "Orange, yellow or brown powdery pustules on leaves.", "Moist weather and dense canopies.",
       ["Remove infected leaves; avoid wetting foliage."], ["Sulfur-based protectants."],
       ["Fungicide recommended locally for the crop."], ["Plant resistant varieties."]),
    _e("g_spot", "Leaf spot (general)", ["spot"], "Fungus or bacteria", "Varies", "Medium",
       "Round or angular spots on leaves, sometimes with a yellow halo.", "Wet leaves and humid weather.",
       ["Remove spotted leaves; water at the base.", "Clear plant debris."], ["Copper-based protectants."],
       ["Locally recommended protectant fungicide or bactericide."], ["Rotate crops and use clean seed."]),
    _e("g_mold", "Mold / mildew (general)", ["mold", "mould"], "Fungus", "Varies", "Medium",
       "Fuzzy or powdery growth on leaves.", "High humidity and poor ventilation.",
       ["Increase airflow; reduce humidity; remove infected leaves."], ["Sulfur or biofungicide sprays."],
       ["Locally recommended fungicide."], ["Space plants and avoid overhead watering."]),
    _e("g_virus", "Virus disease (general)", ["virus"], "Virus", "Varies", "High",
       "Mottled, curled or stunted leaves; no cure.", "Insect vectors (aphids, whiteflies), tools and infected seed.",
       ["Remove and destroy infected plants.", "Control insect vectors and disinfect tools."], [], [],
       ["Use certified virus-free seed and resistant varieties."], incurable=True),
    _e("g_pest", "Pest damage (general)", ["mite", "aphid", "whitefly", "thrips", "pest"], "Pest", "Varies", "Medium",
       "Stippling, curling, webbing or chewed leaves.", "Hot dry weather and lack of natural enemies.",
       ["Wash off pests with water; remove heavily infested leaves."], ["Neem oil or insecticidal soap."],
       ["Locally recommended insecticide/miticide only if needed."], ["Scout weekly; protect natural enemies."]),
    _e("g_rot", "Rot (general)", ["rot"], "Fungus or bacteria", "Varies", "Medium",
       "Soft, dark, decaying tissue.", "Waterlogging, wounds and warm wet weather.",
       ["Remove rotting tissue; improve drainage."], ["Biofungicides where available."],
       ["Locally recommended fungicide."], ["Avoid wounding plants; rotate crops."]),
    _e("g_wilt", "Wilt (general)", ["wilt"], "Fungus or bacteria", "Varies", "High",
       "Leaves wilt and yellow, vascular browning inside stems.", "Soil-borne pathogens, warm soil.",
       ["Remove and destroy wilted plants; do not move soil."], [], [],
       ["Rotate crops, solarise soil, use resistant rootstocks/varieties."], incurable=True),
]

DEFAULT = _e("unknown", "Condition not in the knowledge base", [], "Unknown", "Unknown", "Medium",
             "This condition has no detailed entry yet.", "-",
             ["Isolate the affected plant, remove badly affected leaves and keep foliage dry.",
              "Take clear photos and show them to a local agriculture / extension officer."],
             [], [], ["Practise crop rotation, clean seed and field sanitation."])


def squash(text: str) -> str:
    return re.sub(r"[^a-z]", "", (text or "").lower())


def find_entry(crop: str, disease: str) -> dict:
    """Return the best knowledge-base entry for a model label (e.g. 'Tomato', 'Late blight')."""
    d = squash(disease)
    full = squash(f"{crop} {disease}")
    if d == "healthy" or d.endswith("healthy"):
        return ENTRIES[0]
    for entry in ENTRIES[1:]:
        if any(k in full for k in entry["keywords"]):
            return entry
    for entry in GENERIC:
        if any(k in full for k in entry["keywords"]):
            return entry
    return DEFAULT


def all_entries():
    return ENTRIES + GENERIC


def action_plan(entry: dict, severity_percent: float, grade: str) -> dict:
    """Turn the entry + measured severity into a prioritised, time-bound plan."""
    if entry["id"] == "healthy":
        return dict(headline="No action needed", timeframe="Re-scan in about 7 days",
                    steps=["Keep scouting weekly.", "Keep leaves dry, plants spaced and fertiliser balanced."])
    steps = []
    p = severity_percent
    if p < 2:
        headline, timeframe = "Monitor closely", "Re-scan in 3-5 days"
        steps.append("Damage on this leaf is negligible; check other leaves and neighbouring plants.")
    elif p < 10:
        headline, timeframe = "Act early (mild severity)", "Start within 2-3 days, re-scan in 5 days"
        steps.append("Remove the affected leaves and bag them (do not compost).")
    elif p < 30:
        headline, timeframe = "Treat now (moderate severity)", "Start this week, re-scan every 3-5 days"
        steps.append("Remove affected leaves and start the control measures below; protect nearby healthy plants.")
    else:
        headline, timeframe = "Urgent (severe)", "Act within 24 hours"
        steps.append("Isolate or remove heavily affected plants and check the whole plot today.")
        steps.append("Contact a local agriculture officer before spraying anything.")
    if entry.get("incurable"):
        steps.append("This disease has no cure: remove infected plants early and protect healthy ones (control vectors, clean tools).")
    elif entry["urgency"] == "High" and p >= 2:
        steps.append("This disease can spread very fast; treat the whole plot, not just the visible leaf.")
    if entry["cultural"]:
        steps.append(entry["cultural"][0])
    steps.append("Confirm the diagnosis with a local expert before using any chemical.")
    return dict(headline=headline, timeframe=timeframe, steps=steps)
