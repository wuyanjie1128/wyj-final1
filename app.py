import streamlit as st
import requests
import random
from typing import List, Dict, Any, Optional, Tuple

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Museum Curator — Dog Museum",
    page_icon="🐶",
    layout="wide",
)

# ----------------------------
# Luxury CSS + Masonry + Animations
# ----------------------------
LUX_CSS = """
<style>
/* Global background */
.stApp{
  background: radial-gradient(1200px circle at 10% 0%, #111827 0%, #0b1020 35%, #05060a 100%);
  color:#e5e7eb;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg,#0f172a 0%,#0b1020 100%);
  border-right:1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color:#e5e7eb !important; }

/* Glass card */
.glass{
  background: rgba(255,255,255,0.045);
  border:1px solid rgba(255,255,255,0.09);
  box-shadow: 0 12px 36px rgba(0,0,0,0.55);
  border-radius:18px;
  padding:18px 18px 14px 18px;
}

/* Small glass */
.glass-sm{
  background: rgba(255,255,255,0.035);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;
  padding:12px 12px;
}

/* Banner */
.banner{
  border-radius:20px;
  overflow:hidden;
  border:1px solid rgba(255,255,255,0.08);
  box-shadow:0 12px 40px rgba(0,0,0,0.55);
}

/* Accent */
.gold{ color:#EAB308; font-weight:800; letter-spacing:0.4px; }

/* Chips */
.chip{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(234,179,8,0.12);
  color:#fde68a;
  font-size:12px;
  margin-right:6px;
  border:1px solid rgba(234,179,8,0.25);
}

/* Buttons */
.stButton button{
  border-radius:10px !important;
  border:1px solid rgba(234,179,8,0.42) !important;
  background: linear-gradient(180deg, rgba(234,179,8,0.24), rgba(234,179,8,0.05)) !important;
  color:#fff !important;
  font-weight:700 !important;
  box-shadow:0 8px 18px rgba(234,179,8,0.15);
}

/* Inputs */
div[data-baseweb="select"] > div{
  background: rgba(255,255,255,0.035) !important;
  border-radius:10px !important;
  border:1px solid rgba(255,255,255,0.1) !important;
}
input, textarea{
  background: rgba(255,255,255,0.035) !important;
  border-radius:10px !important;
  border:1px solid rgba(255,255,255,0.1) !important;
  color:#e5e7eb !important;
}

/* Metric */
div[data-testid="stMetric"]{
  background: rgba(255,255,255,0.045);
  padding:12px 12px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,0.09);
}

/* Masonry visual wall */
.masonry{
  column-count: 4;
  column-gap: 14px;
}
@media (max-width: 1400px){ .masonry{ column-count: 3; } }
@media (max-width: 1000px){ .masonry{ column-count: 2; } }
@media (max-width: 640px){ .masonry{ column-count: 1; } }

.card{
  break-inside: avoid;
  background: rgba(255,255,255,0.045);
  border:1px solid rgba(255,255,255,0.09);
  border-radius:16px;
  overflow:hidden;
  margin:0 0 14px 0;
  box-shadow:0 10px 28px rgba(0,0,0,0.55);
  transform: translateY(0);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  animation: fadeUp .35s ease;
}
.card:hover{
  transform: translateY(-4px);
  border-color: rgba(234,179,8,0.45);
  box-shadow:0 16px 40px rgba(0,0,0,0.7);
}

.card img{
  width:100%;
  height:auto;
  display:block;
}
.card-body{
  padding:10px 12px 12px 12px;
}
.card-title{
  font-weight:800;
  font-size:16px;
  color:#f9fafb;
  margin-bottom:4px;
}
.card-meta{
  font-size:12px;
  opacity:0.8;
  margin-bottom:6px;
}
.card-tags span{
  display:inline-block;
  font-size:11px;
  padding:4px 7px;
  border-radius:999px;
  background:rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.08);
  margin-right:5px;
}

@keyframes fadeUp{
  from{ opacity:0; transform: translateY(8px); }
  to{ opacity:1; transform: translateY(0); }
}
</style>
"""
st.markdown(LUX_CSS, unsafe_allow_html=True)

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
# Banners / Section Images (static)
# ----------------------------
BANNERS = {
    "home": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=1600&auto=format&fit=crop",
    "gallery": "https://images.unsplash.com/photo-1517423440428-a5a00ad493e8?q=80&w=1600&auto=format&fit=crop",
    "parts": "https://images.unsplash.com/photo-1558944351-cd2c1c0704d2?q=80&w=1600&auto=format&fit=crop",
    "triage": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?q=80&w=1600&auto=format&fit=crop",
    "meds": "https://images.unsplash.com/photo-1583912268180-7f0ec4a3e2e8?q=80&w=1600&auto=format&fit=crop",
    "favorites": "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?q=80&w=1600&auto=format&fit=crop",
}
BODY_PART_IMAGES = {
    "Eyes": "https://images.unsplash.com/photo-1583512603826-8b1a9957b9b4?q=80&w=1200&auto=format&fit=crop",
    "Ears": "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?q=80&w=1200&auto=format&fit=crop",
    "Mouth / Teeth": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?q=80&w=1200&auto=format&fit=crop",
    "Skin / Coat": "https://images.unsplash.com/photo-1507146426996-ef05306b995a?q=80&w=1200&auto=format&fit=crop",
    "Paws / Nails": "https://images.unsplash.com/photo-1568572933382-74d440642117?q=80&w=1200&auto=format&fit=crop",
    "Stomach / Digestion": "https://images.unsplash.com/photo-1552053831-71594a27632d?q=80&w=1200&auto=format&fit=crop",
}

