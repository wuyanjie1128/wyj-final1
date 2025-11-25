import streamlit as st
import streamlit.components.v1 as components
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
# Luxury CSS (no wing banners)
# ----------------------------
LUX_CSS = """
<style>
.stApp{
  background: radial-gradient(1200px circle at 10% 0%, #111827 0%, #0b1020 35%, #05060a 100%);
  color:#e5e7eb;
}
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg,#0f172a 0%,#0b1020 100%);
  border-right:1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color:#e5e7eb !important; }

.glass{
  background: rgba(255,255,255,0.045);
  border:1px solid rgba(255,255,255,0.09);
  box-shadow: 0 12px 36px rgba(0,0,0,0.55);
  border-radius:18px;
  padding:18px 18px 14px 18px;
}
.glass-sm{
  background: rgba(255,255,255,0.035);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;
  padding:12px 12px;
}
.gold{ color:#EAB308; font-weight:800; letter-spacing:0.4px; }

.chip{
  display:inline-block;padding:6px 10px;border-radius:999px;
  background: rgba(234,179,8,0.12);color:#fde68a;font-size:12px;margin-right:6px;
  border:1px solid rgba(234,179,8,0.25);
}

.stButton button{
  border-radius:10px !important;
  border:1px solid rgba(234,179,8,0.42) !important;
  background: linear-gradient(180deg, rgba(234,179,8,0.24), rgba(234,179,8,0.05)) !important;
  color:#fff !important;font-weight:700 !important;
  box-shadow:0 8px 18px rgba(234,179,8,0.15);
}
div[data-baseweb="select"] > div{
  background: rgba(255,255,255,0.035) !important;
  border-radius:10px !important;border:1px solid rgba(255,255,255,0.1) !important;
}
input, textarea{
  background: rgba(255,255,255,0.035) !important;
  border-radius:10px !important;border:1px solid rgba(255,255,255,0.1) !important;
  color:#e5e7eb !important;
}
div[data-testid="stMetric"]{
  background: rgba(255,255,255,0.045);
  padding:12px 12px;border-radius:14px;border:1px solid rgba(255,255,255,0.09);
}

/* Masonry */
.masonry{ column-count:4; column-gap:14px; }
@media (max-width: 1400px){ .masonry{ column-count:3; } }
@media (max-width: 1000px){ .masonry{ column-count:2; } }
@media (max-width: 640px){ .masonry{ column-count:1; } }

.card{
  break-inside:avoid;
  background: rgba(255,255,255,0.045);
  border:1px solid rgba(255,255,255,0.09);
  border-radius:16px; overflow:hidden; margin:0 0 14px 0;
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
.card img{ width:100%; height:auto; display:block; }
.card-body{ padding:10px 12px 12px 12px; }
.card-title{ font-weight:800; font-size:16px; color:#f9fafb; margin-bottom:4px; }
.card-meta{ font-size:12px; opacity:0.8; margin-bottom:6px; }
.card-tags span{
  display:inline-block;font-size:11px;padding:4px 7px;border-radius:999px;
  background:rgba(255,255,255,0.06);
  border:1px solid rgba(255,255,255,0.08);
  margin-right:5px;
}
@keyframes fadeUp{
  from{opacity:0;transform: translateY(8px);}
  to{opacity:1;transform: translateY(0);}
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
def fetch_breed_images(breed_id: int, limit: int = 12) -> List[str]:
    data = safe_get_json(
        "https://api.thedogapi.com/v1/images/search",
        params={"breed_id": breed_id, "limit": limit}
    )
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

def breed_thumb_url(b: Dict[str, Any]) -> str:
    ref = b.get("reference_image_id")
    if ref:
        return f"https://cdn2.thedogapi.com/images/{ref}.jpg"
    pool = fetch_random_images(1)
    return pool[0] if pool else ""

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
**{name}** is presented here as a living cultural artifact—its physique and temperament echo centuries of selective breeding.

### 🧭 Department / Geographic Lineage
- **Origin:** {origin}
- **Museum Department:** **{region}**

### 🏛️ Historical Context
Bred for **{bred_for.lower()}**, classified as **{group}**.
Behavior and structure reflect this purpose.

### 🎭 Temperament
**{temperament}**

### 🧬 Physical Form
- Size: **{size}**
- Height: **{height} cm**
- Weight: **{weight} kg**

### 🩺 Care Notes
Life span: **{life_span}**. Routine exercise + mental enrichment recommended.

### 💡 Curator Highlight
A breed shaped by **function → companionship**, preserved like a masterpiece.
""".strip()

