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
# Helpers (Safe Requests)
# ----------------------------
def safe_get_json(url: str, params: Optional[dict] = None, timeout: int = 10):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ----------------------------
# Data Fetching
#   Priority 1: TheDogAPI (no key required for basic usage)
#   Fallback: local sample + Dog CEO random images
# ----------------------------
@st.cache_data(show_spinner=False)
def fetch_breeds() -> List[Dict[str, Any]]:
    """
    Fetch breed metadata from TheDogAPI.
    If it fails, return sample data.
    """
    url = "https://api.thedogapi.com/v1/breeds"
    data = safe_get_json(url)
    if isinstance(data, list) and len(data) > 0:
        return data
    
    # ---- Fallback Sample Data (offline-safe) ----
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
def fetch_breed_images_from_thedogapi(breed_id: int, limit: int = 8) -> List[str]:
    """
    Get multiple images for a breed from TheDogAPI.
    If request fails or empty, return empty list.
    """
    url = "https://api.thedogapi.com/v1/images/search"
    params = {"breed_id": breed_id, "limit": limit}
    data = safe_get_json(url, params=params)
    if isinstance(data, list):
        return [d.get("url") for d in data if d.get("url")]
    return []


@st.cache_data(show_spinner=False)
def fetch_random_images(limit: int = 8) -> List[str]:
    """
    Fallback random dog images from Dog CEO API (no key).
    """
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
    """
    TheDogAPI returns {'metric': 'xx - yy'} typically.
    """
    if isinstance(x, dict):
        m = x.get("metric")
        if isinstance(m, str) and m.strip():
            return m
    return default


# ----------------------------
# "Curator-style" Narrative (No OpenAI)
#   Use info + templates to make rich descriptions
# ----------------------------
def curator_narrative(b: Dict[str, Any]) -> str:
    name = normalize_text(b.get("name"))
    origin = normalize_text(b.get("origin"))
    group = normalize_text(b.get("breed_group"))
    bred_for = normalize_text(b.get("bred_for"))
    temperament = normalize_text(b.get("temperament"), default="Varied")
    life_span = normalize_text(b.get("life_span"))
    weight = metric_range(b.get("weight"))
    height = metric_range(b.get("height"))

    # Simple structured storytelling
    text = f"""
**{name}** is a breed with a distinctive presence and cultural footprint.  
Originating from **{origin}**, this dog has historically been associated with **{bred_for.lower()}**, 
which shaped its physical build and behavioral traits.

### 🧭 Historical & Functional Context
Belonging to the **{group}** group, {name} evolved through selective breeding aimed at 
balancing **utility** and **companionship**. These historical demands still echo in the breed’s 
modern temperament and needs.

### 🎭 Temperament & Personality
Commonly described as: **{temperament}**.  
In daily life this often translates to:
- strong emotional bonding with humans  
- a clear preference for routines  
- breed-typical instincts tied to its original role

### 🧬 Appearance & Body Language
With an average height of **{height} cm** and weight of **{weight} kg**,  
{name} typically presents:
- a proportionate, functional silhouette  
- expressive facial cues  
- movement patterns hinting at its working ancestry

### 🩺 Care, Health & Lifestyle
Average life expectancy is **{life_span}**.  
To thrive, {name} benefits from:
- consistent exercise matched to energy level  
- early socialization  
- mental enrichment (training, scent games, puzzle toys)

### 💡 Curator’s Highlight
Think of {name} as a “living artifact” of human–animal coevolution:  
a breed whose **form, instincts, and affection** were carefully sculpted across generations.
"""
    return text.strip()


# ----------------------------
# UI
# ----------------------------
st.title("🎨 AI Museum Curator")
st.caption(
    "A curator-style dog breed gallery. "
    "Real breed data is fetched from public APIs and displayed with rich, professional narratives."
)

breeds = fetch_breeds()

