import streamlit as st
import requests
import random
from typing import List, Dict, Any, Optional, Tuple

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Museum Curator — Dog Breed Gallery",
    page_icon="🐶",
    layout="wide",
)

# ----------------------------
# Safe Requests
# ----------------------------
def safe_get_json(url: str, params: Optional[dict] = None, timeout: int = 10):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ----------------------------
# Origin -> Department (Region Gallery)
# ----------------------------
def origin_to_region(origin: str) -> str:
    o = (origin or "").lower()

    asia = [
        "japan", "china", "korea", "tibet", "thailand", "vietnam", "india",
        "mongolia", "siberia", "russia", "nepal", "iran", "israel", "turkmenistan",
        "kazakhstan", "uzbekistan", "afghanistan", "pakistan", "myanmar", "laos"
    ]
    europe = [
        "england", "scotland", "ireland", "wales", "france", "germany", "italy", "spain",
        "portugal", "sweden", "norway", "finland", "denmark", "netherlands", "belgium",
        "switzerland", "austria", "poland", "hungary", "czech", "slovakia", "croatia",
        "serbia", "greece", "romania", "bulgaria", "ukraine", "russia", "turkey"
    ]
    americas = [
        "united states", "usa", "america", "canada", "mexico",
        "brazil", "argentina", "chile", "peru", "colombia", "venezuela", "uruguay"
    ]
    africa = [
        "africa", "egypt", "morocco", "mali", "kenya", "ethiopia", "tunisia",
        "algeria", "nigeria", "south africa"
    ]
    oceania = ["australia", "new zealand", "tasmania"]

    if any(k in o for k in asia):
        return "Asia Gallery"
    if any(k in o for k in europe):
        return "Europe Gallery"
    if any(k in o for k in americas):
        return "Americas Gallery"
    if any(k in o for k in africa):
        return "Africa Gallery"
    if any(k in o for k in oceania):
        return "Oceania Gallery"
    return "Unknown / Global"


# ----------------------------
# Fetch Breeds (TheDogAPI)
# ----------------------------
@st.cache_data(show_spinner=False)
def fetch_breeds() -> List[Dict[str, Any]]:
    url = "https://api.thedogapi.com/v1/breeds"
    data = safe_get_json(url)
    if isinstance(data, list) and len(data) > 0:
        return data

    # Fallback Sample
    return [
        {
            "id": 0,
            "name": "Golden Retriever",
            "bred_for": "Retrieving",
            "breed_group": "Sporting",
            "origin": "Scotland",
            "temperament": "Intelligent, Friendly, Reliable",
            "life_span": "10 - 12 years",
            "weight": {"metric": "25 - 34"},
            "height": {"metric": "51 - 61"},
        }
    ]


@st.cache_data(show_spinner=False)
def fetch_breed_images_from_thedogapi(breed_id: int, limit: int = 12) -> List[str]:
    url = "https://api.thedogapi.com/v1/images/search"
    params = {"breed_id": breed_id, "limit": limit}
    data = safe_get_json(url, params=params)
    if isinstance(data, list):
        return [d.get("url") for d in data if d.get("url")]
    return []


@st.cache_data(show_spinner=False)
def fetch_random_images(limit: int = 12) -> List[str]:
    url = f"https://dog.ceo/api/breeds/image/random/{limit}"
    data = safe_get_json(url)
    if isinstance(data, dict) and data.get("status") == "success":
        imgs = data.get("message")
        if isinstance(imgs, list):
            return imgs
    return []


def normalize_text(x: Any, default: str = "Unknown") -> str:
    if x is None:
        return default
    if isinstance(x, str) and x.strip():
        return x.strip()
    return default


def metric_range(x: Any, default: str = "Unknown") -> str:
    if isinstance(x, dict):
        m = x.get("metric")
        if isinstance(m, str) and m.strip():
            return m
    return default


def get_avg_kg(weight_metric: str) -> Optional[float]:
    try:
        parts = weight_metric.replace("–", "-").split("-")
        nums = [float(p.strip()) for p in parts if p.strip()]
        if not nums:
            return None
        return sum(nums) / len(nums)
    except Exception:
        return None


def size_category(weight_metric: str) -> str:
    avg = get_avg_kg(weight_metric)
    if avg is None:
        return "Unknown"
    if avg < 10:
        return "Small"
    if avg < 25:
        return "Medium"
    if avg < 40:
        return "Large"
    return "Giant"


