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
# API Constants
# ------------------------------------------------------------
DOG_API_URL = "https://api.thedogapi.com/v1/breeds"

# ------------------------------------------------------------
# Helper: Load All Dog Breeds
# ------------------------------------------------------------
@st.cache_data
def load_all_breeds():
    try:
        response = requests.get(DOG_API_URL)
        response.raise_for_status()
        return response.json()
    except:
        st.error("Failed to fetch dog breed data from TheDogAPI.")
        return []

all_breeds = load_all_breeds()

# ------------------------------------------------------------
# Sidebar: Navigation
# ------------------------------------------------------------
st.sidebar.header("Navigation")

if "index" not in st.session_state:
    st.session_state.index = 0

total = len(all_breeds)

def go_previous():
    st.session_state.index = (st.session_state.index - 1) % total

def go_next():
    st.session_state.index = (st.session_state.index + 1) % total

def go_random():
    st.session_state.index = random.randint(0, total - 1)

st.sidebar.button("⬅️ Previous", on_click=go_previous)
st.sidebar.button("🔀 Random", on_click=go_random)
st.sidebar.button("➡️ Next", on_click=go_next)

# ------------------------------------------------------------
# Sidebar: API Key
# ------------------------------------------------------------
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Add your OpenAI API key to generate curator-style explanations."
)

# ------------------------------------------------------------
# Main UI
# ------------------------------------------------------------
st.title("🐶 AI Dog Breed Curator")
st.write("Explore real dog breed information enhanced with AI-generated curator-style explanations.")

if total == 0:
    st.stop()

breed = all_breeds[st.session_state.index]

# ------------------------------------------------------------
# Display Dog Information
# ------------------------------------------------------------
st.header(breed.get("name", "Unknown Breed"))

col1, col2 = st.columns([1, 2])

with col1:
    if breed.get("image") and breed["image"].get("url"):
        st.image(breed["image"]["url"], use_column_width=True)
    else:
        st.info("No image available.")

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
    st.info("Please add your OpenAI API key in the sidebar to generate AI explanations.")
else:
    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
You are an elite museum curator specializing in zoology and canine history.
Provide a rich, elegant, and deeply informative curator-style explanation 
for the following dog breed.

Include:
- Historical background  
- Cultural significance  
- Personality traits  
- Role in society  
- Any interesting facts  

Breed Name: {breed.get('name')}
Breed Group: {breed.get('breed_group')}
Origin: {breed.get('origin')}
Temperament: {breed.get('temperament')}
Life Span: {breed.get('life_span')}
Weight: {breed.get('weight', {}).get('metric')}
Height: {breed.get('height', {}).get('metric')}
"""

    with st.spinner("Generating curator-style explanation..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            explanation = response.choices[0].message.content
            st.write(explanation)
        except Exception as e:
            st.error(f"AI generation failed: {e}")