# ----------------------------
# Origin -> Department
# ----------------------------
def origin_to_region(origin: str) -> str:
    o = (origin or "").lower()
    asia = ["japan","china","korea","tibet","thailand","vietnam","india","mongolia","siberia","russia","nepal","iran","israel"]
    europe = ["england","scotland","ireland","wales","france","germany","italy","spain","portugal","sweden","norway","finland","denmark",
              "netherlands","belgium","switzerland","austria","poland","hungary","czech","slovakia","croatia","serbia","greece","romania",
              "bulgaria","ukraine","russia","turkey"]
    americas = ["united states","usa","america","canada","mexico","brazil","argentina","chile","peru","colombia","uruguay"]
    africa = ["africa","egypt","morocco","mali","kenya","ethiopia","tunisia","algeria","nigeria","south africa"]
    oceania = ["australia","new zealand","tasmania"]

    if any(k in o for k in asia): return "Asia Gallery"
    if any(k in o for k in europe): return "Europe Gallery"
    if any(k in o for k in americas): return "Americas Gallery"
    if any(k in o for k in africa): return "Africa Gallery"
    if any(k in o for k in oceania): return "Oceania Gallery"
    return "Unknown / Global"


# ----------------------------
# Fetch Breeds
# ----------------------------
@st.cache_data(show_spinner=False)
def fetch_breeds() -> List[Dict[str, Any]]:
    data = safe_get_json("https://api.thedogapi.com/v1/breeds")
    if isinstance(data, list) and len(data) > 0:
        return data
    return [{
        "id": 0, "name": "Golden Retriever",
        "bred_for": "Retrieving", "breed_group": "Sporting",
        "origin": "Scotland", "temperament": "Intelligent, Friendly, Reliable",
        "life_span": "10 - 12 years",
        "weight": {"metric": "25 - 34"}, "height": {"metric": "51 - 61"},
    }]

@st.cache_data(show_spinner=False)
def fetch_breed_images(breed_id: int, limit: int = 10) -> List[str]:
    data = safe_get_json("https://api.thedogapi.com/v1/images/search",
                         params={"breed_id": breed_id, "limit": limit})
    if isinstance(data, list):
        return [d.get("url") for d in data if d.get("url")]
    return []

@st.cache_data(show_spinner=False)
def fetch_random_images(limit: int = 8) -> List[str]:
    data = safe_get_json(f"https://dog.ceo/api/breeds/image/random/{limit}")
    if isinstance(data, dict) and data.get("status") == "success":
        imgs = data.get("message")
        if isinstance(imgs, list):
            return imgs
    return []


def normalize_text(x: Any, default: str = "Unknown") -> str:
    if x is None: return default
    if isinstance(x, str) and x.strip(): return x.strip()
    return default

def metric_range(x: Any, default: str = "Unknown") -> str:
    if isinstance(x, dict):
        m = x.get("metric")
        if isinstance(m, str) and m.strip(): return m
    return default

