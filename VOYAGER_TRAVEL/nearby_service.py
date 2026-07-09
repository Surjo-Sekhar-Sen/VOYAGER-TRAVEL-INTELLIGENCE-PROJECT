"""
Nearby POI service — free OpenStreetMap Overpass API se "nearby ATMs / malls /
petrol pumps" type queries handle karta hai.

NOTE: Overpass data crowd-sourced hai — matlab tumne khud bataya tha ki kuch
jagah galat/purani ho sakti hai (band ho chuki, ya asal me exist nahi karti).
Isi wajah se iske baad `llm_verify_service.py` chalta hai jo in results ko
tags ke basis pe filter/rank karta hai. Reviews/JustDial live scraping paid +
ToS-restricted hai, isliye MVP me hum OSM ke apne "signal" tags (opening_hours,
disused:*, name missing, etc.) ko hi verification input maan rahe hai.
"""
import math
import httpx
from app.config import OVERPASS_BASE_URL, OVERPASS_TIMEOUT_SECONDS, CATEGORY_TO_OSM_TAGS


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Do lat/long points ke beech ki distance (km) — seedha tumhare diye formula ke hisaab se."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _build_overpass_query(lat: float, lon: float, radius_m: int, tag_pairs: list[tuple[str, str]]) -> str:
    """
    Overpass QL query banata hai. Multiple tag_pairs ho sakte hai (e.g. "fuel" sirf
    ek tag se milta hai, but future categories me OR condition lag sakti hai).
    """
    clauses = []
    for key, value in tag_pairs:
        clauses.append(f'node["{key}"="{value}"](around:{radius_m},{lat},{lon});')
        clauses.append(f'way["{key}"="{value}"](around:{radius_m},{lat},{lon});')
    body = "\n  ".join(clauses)
    return f"""
[out:json][timeout:{OVERPASS_TIMEOUT_SECONDS}];
(
  {body}
);
out center tags;
"""


async def find_nearby(latitude: float, longitude: float, category: str, radius_km: float = 2.0) -> list[dict]:
    """
    Category (jaise "atm") + user location -> raw OSM POIs list (verification se PEHLE).
    Return: list of dicts with name, lat, lon, distance_km, osm_id, tags
    """
    category_key = category.strip().lower()
    tag_pairs = CATEGORY_TO_OSM_TAGS.get(category_key)
    if not tag_pairs:
        raise ValueError(
            f"Category '{category}' abhi supported nahi hai. "
            f"Supported: {list(CATEGORY_TO_OSM_TAGS.keys())}"
        )

    query = _build_overpass_query(latitude, longitude, int(radius_km * 1000), tag_pairs)

    async with httpx.AsyncClient(timeout=OVERPASS_TIMEOUT_SECONDS + 5) as client:
        resp = await client.post(OVERPASS_BASE_URL, data={"data": query})
        resp.raise_for_status()
        data = resp.json()

    places = []
    for el in data.get("elements", []):
        # "way" elements ka center milta hai, "node" ka seedha lat/lon
        if el["type"] == "node":
            plat, plon = el["lat"], el["lon"]
        else:
            center = el.get("center")
            if not center:
                continue
            plat, plon = center["lat"], center["lon"]

        tags = el.get("tags", {})
        name = tags.get("name", "Unnamed")

        places.append({
            "name": name,
            "latitude": plat,
            "longitude": plon,
            "category": category_key,
            "distance_km": round(haversine_km(latitude, longitude, plat, plon), 3),
            "osm_id": f"{el['type']}/{el['id']}",
            "tags": tags,
        })

    places.sort(key=lambda p: p["distance_km"])
    return places
