import os
import random
import requests
import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="AI Dog Breed Curator 🐶",
    page_icon="🐶",
    layout="wide",
)

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
DOG_API_URL = "https://api.thedogapi.com/v1/breeds"

FALLBACK_BREEDS = [
    {
        "id": 1,
        "name": "Affenpinscher",
        "breed_group": "Toy",
        "origin": "Germany, France",
        "life_span": "10 - 12 years",
        "temperament": "Stubborn, Curious, Playful, Adventurous, Active, Fun-loving",
        "weight": {"metric": "3 - 6"},
        "height": {"metric": "23 - 29"},
        "image": {
            "url": "https://cdn2.thedogapi.com/images/BJa4kxc4X.jpg"
        },
    },
    {
        "id": 2,
        "name": "Golden Retriever",
        "breed_group": "Sporting",
        "origin": "Scotland",
        "life_span": "10 - 12 years",
        "temperament": "Intelligent, Friendly, Reliable, Kind, Trustworthy, Confident",
        "weight": {"metric": "25 - 34"},
        "height": {"metric": "51 - 61"},
        "image": {
            "url": "https://cdn2.thedogapi.com/images/HJ7Pzg5EQ.jpg"
        },
    },
    {
        "id": 3,
        "name": "Siberian Husky",
        "breed_group": "Working",
        "origin": "Siberia",
        "life_span": "12 - 15 years",
        "temperament": "Outgoing, Friendly, Alert, Gentle, Intelligent",
        "weight": {"metric": "16 - 27"},
        "height": {"metric": "51 - 60"},
        "image": {
            "url": "https://cdn2.thedogapi.com/images/SyBvVgAq7.jpg"
        },
    },
]

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
@st.cache_data
def load_all_breeds(dog_api_key: str | None = None):
    headers = {}
    if dog_api_key:
        headers["x-api-key"] = dog_api_key

    try:
        resp = requests.get(DOG_API_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list) or len(data) == 0:
            st.warning("Dog API returned no data. Using fallback sample breeds instead.")
            return FALLBACK_BREEDS
        return data
    except Exception as e:
        st.warning(f"Failed to fetch dog breeds from TheDogAPI. Using fallback sample breeds. Error: {e}")
        return FALLBACK_BREEDS


def get_openai_client(api_key: str | None):
    if not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception:
        return None


# ------------------------------------------------------------
# Sidebar: Settings
# ------------------------------------------------------------
st.sidebar.header("Settings")

dog_api_key = st.sidebar.text_input(
    "TheDogAPI Key (optional)",
    type="password",
    help="Optional: add your TheDogAPI key if you have one."
)

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Required for AI curator-style explanations."
)

breeds = load_all_breeds(dog_api_key)
total = len(breeds)

if "index" not in st.session_state:
    st.session_state.index = 0


def go_previous():
    st.session_state.index = (st.session_state.index - 1) % total


def go_next():
    st.session_state.index = (st.session_state.index + 1) % total


def go_random():
    st.session_state.index = random.randint(0, total - 1)


st.sidebar.markdown("### Browse Breeds")
st.sidebar.button("⬅️ Previous", on_click=go_previous)
st.sidebar.button("🔀 Random", on_click=go_random)
st.sidebar.button("➡️ Next", on_click=go_next)

st.sidebar.markdown("---")
st.sidebar.write(f"Total breeds available: **{total}**")

# ------------------------------------------------------------
# Main Content
# ------------------------------------------------------------
st.title("🐶 AI Dog Breed Curator")
st.write("Explore dog breeds with rich information and AI-generated curator-style explanations.")

if total == 0:
    st.error("No breeds available.")
    st.stop()

breed = breeds[st.session_state.index]

st.caption(f"Index: {st.session_state.index + 1} / {total}")

st.header(breed.get("name", "Unknown Breed"))

col1, col2 = st.columns([1, 2])

with col1:
    img_url = breed.get("image", {}).get("url")
    if img_url:
        st.image(img_url, use_column_width=True)
    else:
        st.info("No image available for this breed.")

with col2:
    st.subheader("Breed Information")
    st.markdown(f"**Breed Group:** {breed.get('breed_group', 'N/A')}")
    st.markdown(f"**Origin:** {breed.get('origin', 'Unknown')}")
    st.markdown(f"**Life Span:** {breed.get('life_span', 'N/A')}")
    st.markdown(f"**Temperament:** {breed.get('temperament', 'N/A')}")
    st.markdown(f"**Weight (kg):** {breed.get('weight', {}).get('metric', 'N/A')}")
    st.markdown(f"**Height (cm):** {breed.get('height', {}).get('metric', 'N/A')}")

# ------------------------------------------------------------
# AI Curator Explanation
# ------------------------------------------------------------
st.subheader("Curator's Interpretation")

if not openai_api_key:
    st.info("Please add your OpenAI API key in the sidebar to enable AI explanations.")
else:
    client = get_openai_client(openai_api_key)
    if client is None:
        st.error("Failed to initialize OpenAI client. Please check your API key.")
    else:
        prompt = f"""
You are a professional museum-style curator specializing in dogs and canine history.
Write a detailed, engaging, and informative curator-style explanation for this dog breed.

Include:
- Historical background
- Cultural significance
- Personality and temperament
- Typical role in human society (e.g., companion, working dog, hunting dog)
- Any interesting or surprising facts

Write in a warm but professional tone, as if explaining to visitors in a museum exhibition.

Breed Name: {breed.get('name')}
Breed Group: {breed.get('breed_group')}
Origin: {breed.get('origin')}
Temperament: {breed.get('temperament')}
Life Span: {breed.get('life_span')}
Weight (kg): {breed.get('weight', {}).get('metric')}
Height (cm): {breed.get('height', {}).get('metric')}
"""

        with st.spinner("Generating curator-style explanation..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=350,
                )
                explanation = response.choices[0].message.content
                st.write(explanation)
            except Exception as e:
                # Show friendly error, but don't break the rest of the app
                st.error(
                    "AI generation failed. "
                    "Most likely your OpenAI account has no remaining quota or billing is not set up."
                )
                st.code(str(e), language="text")