def get_avg_kg(weight_metric: str) -> Optional[float]:
    try:
        parts = weight_metric.replace("–","-").split("-")
        nums = [float(p.strip()) for p in parts if p.strip()]
        if not nums: return None
        return sum(nums)/len(nums)
    except Exception:
        return None

def size_category(weight_metric: str) -> str:
    avg = get_avg_kg(weight_metric)
    if avg is None: return "Unknown"
    if avg < 10: return "Small"
    if avg < 25: return "Medium"
    if avg < 40: return "Large"
    return "Giant"


# ----------------------------
# Breed Thumbnail (best-effort)
# ----------------------------
def breed_thumb_url(b: Dict[str, Any]) -> str:
    ref = b.get("reference_image_id")
    if ref:
        return f"https://cdn2.thedogapi.com/images/{ref}.jpg"
    # fallback random (cached)
    pool = fetch_random_images(1)
    return pool[0] if pool else BANNERS["gallery"]


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

    return f"""
**{name}** is presented here as a living cultural artifact—  
its physique and temperament echo centuries of selective breeding.

### 🧭 Department / Geographic Lineage
- **Origin:** {origin}
- **Museum Department:** **{region}**

### 🏛️ Historical & Functional Context
Bred for **{bred_for.lower()}**, classified in the **{group}** group.  
These tasks shaped gait, attention, and social instincts.

### 🎭 Temperament & Personality
**{temperament}**  
Often seen as: bonding deeply, acting with role-specific instincts,
and showing energy patterns tied to history.

### 🧬 Physical Form & Visual Impressions
- **Size:** {size}
- **Height:** {height} cm
- **Weight:** {weight} kg  
The silhouette hints at the breed’s original work.

### 🩺 Care Notes
Life span: **{life_span}**.  
Stable routine + physical exercise + brain games = a thriving dog.

### 💡 Curator’s Highlight
A breed shaped by **function**, refined into **companionship**,
and preserved in today’s homes like a masterpiece.
""".strip()


# ----------------------------
# Health Wings Data
# ----------------------------
BODY_PARTS = {
    "Eyes": {
        "normal": ["Clear, bright eyes", "No thick discharge", "Not squinting"],
        "watch_for": ["Yellow/green discharge", "Redness/swelling", "Cloudy haze", "Constant squinting"],
        "meaning": "Eyes can reflect allergy, infection, injury, or age-related change."
    },
    "Ears": {
        "normal": ["Light pink, no strong smell", "Minimal wax"],
        "watch_for": ["Bad odor", "Brown/black debris", "Head shaking", "Pain when touched"],
        "meaning": "Ear problems are common and often allergy/infection related."
    },
    "Mouth / Teeth": {
        "normal": ["Pink gums", "Clean teeth", "No constant drooling"],
        "watch_for": ["Red gums/bleeding", "Bad breath", "Broken tooth", "Refuses food"],
        "meaning": "Dental disease is frequent in dogs—gums and tartar matter."
    },
    "Skin / Coat": {
        "normal": ["Shiny coat", "No bald patches", "No intense itch"],
        "watch_for": ["Hot spots", "Dandruff", "Bumps/lumps", "Heavy scratching"],
        "meaning": "Skin shows allergy, parasites, infection, or hormonal issues."
    },
    "Paws / Nails": {
        "normal": ["Pads not cracked", "Nails not overgrown", "No limping"],
        "watch_for": ["Limping", "Bleeding nail", "Constant licking", "Swollen toes"],
        "meaning": "Paws reveal injury, arthritis, foreign bodies, or dermatitis."
    },
    "Stomach / Digestion": {
        "normal": ["Not bloated", "Regular poop", "Normal appetite"],
        "watch_for": ["Hard bloated belly", "Repeated vomiting", "Black/bloody stool"],
        "meaning": "GI signs range from mild upset to emergencies."
    },
}

