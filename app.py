import random
import requests
import streamlit as st

# ------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dog Breed Explorer 🐶",
    page_icon="🐶",
    layout="wide",
)

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
DOG_API_URL = "https://api.thedogapi.com/v1/breeds"

# Fallback data if external API request fails (keeps UI working!)
FALLBACK_BREEDS = [
    {
        "name": "Affenpinscher",
        "breed_group": "Toy",
        "origin": "Germany, France",
        "life_span": "10 - 12 years",
        "temperament": "Stubborn, Curious, Playful, Adventurous, Active, Fun-loving",
        "weight": {"metric": "3 - 6"},
        "height": {"metric": "23 - 29"},
        "image": {"url": "https://cdn2.thedogapi.com/images/BJa4kxc4X.jpg"},
    },
    {
        "name": "Golden Retriever",
        "breed_group": "Sporting",
        "origin": "Scotland",
        "life_span": "10 - 12 years",
        "temperament": "Friendly, Reliable, Kind, Confident",
        "weight": {"metric": "25 - 34"},
        "height": {"metric": "51 - 61"},
        "image": {"url": "https://cdn2.thedogapi.com/images/HJ7Pzg5EQ.jpg"},
    },
    {
        "name": "Siberian Husky",
        "breed_group": "Working",
        "origin": "Siberia",
        "life_span": "12 - 15 years",
        "temperament": "Outgoing, Friendly, Alert, Gentle",
        "weight": {"metric": "16 - 27"},
        "height": {"metric": "51 - 60"},
        "image": {"url": "https://cdn2.thedogapi.com/images/SyBvVgAq7.jpg"},
    },
]

# ------------------------------------------------------------
# Helper to fetch data safely
# ------------------------------------------------------------
@st.cache_data
def load_all_breeds():
    try:
        response = requests.get(DOG_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) == 0:
            return FALLBACK_BREEDS
        return data
    except:
        return FALLBACK_BREEDS


breeds = load_all_breeds()
total = len(breeds)

if "index" not in st.session_state:
    st.session_state.index = 0

def go_previous():
    st.session_state.index = (st.session_state.index - 1) % total

def go_next():
    st.session_state.index = (st.session_state.index + 1) % total

def go_random():
    st.session_state.index = random.randint(0, total - 1)

# ------------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------------
st.sidebar.title("Navigation")
st.sidebar.button("⬅️ Previous", on_click=go_previous)
st.sidebar.button("🔀 Random", on_click=go_random)
st.sidebar.button("➡️ Next", on_click=go_next)
st.sidebar.write(f"Total Breeds: **{total}**")

# ------------------------------------------------------------
# Main Display
# ------------------------------------------------------------
st.title("🐶 Dog Breed Explorer")
st.write("Browse real-world dog breeds with images and key details!")

breed = breeds[st.session_state.index]

st.header(breed.get("name", "Unknown Breed"))
st.caption(f"Breed Index: {st.session_state.index + 1} / {total}")

col1, col2 = st.columns([1.2, 1.8])

with col1:
    img_url = breed.get("image", {}).get("url")
    if img_url:
        st.image(img_url, use_column_width=True)
    else:
        st.warning("No image available for this breed.")

with col2:
    st.subheader("Details")
    st.markdown(f"**Breed Group:** {breed.get('breed_group', 'N/A')}")
    st.markdown(f"**Origin:** {breed.get('origin', 'Unknown')}")
    st.markdown(f"**Life Span:** {breed.get('life_span', 'N/A')}")
    st.markdown(f"**Temperament:** {breed.get('temperament', 'N/A')}")
    st.markdown(f"**Weight (kg):** {breed.get('weight', {}).get('metric', 'N/A')}")
    st.markdown(f"**Height (cm):** {breed.get('height', {}).get('metric', 'N/A')}")