# ----------------------------
# Curator Narrative (No AI key)
# ----------------------------
def curator_narrative(b: Dict[str, Any]) -> str:
    name = normalize_text(b.get("name"))
    origin = normalize_text(b.get("origin"))
    region = normalize_text(b.get("region"), "Unknown / Global")
    group = normalize_text(b.get("breed_group"), "Other/Unknown")
    bred_for = normalize_text(b.get("bred_for"))
    temperament = normalize_text(b.get("temperament"), default="Varied")
    life_span = normalize_text(b.get("life_span"))
    weight = metric_range(b.get("weight"))
    height = metric_range(b.get("height"))
    size = size_category(weight)

    text = f"""
**{name}** is presented here as a living cultural artifact—  
a breed whose form, instincts, and companionship style were refined through history.

### 🧭 Department / Geographic Lineage
- **Origin:** {origin}  
- **Museum Department:** **{region}**

### 🏛️ Historical & Functional Context
Traditionally bred for **{bred_for.lower()}**, {name} belongs to the **{group}** group.

### 🎭 Temperament & Personality
**{temperament}**

### 🧬 Physical Form & Visual Impressions
- **Size:** {size}  
- **Height:** {height} cm  
- **Weight:** {weight} kg  

### 🩺 Care & Lifestyle Notes
Average life span: **{life_span}**  
Keep a stable routine, do breed-appropriate exercise, and enrich mentally.

### 💡 Curator’s Highlight
{ name } is a bridge between **human needs** and **canine evolution**.
"""
    return text.strip()


# ----------------------------
# New Wing 1: Body Parts Explorer (knowledge cards)
# ----------------------------
BODY_PARTS = {
    "Eyes": {
        "normal": [
            "Clear, bright eyes", "No thick discharge", "Not squinting"
        ],
        "watch_for": [
            "Yellow/green discharge", "Redness or swelling",
            "Cloudy/blue haze", "Constant squinting"
        ],
        "meaning": "Eyes reflect allergy, infection, injury, aging changes."
    },
    "Ears": {
        "normal": [
            "Light pink, no strong smell", "Minimal wax", "Dog not scratching a lot"
        ],
        "watch_for": [
            "Bad odor", "Brown/black debris", "Head shaking",
            "Pain when touched"
        ],
        "meaning": "Ear issues are common; could relate to infection or allergy."
    },
    "Mouth / Teeth": {
        "normal": [
            "Pink gums", "Clean teeth", "No constant drooling"
        ],
        "watch_for": [
            "Red gums/bleeding", "Bad breath", "Broken tooth",
            "Refuses food"
        ],
        "meaning": "Dental disease is frequent; check gums and tartar."
    },
    "Skin / Coat": {
        "normal": [
            "Shiny coat", "No bald patches", "No strong itch"
        ],
        "watch_for": [
            "Hot spots", "Dandruff", "Bumps/lumps",
            "Intense scratching"
        ],
        "meaning": "Skin shows allergy, parasites, infection, hormonal issues."
    },
    "Paws / Nails": {
        "normal": [
            "Pads not cracked", "Nails not overgrown", "No limping"
        ],
        "watch_for": [
            "Limping", "Bleeding nail", "Constant licking",
            "Swollen toes"
        ],
        "meaning": "Paws indicate injury, arthritis, foreign objects."
    },
    "Stomach / Digestion": {
        "normal": [
            "Firm but not bloated", "Regular poop", "Normal appetite"
        ],
        "watch_for": [
            "Hard bloated belly", "Repeated vomiting",
            "Black/bloody stool", "No poop > 24h"
        ],
        "meaning": "GI signs range from mild upset to emergencies."
    },
}