# ----------------------------
# Body Parts Wing (no images)
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

# ----------------------------
# Global Medication Knowledge (shown inside diagnosis)
# Categories follow WSAVA essential med structure. :contentReference[oaicite:1]{index=1}
MED_BY_SYSTEM = {
    "Skin / Allergy / Parasite": [
        ("Flea & Tick Control", ["Afoxolaner", "Fluralaner", "Sarolaner", "Fipronil"]),
        ("Dewormers / Antiparasitics", ["Pyrantel", "Fenbendazole", "Praziquantel"]),
        ("Allergy / Itch Control", ["Oclacitinib", "Lokivetmab", "Vet-guided antihistamines"]),
        ("Antibiotics (if bacterial)", ["Cephalexin", "Amoxicillin–clavulanate"]),
        ("Antifungals (if fungal/yeast)", ["Itraconazole", "Terbinafine"])
    ],
    "Eyes/Ears": [
        ("Eye/Ear Drops (cause-specific)", ["Antibiotic drops", "Anti-inflammatory drops", "Artificial tears"]),
        ("Antibiotics (if bacterial)", ["Amoxicillin–clavulanate", "Cephalexin"]),
        ("Allergy control (if allergic)", ["Oclacitinib", "Lokivetmab"])
    ],
    "Digestive / GI": [
        ("Anti-nausea", ["Maropitant (Cerenia)"]),
        ("GI protectants", ["Omeprazole", "Famotidine"]),
        ("Antibiotics/Antiprotozoals (cause-specific)", ["Metronidazole"]),
        ("Probiotics / Diet therapy", ["Vet-approved probiotics"])
    ],
    "Respiratory": [
        ("Antibiotics (if bacterial)", ["Doxycycline", "Amoxicillin–clavulanate"]),
        ("Cough control (vet decides)", ["Cause-specific meds"])
    ],
    "Musculoskeletal / Joint": [
        ("Canine NSAIDs (prescription)", ["Carprofen", "Meloxicam", "Firocoxib"]),
        ("Pain management adjuncts", ["Vet-guided options"])
    ],
    "Neurology": [
        ("Anti-seizure (prescription)", ["Phenobarbital", "Levetiracetam", "Potassium bromide"])
    ]
}

HUMAN_DRUG_WARNING = (
    "⚠️ **Never give human painkillers like ibuprofen/naproxen/acetaminophen to dogs.** "
    "They are toxic and can cause life-threatening reactions. "
    "Use only vet-prescribed canine medications."
)  # :contentReference[oaicite:2]{index=2}

# ----------------------------
# Triage + Diagnosis Heuristics
# ----------------------------
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
    if symptoms["collapse_seizure"]: systems.append("Neurology")

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


def photo_heuristic(photo_type: str, signs: List[str]) -> Tuple[List[str], List[str]]:
    """
    Returns (possible_conditions, related_systems)
    NOTE: heuristic only, not real diagnosis.
    """
    possible = []
    systems = []

    if photo_type == "Skin / Coat":
        systems.append("Skin / Allergy / Parasite")
        if "Red rash / bumps" in signs:
            possible += ["Allergic dermatitis", "Insect bites", "Bacterial folliculitis"]
        if "Circular hair loss" in signs:
            possible += ["Ringworm (fungal)", "Mite-related mange"]
        if "Oily skin / odor" in signs:
            possible += ["Yeast dermatitis", "Seborrhea"]
        if "Ticks / fleas visible" in signs:
            possible += ["Ectoparasite infestation"]

    elif photo_type == "Eyes":
        systems.append("Eyes/Ears")
        if "Redness / swelling" in signs:
            possible += ["Conjunctivitis", "Allergy flare", "Irritation/foreign body"]
        if "Thick discharge" in signs:
            possible += ["Bacterial conjunctivitis", "Blocked tear ducts"]
        if "Cloudy surface" in signs:
            possible += ["Corneal ulcer", "Cataract (needs vet exam)"]

    elif photo_type == "Ears":
        systems.append("Eyes/Ears")
        if "Dark debris" in signs:
            possible += ["Yeast/bacterial otitis", "Ear mites"]
        if "Strong odor" in signs:
            possible += ["Otitis externa"]
        if "Red inflamed canal" in signs:
            possible += ["Allergic ear inflammation", "Infection"]

    elif photo_type == "Mouth / Teeth":
        systems.append("Eyes/Ears")
        if "Red gums / bleeding" in signs:
            possible += ["Gingivitis / periodontal disease"]
        if "Broken tooth" in signs:
            possible += ["Dental fracture (painful, needs vet)"]
        if "Heavy tartar" in signs:
            possible += ["Dental calculus / periodontal risk"]

    elif photo_type == "Paws / Legs":
        systems.append("Musculoskeletal / Joint")
        if "Swollen toe / pad" in signs:
            possible += ["Paw injury", "Foreign body", "Interdigital cyst"]
        if "Bleeding nail" in signs:
            possible += ["Nail trauma"]
        if "Licking constantly" in signs:
            possible += ["Allergy-related paw dermatitis", "Pain"]

    elif photo_type == "Poop / Vomit":
        systems.append("Digestive / GI")
        if "Watery diarrhea" in signs:
            possible += ["Acute gastroenteritis", "Diet intolerance"]
        if "Blood visible" in signs:
            possible += ["Hemorrhagic diarrhea (urgent)", "Parvovirus risk in puppies"]
        if "Worms visible" in signs:
            possible += ["Intestinal parasites"]

    if not possible:
        possible = ["Non-specific abnormality — needs vet confirmation"]

    return sorted(list(set(possible))), sorted(list(set(systems)))


