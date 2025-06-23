import sys
st.info(f"🧠 Python version: {sys.version}")
import os
import streamlit as st
import pandas as pd
import folium
from dotenv import load_dotenv
from streamlit_folium import st_folium
import streamlit.components.v1 as components

from utils.getlocation import get_user_coordinates, reverse_geocode
from utils.map_utils import create_map
from utils.voice_utils import voice_input_html
from utils.sentiment import get_sentiment_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "pg_dataset_with_coords.csv")
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

df = pd.read_csv(DATA_PATH)
df["City"] = df["City"].astype(str).str.strip()
df["Area"] = df["Area"].astype(str).str.strip()

city_list = sorted(df["City"].unique())
types = df["Type"].unique()
foods = df["Food Quality"].unique()
rooms = df["Room Quality"].unique()

# Emoji display for amenities
def display_amenities(text):
    icon_map = {
        "WiFi": "🛜", "AC": "❄️", "Laundry": "🧺", "Gym": "🏋️‍♂️", "Security": "🛡️",
        "Power Backup": "🔌", "Parking": "🚗", "Housekeeping": "🧹", "Lift": "🛗",
        "Water Purifier": "🚰", "CCTV": "📹", "Study Table": "📚", "Fridge": "🧊",
        "Geyser": "♨️", "TV": "📺", "Balcony": "🌇", "Mattress": "🛏️", "24x7 Water": "💧"
    }
    return " ".join([icon_map.get(i.strip(), i.strip()) for i in text.split(',')])

st.set_page_config(page_title="AI PG Recommender", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏠 AI-Based PG, Hostel & Flat Recommender</h1>", unsafe_allow_html=True)

# ---------------------- SIDEBAR FILTERS ----------------------
with st.sidebar:
    st.header("⚙️ Filter Your Stay")
    use_location = st.checkbox("📍 Auto-detect my location")

    if use_location:
        lat, lon = get_user_coordinates()
        if lat and lon:
            area, city = reverse_geocode(lat, lon)
            st.success(f"🎯 You are near {area}, {city}")
            selected_city = city.strip().title()
            selected_area = area.strip().title()
        else:
            st.warning("📡 Location not detected. Please use manual filters.")
            selected_city = st.selectbox("Select City", city_list)
            selected_area = "All"
    else:
        selected_city = st.selectbox("Select City", city_list)
        areas = list(df[df["City"] == selected_city]["Area"].unique())
        selected_area = st.selectbox("Select Area", ["All"] + sorted(areas))

    selected_type = st.multiselect("Accommodation Type", types, default=list(types))
    food_quality = st.multiselect("Food Quality", foods)
    room_quality = st.multiselect("Room Quality", rooms)
    min_price = st.slider("Min Price", 3000, 20000, 4000, step=500)
    max_price = st.slider("Max Price", 4000, 30000, 15000, step=500)

    sort_option = st.selectbox(
        "📊 Sort Results By",
        [
            "Price: Low to High",
            "Price: High to Low",
            "Safety Score: High to Low",
            "Safety Score: Low to High"
        ]
    )

    st.markdown("🎤 Voice Input (optional):")
    components.html(voice_input_html(), height=100)

# ---------------------- APPLY FILTERS ----------------------
filtered = df[df["City"] == selected_city]
if selected_area != "All":
    filtered = filtered[filtered["Area"] == selected_area]
if selected_type:
    filtered = filtered[filtered["Type"].isin(selected_type)]
if food_quality:
    filtered = filtered[filtered["Food Quality"].isin(food_quality)]
if room_quality:
    filtered = filtered[filtered["Room Quality"].isin(room_quality)]
filtered = filtered[(filtered["Price"] >= min_price) & (filtered["Price"] <= max_price)]

# ✅ Sorting
if sort_option == "Price: Low to High":
    filtered = filtered.sort_values(by="Price", ascending=True)
elif sort_option == "Price: High to Low":
    filtered = filtered.sort_values(by="Price", ascending=False)
elif sort_option == "Safety Score: High to Low":
    filtered = filtered.sort_values(by="Safety Score", ascending=False)
elif sort_option == "Safety Score: Low to High":
    filtered = filtered.sort_values(by="Safety Score", ascending=True)

# ---------------------- RESULTS + MAP ----------------------
tab1, tab2 = st.tabs(["📋 Results", "🗺️ Map View"])

# 📋 Results Tab
with tab1:
    st.markdown(f"<h3>📍 Results for <b>{selected_city}</b>{' - ' + selected_area if selected_area != 'All' else ''}</h3>", unsafe_allow_html=True)
    if not filtered.empty:
        for _, row in filtered.iterrows():
            st.markdown(f"""
                <div style='border:2px solid #ccc; padding:15px; border-radius:10px; margin-bottom:10px; background-color:#000; color:white'>
                    <h4>{row['Name']} — <i>{row['Type']}</i></h4>
                    <b>Area:</b> {row['Area']} | <b>City:</b> {row['City']}<br>
                    <b>Price:</b> ₹{row['Price']} | <b>Accommodations:</b> {row['Accommodations']}<br>
                    <b>Food Quality:</b> {row['Food Quality']} | <b>Room Quality:</b> {row['Room Quality']}<br>
                    <b>Nearby:</b> {row['Nearby Institutes']}, {row['Nearby Hospitals']}, {row['Nearby Malls']}<br>
                    <b>Amenities:</b> {display_amenities(row['Amenities'])}<br>
            """, unsafe_allow_html=True)

            if 'Reviews' in row and pd.notnull(row['Reviews']):
                label, score = get_sentiment_score(row['Reviews'])
                color = "green" if label.upper() == "POSITIVE" else "red"
                st.markdown(f"<b>🗣️ Review Sentiment:</b> <span style='color:{color}'>{label.title()} ({score})</span><br>", unsafe_allow_html=True)

            if 'Safety Score' in row and pd.notnull(row['Safety Score']):
                st.markdown(f"<b>🛡️ Area Safety Score:</b> ⭐ {row['Safety Score']} / 5<br>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("😕 No PGs or Flats found for the selected filters.")

# 🗺️ Map Tab
with tab2:
    st.subheader("🗺️ Map View")
    filtered = filtered[pd.to_numeric(filtered["Latitude"], errors="coerce").notnull()]
    filtered = filtered[pd.to_numeric(filtered["Longitude"], errors="coerce").notnull()]
    filtered["Latitude"] = filtered["Latitude"].astype(float)
    filtered["Longitude"] = filtered["Longitude"].astype(float)

    if not filtered.empty:
        m = create_map(filtered)
        st_folium(m, width=700, height=500)
    else:
        st.warning("No valid locations available to show on map.")