# Sidebar Filters
st.sidebar.header("Settings")
all_names = [b.get("name", "Unknown") for b in breeds]
keyword = st.sidebar.text_input("Search breed", "")
breed_groups = sorted(list({normalize_text(b.get("breed_group"), "Unknown") for b in breeds}))
selected_group = st.sidebar.selectbox("Breed Group", ["All"] + breed_groups)

# Filtered list
filtered = []
for b in breeds:
    n = normalize_text(b.get("name"))
    g = normalize_text(b.get("breed_group"), "Unknown")
    if keyword and keyword.lower() not in n.lower():
        continue
    if selected_group != "All" and g != selected_group:
        continue
    filtered.append(b)

if not filtered:
    st.warning("No breeds found. Showing all breeds instead.")
    filtered = breeds

# Breed selector
selected_name = st.sidebar.selectbox("Choose a breed", [normalize_text(b.get("name")) for b in filtered])
current = next((b for b in filtered if normalize_text(b.get("name")) == selected_name), filtered[0])

# Fetch images
breed_id = current.get("id", 0)
images = fetch_breed_images_from_thedogapi(breed_id, limit=10)

# If no images, fallback random
if not images:
    images = fetch_random_images(limit=10)

# Split layout
left, right = st.columns([1.1, 1.4], gap="large")

with left:
    # Hero image
    if images:
        st.image(images[0], use_container_width=True, caption=normalize_text(current.get("name")))
    else:
        st.info("No image available right now.")

    # Gallery
    st.subheader("🖼️ Breed Gallery")
    if len(images) > 1:
        cols = st.columns(3)
        for i, url in enumerate(images[1:10]):
            with cols[i % 3]:
                st.image(url, use_container_width=True)
    else:
        st.write("Gallery will appear here.")

with right:
    st.subheader(f"🐕 {normalize_text(current.get('name'))}")

    # Basic Info
    st.markdown("### 📌 Basic Information")
    c1, c2, c3 = st.columns(3)
    c1.metric("Origin", normalize_text(current.get("origin")))
    c2.metric("Life Span", normalize_text(current.get("life_span")))
    c3.metric("Breed Group", normalize_text(current.get("breed_group"), "Unknown"))

    # Appearance
    st.markdown("### 📏 Appearance")
    a1, a2 = st.columns(2)
    a1.write(f"**Height (cm):** {metric_range(current.get('height'))}")
    a2.write(f"**Weight (kg):** {metric_range(current.get('weight'))}")

    # Temperament
    st.markdown("### 🎭 Temperament & Behavior")
    st.write(normalize_text(current.get("temperament"), default="No temperament data."))

    # Original Purpose
    st.markdown("### 🧭 Original Role / Bred For")
    st.write(normalize_text(current.get("bred_for"), default="No historical role data."))

    # Curator Narrative
    st.markdown("### 🧑‍🎨 Curator’s Interpretation (AI-style)")
    st.markdown(curator_narrative(current))

    # Extra intelligent mini-sections
    st.markdown("### 🧠 Smart Subtopics")
    sub1, sub2 = st.columns(2)
    with sub1:
        st.markdown("**Training Tips**")
        st.write(
            "Use short, positive sessions. "
            "Reward-based learning works best for most breeds."
        )
        st.markdown("**Ideal Home**")
        st.write(
            "Match activity level to living space. "
            "Some breeds prefer busy families, some enjoy quiet routines."
        )
    with sub2:
        st.markdown("**Grooming Notes**")
        st.write(
            "Coat type matters: double coats shed seasonally; "
            "short coats need less brushing."
        )
        st.markdown("**Social Needs**")
        st.write(
            "Early exposure to people, dogs, and environments helps "
            "build confident adult behavior."
        )

# Footer
st.divider()
st.caption(
    "Data Source: Public Dog APIs (TheDogAPI, Dog CEO). "
    "This demo uses a built-in narrative generator, so no OpenAI key is required."
)