def render_recommended_meds(systems: List[str]):
    if not systems:
        st.write("No specific system detected from inputs.")
        return

    st.markdown("### 💊 Education-Only Medication Categories (Global)")
    st.info(HUMAN_DRUG_WARNING)

    for sys in systems:
        meds = MED_BY_SYSTEM.get(sys, [])
        if not meds:
            continue
        st.markdown(f"**Related System: {sys}**")
        for title, examples in meds:
            st.write(f"- **{title}:** {', '.join(examples)}")
        st.caption("⚠️ These are common global categories. **Actual drug choice/dose requires a veterinarian.**") 


# ----------------------------
# Header (no top photo)
# ----------------------------
st.markdown(
    """
    <div class="glass">
      <h1 style="margin-bottom:6px;">🎨 AI Museum Curator</h1>
      <div class="chip">Global Dog Breeds</div>
      <div class="chip">Curator Narratives</div>
      <div class="chip">Anatomy Wing</div>
      <div class="chip">Symptom + Photo Analyzer</div>
      <p style="opacity:0.9;margin-top:10px;">
        A luxury dog museum where each breed is curated like fine art.
        Health tools are educational triage only.
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Data Prepare
# ----------------------------
breeds = fetch_breeds()
for b in breeds:
    b["region"] = origin_to_region(b.get("origin", ""))
    b["size"] = size_category(metric_range(b.get("weight")))

regions = sorted(list({b.get("region", "Unknown / Global") for b in breeds}))
groups = sorted(list({normalize_text(b.get("breed_group"), "Other/Unknown") for b in breeds}))
sizes = sorted(list({b.get("size", "Unknown") for b in breeds}))


# ----------------------------
# Sidebar Wings (Lobby/Exhibition/MedLibrary removed)
# ----------------------------
st.sidebar.header("Museum Wings")
mode = st.sidebar.radio(
    "Select a wing",
    ["Breed Gallery", "Body Parts Explorer", "Symptom & Photo Analyzer"],
    key="mode"
)


# ============================================================
# WING A: BREED GALLERY
# ============================================================
if mode == "Breed Gallery":
    st.markdown(
        '<div class="glass"><h2>🐶 Breed Gallery Wing</h2>'
        '<p style="opacity:0.9">Explore nearly all dog breeds worldwide with curator narratives and exhibitions.</p></div>',
        unsafe_allow_html=True
    )

    st.sidebar.header("Gallery Settings")
    keyword = st.sidebar.text_input("Search breed", "")
    selected_region = st.sidebar.selectbox("Department", ["All"] + regions)
    selected_group = st.sidebar.selectbox("Breed Group", ["All"] + groups)
    selected_size = st.sidebar.selectbox("Size", ["All"] + sizes)

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

    if st.sidebar.button("🎲 Curator Pick"):
        st.session_state["picked_name"] = normalize_text(random.choice(filtered).get("name"))

    names_list = [normalize_text(b.get("name")) for b in filtered]
    picked_name = st.session_state.get("picked_name")
    default_index = names_list.index(picked_name) if picked_name in names_list else 0

    selected_name = st.selectbox("🎨 Select a breed to open its exhibition", names_list, index=default_index)
    current = next((b for b in filtered if normalize_text(b.get("name")) == selected_name), filtered[0])

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

        st.markdown("### 🎭 Temperament")
        st.write(normalize_text(current.get("temperament"), default="No temperament data."))

        st.markdown("### 🧭 Original Role / Bred For")
        st.write(normalize_text(current.get("bred_for"), default="No historical role data."))

        st.markdown("### 🧑‍🎨 Curator Narrative")
        st.markdown(curator_narrative(current))
        st.markdown("</div>", unsafe_allow_html=True)

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
    components.html("\n".join(wall_html), height=1200, scrolling=True)


# ============================================================
# WING B: BODY PARTS (no images)
# ============================================================
elif mode == "Body Parts Explorer":
    st.markdown(
        '<div class="glass"><h2>🔍 Body Parts Explorer Wing</h2>'
        '<p style="opacity:0.9">Observe dogs by anatomy like a curator studying a masterpiece.</p></div>',
        unsafe_allow_html=True
    )

    part = st.selectbox("Choose a body part", list(BODY_PARTS.keys()))
    info = BODY_PARTS[part]

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
# WING C: SYMPTOM + PHOTO ANALYZER (meds integrated)
# ============================================================
else:
    st.markdown(
        '<div class="glass"><h2>🩺 Symptom & Photo Analyzer Wing</h2>'
        '<p style="opacity:0.9">Educational triage + photo-assisted observation. Not a diagnosis or prescription.</p></div>',
        unsafe_allow_html=True
    )
    st.warning(
        "⚠️ This tool provides **general education only**. It cannot diagnose disease or prescribe medication. "
        "If your dog is very young/old, symptoms are severe, or worsening fast → see a vet."
    )

    tab1, tab2 = st.tabs(["🧾 Symptom Questionnaire", "📷 Photo-Assisted Analyzer"])

    # ---- Tab 1: Questionnaire
    with tab1:
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

            st.markdown("### 💊 Medication Education (based on systems)")
            render_recommended_meds(systems)

            st.markdown("### 📌 What to record for the vet")
            st.write(
                "- Start time and progression\n"
                "- Frequency per day\n"
                "- Photos/videos\n"
                "- Food/environment changes\n"
                "- Any meds already given"
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tab 2: Photo Assisted
    with tab2:
        st.markdown('<div class="glass-sm">Upload one symptom photo. We will analyze using a rule-based curator model.</div>',
                    unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload symptom photo (jpg/png)", type=["jpg","jpeg","png"])
        if uploaded:
            st.image(uploaded, use_container_width=True)

        photo_type = st.selectbox(
            "What does the photo show?",
            ["Skin / Coat", "Eyes", "Ears", "Mouth / Teeth", "Paws / Legs", "Poop / Vomit", "Other / Unknown"]
        )

        # Dynamic sign checklists
        sign_options = {
            "Skin / Coat": ["Red rash / bumps", "Circular hair loss", "Oily skin / odor", "Ticks / fleas visible"],
            "Eyes": ["Redness / swelling", "Thick discharge", "Cloudy surface", "Squinting / closed eye"],
            "Ears": ["Dark debris", "Strong odor", "Red inflamed canal", "Head shaking"],
            "Mouth / Teeth": ["Red gums / bleeding", "Broken tooth", "Heavy tartar", "Drooling a lot"],
            "Paws / Legs": ["Swollen toe / pad", "Bleeding nail", "Licking constantly", "Visible cut/wound"],
            "Poop / Vomit": ["Watery diarrhea", "Blood visible", "Worms visible", "Repeated vomiting"],
            "Other / Unknown": ["Painful posture", "Large lump", "Unknown change"]
        }

        signs = st.multiselect("Visible signs", sign_options.get(photo_type, []))
        text_note = st.text_area("Extra description (optional)", placeholder="e.g., started 2 days ago, dog keeps scratching...")

        if st.button("Analyze Photo"):
            possible_conditions, systems = photo_heuristic(photo_type, signs)

            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown("## 🧠 Photo-Assisted Summary (Educational)")

            st.markdown("### Possible conditions (not diagnosis)")
            for c in possible_conditions:
                st.write(f"- {c}")

            st.markdown("### Related systems")
            for s in systems:
                st.write(f"- {s}")

            st.markdown("### 💊 Medication Education (based on systems)")
            render_recommended_meds(systems)

            st.info(
                "If symptoms are severe, spreading fast, painful, or your dog seems weak → **vet visit is required**. "
                "Photo tools cannot replace physical examination/lab tests."
            )
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.divider()
st.caption("Data Source: TheDogAPI / Dog CEO API. Health sections are educational triage only.")