def triage(symptoms: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    emergency_flags, soon_flags, systems = [], [], []

    if symptoms["breathing_trouble"]: emergency_flags.append("Breathing trouble")
    if symptoms["collapse_seizure"]: emergency_flags.append("Collapse/seizure")
    if symptoms["bloated_hard_belly"]: emergency_flags.append("Bloated hard belly")
    if symptoms["uncontrolled_bleeding"]: emergency_flags.append("Uncontrolled bleeding")
    if symptoms["cannot_urinate"]: emergency_flags.append("Cannot urinate")
    if symptoms["heatstroke_like"]: emergency_flags.append("Heatstroke signs")

    if symptoms["vomit_diarrhea_hours"] >= 24: soon_flags.append("GI upset >24h")
    if symptoms["appetite_loss_hours"] >= 24: soon_flags.append("No appetite >24h")
    if symptoms["limping_hours"] >= 24: soon_flags.append("Limping >24h")
    if symptoms["eye_ear_pain"]: soon_flags.append("Eye/Ear pain/discharge")
    if symptoms["blood_in_stool_vomit"]: soon_flags.append("Blood in vomit/stool")

    if symptoms["vomit_diarrhea_hours"] > 0: systems.append("Digestive / GI")
    if symptoms["itch_skin"]: systems.append("Skin / Allergy / Parasite")
    if symptoms["cough_sneeze"]: systems.append("Respiratory")
    if symptoms["limping_hours"] > 0: systems.append("Musculoskeletal / Joint")
    if symptoms["eye_ear_pain"]: systems.append("Eyes/Ears")

    if emergency_flags:
        level = "🚨 Emergency — Go to vet/ER now"
        note = ("Emergency signs detected. Online tools cannot diagnose or treat. "
                "Please seek urgent veterinary care immediately.")
    elif soon_flags:
        level = "🟠 Vet Soon (within 24–48h)"
        note = ("Symptoms suggest illness needing professional evaluation. "
                "Contact a vet clinic soon.")
    else:
        level = "🟢 Monitor & Support"
        note = ("No clear emergency signs detected. Monitor closely and see a vet if symptoms persist.")

    curator_note = note + "\n\n**Curator safety note:** This is general education only, not diagnosis or prescription."
    return level, curator_note, systems

MED_LIBRARY = [
    {
        "title": "Parasite Prevention (Flea/Tick)",
        "examples": ["Afoxolaner", "Fluralaner", "Sarolaner"],
        "used_for": "Prevents flea/tick infestations and related skin disease.",
        "watch_for": "Vomiting, lethargy, rare neurologic effects.",
        "note": "Use vet-recommended products; avoid random mixing."
    },
    {
        "title": "Dewormers",
        "examples": ["Pyrantel", "Fenbendazole", "Milbemycin oxime"],
        "used_for": "Treats intestinal parasites.",
        "watch_for": "Occasional mild GI upset.",
        "note": "Parasite type must be confirmed by a vet."
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
        "used_for": "Pain, inflammation, arthritis.",
        "watch_for": "Vomiting, black stool, appetite loss.",
        "note": "Human pain meds can be toxic; never self-dose."
    },
    {
        "title": "Vaccines",
        "examples": ["Rabies", "DHPP", "Leptospirosis"],
        "used_for": "Prevents serious infectious diseases.",
        "watch_for": "Mild fever/soreness after injection.",
        "note": "Schedule depends on age and region."
    },
]


# ----------------------------
# Session State: Favorites
# ----------------------------
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []  # store breed dicts
if "picked_name" not in st.session_state:
    st.session_state["picked_name"] = None


# ----------------------------
# Header / Home Title Block
# ----------------------------
st.markdown(
    f"""
    <div class="glass">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:16px;">
        <div>
          <h1 style="margin-bottom:6px;">🎨 AI Museum Curator</h1>
          <div class="chip">Global Dog Breeds</div>
          <div class="chip">Curator Narratives</div>
          <div class="chip">Anatomy Wing</div>
          <div class="chip">Health Triage</div>
          <div class="chip">Medication Library</div>
          <div class="chip">My Exhibition</div>
          <p style="opacity:0.9;margin-top:10px;">
            A luxury-style dog museum where each breed is curated like fine art.
            No OpenAI key required.
          </p>
        </div>
        <div style="min-width:320px;max-width:440px;">
          <img class="banner" src="{BANNERS['home']}" style="width:100%;height:220px;object-fit:cover;">
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

breeds = fetch_breeds()
for b in breeds:
    b["region"] = origin_to_region(b.get("origin", ""))
    b["size"] = size_category(metric_range(b.get("weight")))

# Quick stats
regions = sorted(list({b.get("region", "Unknown / Global") for b in breeds}))
groups = sorted(list({normalize_text(b.get("breed_group"), "Other/Unknown") for b in breeds}))

# ----------------------------
# Sidebar: Wings
# ----------------------------
st.sidebar.header("Museum Wings")
mode = st.sidebar.radio(
    "Select a wing",
    ["Home Lobby", "Breed Gallery", "Body Parts Explorer", "Symptom Checker", "Medication Library", "My Exhibition"]
)

# ============================================================
# WING 0: HOME LOBBY (Museum entrance)
# ============================================================
if mode == "Home Lobby":
    st.image(BANNERS["home"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>🏛️ Museum Lobby</h2>'
        '<p style="opacity:0.9">Welcome to a global dog museum. Choose a wing, explore departments, and curate your own exhibition.</p></div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Breeds", f"{len(breeds)}")
    c2.metric("Departments", f"{len(regions)}")
    c3.metric("Breed Groups", f"{len(groups)}")
    c4.metric("Your Favorites", f"{len(st.session_state['favorites'])}")

    st.markdown("### 🗺️ Departments Preview")
    dept_cols = st.columns(3)
    for i, r in enumerate(regions):
        sample = [b for b in breeds if b.get("region") == r]
        if not sample:
            continue
        pick = random.choice(sample)
        img = breed_thumb_url(pick)

        with dept_cols[i % 3]:
            st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown(f"**{r}**")
            st.caption(f"Examples: {', '.join([normalize_text(x.get('name')) for x in random.sample(sample, min(3,len(sample)))])}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ⭐ Curator’s Picks")
    picks = random.sample(breeds, k=min(6, len(breeds)))
    pick_cols = st.columns(3)
    for i, b in enumerate(picks):
        with pick_cols[i % 3]:
            st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
            st.image(breed_thumb_url(b), use_container_width=True)
            st.markdown(f"**{normalize_text(b.get('name'))}**")
            st.caption(f"{b.get('region','Unknown')} · {normalize_text(b.get('breed_group'),'Other/Unknown')}")
            if st.button("View in Gallery", key=f"lobby_view_{b.get('id')}"):
                st.session_state["picked_name"] = normalize_text(b.get("name"))
                st.session_state["force_mode"] = "Breed Gallery"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# If user jumped from lobby
if st.session_state.get("force_mode"):
    mode = st.session_state.pop("force_mode")

# ============================================================
# WING A: BREED GALLERY
# ============================================================
if mode == "Breed Gallery":
    st.image(BANNERS["gallery"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>🐶 Breed Gallery Wing</h2>'
        '<p style="opacity:0.9">Explore almost all dog breeds worldwide with curator-style narratives and multi-image exhibitions.</p></div>',
        unsafe_allow_html=True
    )

    # Sidebar filters
    st.sidebar.header("Gallery Settings")
    keyword = st.sidebar.text_input("Search breed", "")
    selected_region = st.sidebar.selectbox("Department (Region Gallery)", ["All"] + regions)
    selected_group = st.sidebar.selectbox("Breed Group", ["All"] + groups)
    sizes = sorted(list({b.get("size", "Unknown") for b in breeds}))
    selected_size = st.sidebar.selectbox("Size Category", ["All"] + sizes)

    filtered = []
    for b in breeds:
        n = normalize_text(b.get("name"))
        r = b.get("region", "Unknown / Global")
        g = normalize_text(b.get("breed_group"), "Other/Unknown")
        s = b.get("size", "Unknown")
        if keyword and keyword.lower() not in n.lower(): continue
        if selected_region != "All" and r != selected_region: continue
        if selected_group != "All" and g != selected_group: continue
        if selected_size != "All" and s != selected_size: continue
        filtered.append(b)
    if not filtered:
        st.warning("No breeds found with current filters. Showing all breeds instead.")
        filtered = breeds

    st.sidebar.divider()
    if st.sidebar.button("🎲 Curator Pick (Random Breed)"):
        st.session_state["picked_name"] = normalize_text(random.choice(filtered).get("name"))

    names_list = [normalize_text(b.get("name")) for b in filtered]
    picked_name = st.session_state.get("picked_name")
    default_index = names_list.index(picked_name) if picked_name in names_list else 0

    selected_name = st.selectbox("🎨 Select a breed to open its exhibition", names_list, index=default_index)
    current = next((b for b in filtered if normalize_text(b.get("name")) == selected_name), filtered[0])

    # Add to favorites button
    fav_ids = {x.get("id") for x in st.session_state["favorites"]}
    if current.get("id") not in fav_ids:
        if st.button("⭐ Add to My Exhibition"):
            st.session_state["favorites"].append(current)
            st.success("Added to your exhibition!")
    else:
        st.info("Already in your exhibition.")

    # Detail exhibition
    images = fetch_breed_images(current.get("id", 0), limit=12)
    if not images:
        images = fetch_random_images(limit=12)

    left, right = st.columns([1.05, 1.7], gap="large")
    with left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.image(images[0], use_container_width=True, caption=normalize_text(current.get("name")))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass"><h3>🖼️ Exhibition Gallery</h3></div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, url in enumerate(images[1:12]):
            with cols[i % 3]:
                st.image(url, use_container_width=True)

    with right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader(f"✨ {normalize_text(current.get('name'))}")

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

        st.markdown("### 🧑‍🎨 Curator’s Interpretation")
        st.markdown(curator_narrative(current))
        st.markdown("</div>", unsafe_allow_html=True)

    # Visual Masonry Wall (high-end look)
    st.markdown("### 🧱 Global Breed Card Wall")
    wall_html = ['<div class="masonry">']
    for b in random.sample(filtered, k=min(80, len(filtered))):
        wall_html.append(f"""
        <div class="card">
            <img src="{breed_thumb_url(b)}"/>
            <div class="card-body">
                <div class="card-title">{normalize_text(b.get("name"))}</div>
                <div class="card-meta">{b.get("region","Unknown")} · {normalize_text(b.get("breed_group"),"Other/Unknown")}</div>
                <div class="card-tags">
                  <span>{b.get("size","Unknown")}</span>
                  <span>{normalize_text(b.get("origin"),"Unknown")}</span>
                </div>
            </div>
        </div>
        """)
    wall_html.append("</div>")
    st.markdown("\n".join(wall_html), unsafe_allow_html=True)

# ============================================================
# WING B: BODY PARTS
# ============================================================
elif mode == "Body Parts Explorer":
    st.image(BANNERS["parts"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>🔍 Body Parts Explorer Wing</h2>'
        '<p style="opacity:0.9">Observe dogs by anatomy like a curator studying a masterpiece. Education only.</p></div>',
        unsafe_allow_html=True
    )

    part = st.selectbox("Choose a body part", list(BODY_PARTS.keys()))
    info = BODY_PARTS[part]
    colA, colB = st.columns([1.1, 1.3], gap="large")

    with colA:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.image(BODY_PART_IMAGES.get(part, BANNERS["parts"]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"## {part}")

        st.markdown("### ✅ What looks normal")
        for x in info["normal"]:
            st.write(f"- {x}")

        st.markdown("### ⚠️ What to watch for")
        for x in info["watch_for"]:
            st.write(f"- {x}")

        st.markdown("### 🧑‍🎨 Curator Note")
        st.write(info["meaning"])

        st.info("Severe pain / rapid worsening / multiple abnormal signs → consult a veterinarian.")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# WING C: SYMPTOM CHECKER
# ============================================================
elif mode == "Symptom Checker":
    st.image(BANNERS["triage"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>🩺 Symptom Checker Wing</h2>'
        '<p style="opacity:0.9">A triage-style curator assistant. Not a diagnosis, no prescriptions.</p></div>',
        unsafe_allow_html=True
    )

    st.warning("General education only. This cannot diagnose disease or prescribe medication.")

    with st.form("symptom_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Dog age (years)", 0.0, 30.0, 3.0, 0.5)
            size = st.selectbox("Dog size", ["Small", "Medium", "Large", "Giant", "Unknown"])
        with col2:
            vomit_diarrhea_hours = st.slider("Vomiting/diarrhea duration (hours)", 0, 72, 0)
            appetite_loss_hours = st.slider("Not eating duration (hours)", 0, 72, 0)
            limping_hours = st.slider("Limping duration (hours)", 0, 168, 0)

        st.markdown("### Other observations")
        itch_skin = st.checkbox("Strong itching / skin rash")
        cough_sneeze = st.checkbox("Coughing / sneezing a lot")
        eye_ear_pain = st.checkbox("Eye/ear pain or discharge")
        blood_in_stool_vomit = st.checkbox("Blood in vomit or stool")

        st.markdown("### Emergency signs (tick if yes)")
        breathing_trouble = st.checkbox("Trouble breathing")
        collapse_seizure = st.checkbox("Collapse / seizure")
        bloated_hard_belly = st.checkbox("Bloated, hard belly")
        uncontrolled_bleeding = st.checkbox("Uncontrolled bleeding")
        cannot_urinate = st.checkbox("Cannot urinate")
        heatstroke_like = st.checkbox("Heatstroke-like signs")

        submitted = st.form_submit_button("Analyze")

    if submitted:
        sym = dict(
            age=age, size=size,
            vomit_diarrhea_hours=vomit_diarrhea_hours,
            appetite_loss_hours=appetite_loss_hours,
            limping_hours=limping_hours,
            itch_skin=itch_skin, cough_sneeze=cough_sneeze, eye_ear_pain=eye_ear_pain,
            blood_in_stool_vomit=blood_in_stool_vomit,
            breathing_trouble=breathing_trouble, collapse_seizure=collapse_seizure,
            bloated_hard_belly=bloated_hard_belly, uncontrolled_bleeding=uncontrolled_bleeding,
            cannot_urinate=cannot_urinate, heatstroke_like=heatstroke_like
        )

        level, note, systems = triage(sym)

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"## {level}")
        st.markdown(note)

        if systems:
            st.markdown("### 🧠 Possible related systems (broad)")
            for s in systems:
                st.write(f"- {s}")

        st.markdown("### 📌 What to record for the vet")
        st.write(
            "- Start time and speed of change\n"
            "- Frequency per day\n"
            "- Photos/videos\n"
            "- Food/environment changes\n"
            "- Any meds already given"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# WING D: MEDICATION LIBRARY
# ============================================================
elif mode == "Medication Library":
    st.image(BANNERS["meds"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>💊 Medication Library Wing</h2>'
        '<p style="opacity:0.9">Curator-grade medication knowledge. Education only, no dosing.</p></div>',
        unsafe_allow_html=True
    )

    st.warning("Never give human medication or change dog doses yourself. Vet decides medicine + dose.")

    for med in MED_LIBRARY:
        with st.expander(f"📁 {med['title']}"):
            st.markdown("**Examples (not recommendations):** " + ", ".join(med["examples"]))
            st.markdown("**Used for:** " + med["used_for"])
            st.markdown("**Watch for:** " + med["watch_for"])
            st.markdown("**Curator safety note:** " + med["note"])

# ============================================================
# WING E: MY EXHIBITION (Favorites)
# ============================================================
else:
    st.image(BANNERS["favorites"], use_container_width=True)
    st.markdown(
        '<div class="glass"><h2>⭐ My Exhibition Wing</h2>'
        '<p style="opacity:0.9">Your private curated gallery. Collect breeds and present your own museum exhibition.</p></div>',
        unsafe_allow_html=True
    )

    favs = st.session_state["favorites"]
    if not favs:
        st.info("Your exhibition is empty. Add breeds from the Gallery wing.")
    else:
        # Export buttons
        export_md = "\n".join([f"- {normalize_text(b.get('name'))} ({b.get('region','Unknown')})" for b in favs])
        st.download_button(
            "⬇️ Export Exhibition (Markdown)",
            data=export_md,
            file_name="my_exhibition.md"
        )

        # Remove controls
        st.markdown("### 🗃️ Exhibition Collection")
        for b in favs[:]:
            colx, coly = st.columns([6,1])
            with colx:
                st.write(f"**{normalize_text(b.get('name'))}** · {b.get('region','Unknown')} · {normalize_text(b.get('breed_group'),'Other/Unknown')}")
            with coly:
                if st.button("Remove", key=f"rm_{b.get('id')}"):
                    st.session_state["favorites"] = [x for x in favs if x.get("id") != b.get("id")]
                    st.rerun()

        # Masonry wall of favorites
        st.markdown("### 🖼️ My Exhibition Wall")
        wall_html = ['<div class="masonry">']
        for b in favs:
            wall_html.append(f"""
            <div class="card">
                <img src="{breed_thumb_url(b)}"/>
                <div class="card-body">
                    <div class="card-title">{normalize_text(b.get("name"))}</div>
                    <div class="card-meta">{b.get("region","Unknown")} · {normalize_text(b.get("breed_group"),"Other/Unknown")}</div>
                </div>
            </div>
            """)
        wall_html.append("</div>")
        st.markdown("\n".join(wall_html), unsafe_allow_html=True)

# Footer
st.divider()
st.caption("Data Source: TheDogAPI / Dog CEO API. Health wings are educational triage only.")
