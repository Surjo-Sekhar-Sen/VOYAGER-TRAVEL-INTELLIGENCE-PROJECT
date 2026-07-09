"""
Central config for the backend.
Saari env vars aur constants yahi se load hote hai — kisi bhi service file me
hardcoded values nahi dalni, yaha se import karo.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env file backend/ folder me honi chahiye (backend/.env)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ---- LLM (Gemini) ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

# ---- Geocoding (Nominatim - free, OpenStreetMap) ----
# IMPORTANT: Nominatim usage policy ke hisaab se ek valid User-Agent + contact
# batana zaroori hai, warna ban ho sakte ho. Apna app name/email daal dena .env me.
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
NOMINATIM_USER_AGENT = os.getenv(
    "NOMINATIM_USER_AGENT", "bangalore-transit-app/0.1 (contact: set-me@example.com)"
)
# Nominatim free tier: max ~1 request/sec. Isliye httpx client me timeout/retry sambhal ke rakha hai.
NOMINATIM_RATE_LIMIT_SECONDS = 1.0

# ---- Nearby POIs (Overpass API - free, OpenStreetMap) ----
OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT_SECONDS = 25

# Bangalore ke bahar ka result na aaye, isliye ek rough bounding box (south,west,north,east)
# Overpass query me bias/limit karne ke liye. Zaroorat pade to badal sakte ho.
BANGALORE_BBOX = (12.75, 77.35, 13.15, 77.85)

# User jo bolega ("atm", "mall", "petrol pump" etc.) usko OSM tag me map karna padega,
# kyuki OSM khud "amenity=atm" jaisa structured tag use karta hai, free-text nahi.
CATEGORY_TO_OSM_TAGS = {
    "atm": [("amenity", "atm")],
    "bank": [("amenity", "bank")],
    "mall": [("shop", "mall")],
    "petrol pump": [("amenity", "fuel")],
    "fuel": [("amenity", "fuel")],
    "gas station": [("amenity", "fuel")],
    "hospital": [("amenity", "hospital")],
    "pharmacy": [("amenity", "pharmacy")],
    "medical store": [("amenity", "pharmacy")],
    "restaurant": [("amenity", "restaurant")],
    "cafe": [("amenity", "cafe")],
    "grocery": [("shop", "supermarket")],
    "supermarket": [("shop", "supermarket")],
    "school": [("amenity", "school")],
    "college": [("amenity", "college")],
    "park": [("leisure", "park")],
    "police station": [("amenity", "police")],
    "bus stop": [("highway", "bus_stop")],
    "metro station": [("railway", "station")],
}

# ---- CORS (frontend dev server) ----
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