# ----------------------------
# New Wing 2: Simple Symptom Checker (triage, NOT diagnosis)
# ----------------------------
def triage(symptoms: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    """
    Return urgency_level, curator_note, possible_systems
    This is NOT diagnosis. Only general triage education.
    """
    emergency_flags = []
    soon_flags = []

    if symptoms["breathing_trouble"]:
        emergency_flags.append("Breathing trouble")
    if symptoms["collapse_seizure"]:
        emergency_flags.append("Collapse / seizures")
    if symptoms["bloated_hard_belly"]:
        emergency_flags.append("Bloated hard belly")
    if symptoms["uncontrolled_bleeding"]:
        emergency_flags.append("Uncontrolled bleeding")
    if symptoms["cannot_urinate"]:
        emergency_flags.append("Cannot urinate")
    if symptoms["heatstroke_like"]:
        emergency_flags.append("Heatstroke signs")

    # Vet soon indications
    if symptoms["vomit_diarrhea_hours"] >= 24:
        soon_flags.append("Vomiting/diarrhea > 24h")
    if symptoms["blood_in_stool_vomit"]:
        soon_flags.append("Blood seen in vomit or stool")
    if symptoms["appetite_loss_hours"] >= 24:
        soon_flags.append("No appetite > 24h")
    if symptoms["limping_hours"] >= 24:
        soon_flags.append("Limping > 24h")
    if symptoms["eye_ear_pain"]:
        soon_flags.append("Eye/Ear pain or discharge")

    possible_systems = []
    if symptoms["vomit_diarrhea_hours"] > 0:
        possible_systems.append("Digestive / GI")
    if symptoms["itch_skin"]:
        possible_systems.append("Skin / Allergy / Parasite")
    if symptoms["cough_sneeze"]:
        possible_systems.append("Respiratory")
    if symptoms["limping_hours"] > 0:
        possible_systems.append("Musculoskeletal / Joint")
    if symptoms["eye_ear_pain"]:
        possible_systems.append("Eyes/Ears")

    if emergency_flags:
        level = "🚨 Emergency — Go to vet/ER now"
        note = (
            "Your inputs include emergency signs. "
            "Online tools cannot diagnose or treat. Please seek urgent veterinary care."
        )
    elif soon_flags:
        level = "🟠 Vet Soon (within 24–48h)"
        note = (
            "These signs can indicate illness that needs professional evaluation. "
            "Contact a vet clinic soon."
        )
    else:
        level = "🟢 Monitor & Support"
        note = (
            "No clear emergency signals detected. "
            "Monitor closely, keep notes, and see a vet if symptoms worsen or persist."
        )

    curator_note = (
        note
        + "\n\n**Curator safety note:** This is general education, not a diagnosis or prescription."
    )
    return level, curator_note, possible_systems


# ----------------------------
# New Wing 3: Medication Library (educational, no dosing)
# ----------------------------
MED_LIBRARY = [
    {
        "title": "Parasite Prevention (Flea/Tick)",
        "examples": ["Afoxolaner", "Fluralaner", "Sarolaner"],
        "used_for": "Prevent fleas/ticks and related skin disease.",
        "watch_for": "Vomiting, lethargy, rare neuro side effects.",
        "note": "Use only vet-recommended products; never mix randomly."
    },
    {
        "title": "Dewormers",
        "examples": ["Pyrantel", "Fenbendazole", "Milbemycin oxime"],
        "used_for": "Intestinal parasites (roundworm, hookworm, etc.).",
        "watch_for": "Mild GI upset occasionally.",
        "note": "Parasite type needs vet confirmation."
    },
    {
        "title": "Antibiotics (Prescription)",
        "examples": ["Amoxicillin-clavulanate", "Cephalexin", "Doxycycline"],
        "used_for": "Bacterial infections (skin, ear, urinary, etc.).",
        "watch_for": "Diarrhea, appetite loss, allergy reactions.",
        "note": "Wrong antibiotic causes resistance—vet only."
    },
    {
        "title": "Pain / Anti-Inflammatory (NSAIDs)",
        "examples": ["Carprofen", "Meloxicam", "Firocoxib"],
        "used_for": "Pain, arthritis, inflammation.",
        "watch_for": "Vomiting, black stool, appetite loss.",
        "note": "Human painkillers can be toxic; never self-dose."
    },
    {
        "title": "Vaccines",
        "examples": ["Rabies", "DHPP", "Leptospirosis"],
        "used_for": "Prevent common infectious diseases.",
        "watch_for": "Mild fever or soreness after injection.",
        "note": "Schedule depends on age and region."
    },
]


# ----------------------------
# UI Start
# ----------------------------
st.title("🎨 AI Museum Curator")
st.caption(
    "A curator-style global dog breed gallery + health/medication wings. "
    "No OpenAI key required."
)

breeds = fetch_breeds()
for b in breeds:
    b["region"] = origin_to_region(b.get("origin", ""))
    b["size"] = size_category(metric_range(b.get("weight")))

# ----------------------------
# Sidebar: Choose Museum Wing
# ----------------------------
st.sidebar.header("Museum Wings")
mode = st.sidebar.radio(
    "Select a wing",
    ["Breed Gallery", "Body Parts Explorer", "Symptom Checker", "Medication Library"]
)

# ----------------------------
# WING A: Breed Gallery (original)
# ----------------------------
if mode == "Breed Gallery":
    st.sidebar.header("Settings")
    keyword = st.sidebar.text_input("Search breed", "")

    regions = sorted(list({b.get("region", "Unknown / Global") for b in breeds}))
    selected_region = st.sidebar.selectbox("Department (Region Gallery)", ["All"] + regions)

    breed_groups = sorted(list({normalize_text(b.get("breed_group"), "Other/Unknown") for b in breeds}))
    selected_group = st.sidebar.selectbox("Breed Group", ["All"] + breed_groups)

    sizes = sorted(list({b.get("size", "Unknown") for b in breeds}))
    selected_size = st.sidebar.selectbox("Size Category", ["All"] + sizes)

    filtered = []
    for b in breeds:
        n = normalize_text(b.get("name"))
        r = b.get("region", "Unknown / Global")
        g = normalize_text(b.get("breed_group"), "Other/Unknown")
        s = b.get("size", "Unknown")

        if keyword and keyword.lower() not in n.lower():
            continue
        if selected_region != "All" and r != selected_region:
            continue
        if selected_group != "All" and g != selected_group:
            continue
        if selected_size != "All" and s != selected_size:
            continue

        filtered.append(b)

    if not filtered:
        st.warning("No breeds found with current filters. Showing all breeds instead.")
        filtered = breeds

    st.sidebar.divider()
    if st.sidebar.button("🎲 Curator Pick (Random Breed)"):
        st.session_state["picked_name"] = normalize_text(random.choice(filtered).get("name"))

    picked_name = st.session_state.get("picked_name")
    names_list = [normalize_text(b.get("name")) for b in filtered]
    default_index = names_list.index(picked_name) if picked_name in names_list else 0

    selected_name = st.sidebar.selectbox("Choose a breed", names_list, index=default_index)
    current = next((b for b in filtered if normalize_text(b.get("name")) == selected_name), filtered[0])

    breed_id = current.get("id", 0)
    images = fetch_breed_images_from_thedogapi(breed_id, limit=12)
    if not images:
        images = fetch_random_images(limit=12)

    left, right = st.columns([1.1, 1.6], gap="large")

    with left:
        if images:
            st.image(images[0], use_container_width=True, caption=normalize_text(current.get("name")))
        else:
            st.info("No image available right now.")

        st.subheader("🖼️ Breed Gallery")
        if len(images) > 1:
            cols = st.columns(3)
            for i, url in enumerate(images[1:12]):
                with cols[i % 3]:
                    st.image(url, use_container_width=True)

    with right:
        st.subheader(f"🐕 {normalize_text(current.get('name'))}")

        st.markdown("### 📌 Basic Information")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Origin", normalize_text(current.get("origin")))
        c2.metric("Department", current.get("region", "Unknown / Global"))
        c3.metric("Breed Group", normalize_text(current.get("breed_group"), "Other/Unknown"))
        c4.metric("Life Span", normalize_text(current.get("life_span")))

        st.markdown("### 📏 Appearance")
        a1, a2, a3 = st.columns(3)
        a1.write(f"**Height (cm):** {metric_range(current.get('height'))}")
        a2.write(f"**Weight (kg):** {metric_range(current.get('weight'))}")
        a3.write(f"**Size Category:** {current.get('size', 'Unknown')}")

        st.markdown("### 🎭 Temperament & Behavior")
        st.write(normalize_text(current.get("temperament"), default="No temperament data."))

        st.markdown("### 🧭 Original Role / Bred For")
        st.write(normalize_text(current.get("bred_for"), default="No historical role data."))

        st.markdown("### 🧑‍🎨 Curator’s Interpretation (AI-style)")
        st.markdown(curator_narrative(current))

# ----------------------------
# WING B: Body Parts Explorer
# ----------------------------
elif mode == "Body Parts Explorer":
    st.subheader("🔍 Body Parts Explorer — Curator Anatomy Notes")
    st.caption("Learn how to observe dogs by body part. This is education, not diagnosis.")

    part = st.selectbox("Choose a body part", list(BODY_PARTS.keys()))
    info = BODY_PARTS[part]

    st.markdown(f"## {part}")
    st.markdown("### ✅ What looks normal")
    for x in info["normal"]:
        st.write(f"- {x}")

    st.markdown("### ⚠️ What to watch for")
    for x in info["watch_for"]:
        st.write(f"- {x}")

    st.markdown("### 🧑‍🎨 Curator Note")
    st.write(info["meaning"])

    st.info(
        "If you notice severe pain, rapid worsening, or multiple abnormal signs, "
        "please consult a veterinarian. Home checks help you notice changes early. "
    )

# ----------------------------
# WING C: Symptom Checker (triage only)
# ----------------------------
elif mode == "Symptom Checker":
    st.subheader("🩺 Symptom Checker — Curator Triage (Not a Diagnosis)")
    st.warning(
        "This tool provides general triage education only. "
        "Online systems cannot diagnose diseases or prescribe medications. "
        "Seek a vet for any serious concern."
    )

    with st.form("symptom_form"):
        age = st.number_input("Dog age (years)", 0.0, 30.0, 3.0, 0.5)
        size = st.selectbox("Dog size", ["Small", "Medium", "Large", "Giant", "Unknown"])

        st.markdown("### Main observations")
        vomit_diarrhea_hours = st.slider("Vomiting/diarrhea duration (hours)", 0, 72, 0)
        appetite_loss_hours = st.slider("Not eating duration (hours)", 0, 72, 0)
        limping_hours = st.slider("Limping duration (hours)", 0, 168, 0)

        itch_skin = st.checkbox("Strong itching / skin rash")
        cough_sneeze = st.checkbox("Coughing / sneezing a lot")
        eye_ear_pain = st.checkbox("Eye/ear pain or discharge")

        st.markdown("### Emergency signs (tick if yes)")
        breathing_trouble = st.checkbox("Trouble breathing")
        collapse_seizure = st.checkbox("Collapse / seizure")
        bloated_hard_belly = st.checkbox("Bloated, hard belly")
        uncontrolled_bleeding = st.checkbox("Uncontrolled bleeding")
        cannot_urinate = st.checkbox("Cannot urinate")
        heatstroke_like = st.checkbox("Heatstroke-like signs (very hot, panting nonstop)")

        submitted = st.form_submit_button("Analyze")

    if submitted:
        sym = dict(
            age=age,
            size=size,
            vomit_diarrhea_hours=vomit_diarrhea_hours,
            appetite_loss_hours=appetite_loss_hours,
            limping_hours=limping_hours,
            itch_skin=itch_skin,
            cough_sneeze=cough_sneeze,
            eye_ear_pain=eye_ear_pain,
            breathing_trouble=breathing_trouble,
            collapse_seizure=collapse_seizure,
            bloated_hard_belly=bloated_hard_belly,
            uncontrolled_bleeding=uncontrolled_bleeding,
            cannot_urinate=cannot_urinate,
            heatstroke_like=heatstroke_like,
            blood_in_stool_vomit=False,  # reserved for expansion
        )

        level, note, systems = triage(sym)

        st.markdown(f"## {level}")
        st.markdown(note)

        if systems:
            st.markdown("### 🧠 Possible related body systems (broad, not diagnosis)")
            for s in systems:
                st.write(f"- {s}")

        st.markdown("### 📌 What you can record for the vet")
        st.write(
            "- When symptoms started\n"
            "- Frequency (how many times per day)\n"
            "- Photos/videos of the issue\n"
            "- Food, treats, new environments\n"
            "- Any medications already given (if any)"
        )

# ----------------------------
# WING D: Medication Library
# ----------------------------
else:
    st.subheader("💊 Medication Library — Curator Drug Notes (Education Only)")
    st.warning(
        "Never give human medication or change doses yourself. "
        "Many human drugs are toxic to dogs; dosing must come from a veterinarian."
    )

    for med in MED_LIBRARY:
        with st.expander(f"📁 {med['title']}"):
            st.markdown("**Examples (not recommendations):** " + ", ".join(med["examples"]))
            st.markdown("**Used for:** " + med["used_for"])
            st.markdown("**Watch for:** " + med["watch_for"])
            st.markdown("**Curator safety note:** " + med["note"])

    st.info(
        "If your dog is sick, a vet must decide the right medication and dose. "
        "This wing is for learning and understanding only."
    )

# Footer
st.divider()
st.caption(
    "Data Source: TheDogAPI / Dog CEO API. "
    "Health-related wings are general education & triage only."
)
