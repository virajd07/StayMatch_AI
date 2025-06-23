import os
import requests
from dotenv import load_dotenv
from streamlit_js_eval import streamlit_js_eval

# Load environment variables from .env
load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

def get_user_coordinates():
    """
    Uses browser geolocation via streamlit-js-eval to get user coordinates.
    Returns: (latitude, longitude) or (None, None) if not available.
    """
    result = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_location")
    if result and "coords" in result:
        lat = result["coords"]["latitude"]
        lon = result["coords"]["longitude"]
        return lat, lon
    return None, None

def reverse_geocode(lat, lon):
    """
    Uses OpenCage API to convert coordinates to human-readable location (area and city).
    """
    if not OPENCAGE_API_KEY:
        raise ValueError("OpenCage API key not found. Please add it to your .env file.")

    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={OPENCAGE_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["results"]:
            comp = data["results"][0]["components"]
            area = comp.get("suburb") or comp.get("neighbourhood") or comp.get("village") or ""
            city = comp.get("city") or comp.get("town") or comp.get("state_district") or ""
            return area.title(), city.title()
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
    return None, None
