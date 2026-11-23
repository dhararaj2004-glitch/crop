"""Who to contact and where to find the nearest help.

The app does not need GPS or paid APIs: it builds Google Maps search links from the district/state
the user types, plus official national resources (India) that were checked at build time.
"""
from urllib.parse import quote_plus

INDIA_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


def maps_url(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)


def _place(state: str, district: str) -> str:
    parts = [p for p in (district.strip(), state.strip()) if p and not p.startswith("--")]
    return ", ".join(parts)


def get_help(country: str, state: str = "", district: str = "", crop: str = "") -> dict:
    place = _place(state, district)
    near = f" near {place}" if place else ""
    contacts, searches = [], []

    if country == "India":
        contacts += [
            dict(name="Kisan Call Centre (free expert advice)", phone="1800-180-1551",
                 detail="Toll-free from any phone; agricultural experts answer in local languages (usually 6 AM to 10 PM).",
                 url="https://mkisan.gov.in"),
            dict(name="Krishi Vigyan Kendra (KVK) - district farm science centre",
                 detail="About 730 KVKs, roughly one per district, run by ICAR with agricultural universities. Best first stop for disease diagnosis and training.",
                 url="https://kvk.icar.gov.in"),
            dict(name="KVK Khoj and Kisan Suvidha apps",
                 detail="Government mobile apps that can show the nearest KVK and let you contact it."),
            dict(name="District / block agriculture officer (Krishi Bhawan)",
                 detail="Your state agriculture department office; ask for the plant protection officer for disease and spray advice and for crop-insurance help."),
            dict(name="State agricultural university / research station",
                 detail="Often has plant clinics and diagnostic labs; useful for confirming unusual diseases."),
        ]
        searches += [
            ("Krishi Vigyan Kendra (KVK)", f"Krishi Vigyan Kendra{near}"),
            ("District agriculture office", f"District agriculture office Krishi Bhawan{near}"),
            ("Agricultural university / research station", f"Agricultural university{near}"),
            ("Agri-input shop (seeds, fertiliser, pesticides)", f"Agri input shop pesticide dealer{near}"),
        ]
    else:
        contacts += [
            dict(name="National / regional agricultural extension service",
                 detail="Ask the local agriculture ministry office for the plant protection or extension officer."),
            dict(name="Agricultural university or research institute",
                 detail="Many run plant clinics or diagnostic labs."),
        ]
        searches += [
            ("Agricultural extension office", f"Agricultural extension office{near}"),
            ("Agricultural university", f"Agricultural university{near}"),
            ("Agri-input shop", f"Agricultural supply store pesticide{near}"),
        ]
    if crop:
        searches.append((f"{crop} specialists", f"{crop} farming advisory expert{near}"))
    return dict(place=place, contacts=contacts,
                searches=[(label, maps_url(q)) for label, q in searches])
