import streamlit as st
import requests
import random
from typing import List, Dict, Any, Optional

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

    # Asia
    asia = [
        "japan", "china", "korea", "tibet", "thailand", "vietnam", "india",
        "mongolia", "siberia", "russia", "nepal", "iran", "israel", "turkmenistan",
        "kazakhstan", "uzbekistan", "afghanistan", "pakistan", "myanmar", "laos"
    ]

    # Europe
    europe = [
        "england", "scotland", "ireland", "wales", "france", "germany", "italy", "spain",
        "portugal", "sweden", "norway", "finland", "denmark", "netherlands", "belgium",
        "switzerland", "austria", "poland", "hungary", "czech", "slovakia", "croatia",
        "serbia", "greece", "romania", "bulgaria", "ukraine", "russia", "turkey"
    ]

    # Americas
    americas = [
        "united states", "usa", "america", "canada", "mexico",
        "brazil", "argentina", "chile", "peru", "colombia", "venezuela", "uruguay"
    ]

    # Africa
    africa = [
        "africa", "egypt", "morocco", "mali", "kenya", "ethiopia", "tunisia",
        "algeria", "nigeria", "south africa"
    ]

    # Oceania
    oceania = [
        "australia", "new zealand", "tasmania"
    ]

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
#   If fails -> sample fallback
# ----------------------------
@st.cache_data(show_spinner=False)
def fetch_breeds() -> List[Dict[str, Any]]:
    url = "https://api.thedogapi.com/v1/breeds"
    data = safe_get_json(url)
    if isinstance(data, list) and len(data) > 0:
        return data

    # Fallback Sample Data
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
            "reference_image_id": None,
        },
        {
            "id": 1,
            "name": "Siberian Husky",
            "bred_for": "Sled pulling",
            "breed_group": "Working",
            "origin": "Russia",
            "temperament": "Alert, Energetic, Outgoing",
            "life_span": "12 - 15 years",
            "weight": {"metric": "16 - 27"},
            "height": {"metric": "50 - 60"},
            "reference_image_id": None,
        },
        {
            "id": 2,
            "name": "Shiba Inu",
            "bred_for": "Hunting",
            "breed_group": "Non-Sporting",
            "origin": "Japan",
            "temperament": "Bold, Independent, Good-natured",
            "life_span": "12 - 16 years",
            "weight": {"metric": "8 - 11"},
            "height": {"metric": "33 - 43"},
            "reference_image_id": None,
        },
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
This regional lineage often shapes coat type, stamina, and temperament.

### 🏛️ Historical & Functional Context
Traditionally bred for **{bred_for.lower()}**, {name} belongs to the **{group}** group.  
Its modern behavior still reflects the practical roles it once served.

### 🎭 Temperament & Personality
Common descriptors include: **{temperament}**  
This usually results in:
- stable bonding with humans  
- predictable breed-typical instincts  
- characteristic social/energy patterns  

### 🧬 Physical Form & Visual Impressions
- **Size Category:** {size}  
- **Height:** {height} cm  
- **Weight:** {weight} kg  

The silhouette and movement of {name} often reveal its original working purpose.

### 🩺 Health, Care & Exhibition Notes
Average life span: **{life_span}**  
Recommended lifestyle:
- daily exercise aligned to energy level  
- early socialization to reduce anxiety  
- mental enrichment (training, puzzles, sniffing games)

### 💡 Curator’s Highlight
{ name } is best understood as a bridge between **human needs** and **canine evolution**—  
a breed shaped by function, but treasured for companionship.
"""
    return text.strip()


# ----------------------------
# UI Start
# ----------------------------
st.title("🎨 AI Museum Curator")
st.caption(
    "A curator-style global dog breed gallery. "
    "Real breed data from public APIs, with rich narratives and image exhibitions."
)

breeds = fetch_breeds()

# attach region + size
for b in breeds:
    b["region"] = origin_to_region(b.get("origin", ""))
    b["size"] = size_category(metric_range(b.get("weight")))

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Settings")

keyword = st.sidebar.text_input("Search breed", "")

regions = sorted(list({b.get("region", "Unknown / Global") for b in breeds}))
selected_region = st.sidebar.selectbox("Department (Region Gallery)", ["All"] + regions)

breed_groups = sorted(list({normalize_text(b.get("breed_group"), "Other/Unknown") for b in breeds}))
selected_group = st.sidebar.selectbox("Breed Group", ["All"] + breed_groups)

sizes = sorted(list({b.get("size", "Unknown") for b in breeds}))
selected_size = st.sidebar.selectbox("Size Category", ["All"] + sizes)

# Filter
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

# Featured / Curator Pick
st.sidebar.divider()
if st.sidebar.button("🎲 Curator Pick (Random Breed)"):
    st.session_state["picked_name"] = normalize_text(random.choice(filtered).get("name"))

picked_name = st.session_state.get("picked_name")

names_list = [normalize_text(b.get("name")) for b in filtered]
default_index = names_list.index(picked_name) if picked_name in names_list else 0

selected_name = st.sidebar.selectbox(
    "Choose a breed",
    names_list,
    index=default_index,
)

current = next((b for b in filtered if normalize_text(b.get("name")) == selected_name), filtered[0])

# ----------------------------
# Fetch images
# ----------------------------
breed_id = current.get("id", 0)
images = fetch_breed_images_from_thedogapi(breed_id, limit=12)

if not images:
    images = fetch_random_images(limit=12)

# ----------------------------
# Main Layout
# ----------------------------
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
    else:
        st.write("Gallery will appear here.")

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

    st.markdown("### 🧑‍🎨 Curator’s Interpretation (AI-style, no key required)")
    st.markdown(curator_narrative(current))

    st.markdown("### 🧠 Smart Subtopics")
    sub1, sub2 = st.columns(2)

    with sub1:
        st.markdown("**Training Tips**")
        st.write(
            "Use short, reward-based sessions. "
            "Adjust difficulty to its working history and energy level."
        )
        st.markdown("**Ideal Home**")
        st.write(
            "Match exercise needs to your environment. "
            "Working breeds enjoy structured routines and tasks."
        )

    with sub2:
        st.markdown("**Grooming Notes**")
        st.write(
            "Coat type affects shedding and brushing frequency. "
            "Double coats shed seasonally."
        )
        st.markdown("**Social Needs**")
        st.write(
            "Early exposure to people, dogs, and places helps "
            "build stable adult temperament."
        )

st.divider()
st.caption(
    "Data Source: TheDogAPI / Dog CEO API. "
    "This project uses a built-in curator narrative generator, so no OpenAI key is required."
)
