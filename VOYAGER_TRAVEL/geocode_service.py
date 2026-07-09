"""
Geocoding service — free OpenStreetMap Nominatim use kar rahe hai.
Kaam: user jo place type kare (autocomplete) ya "select" kare, uska lat/long nikalna.

NOTE: Nominatim free/public instance rate-limited hai (~1 req/sec) aur bulk/production
use ke liye apna khud ka self-hosted instance ya paid provider (LocationIQ, Mapbox)
chahiye hoga jab users badhenge. Abhi MVP ke liye ye theek hai.
"""
import httpx
from app.config import NOMINATIM_BASE_URL, NOMINATIM_USER_AGENT, BANGALORE_BBOX
from app.models.schemas import GeocodeSuggestion


async def search_places(query: str, limit: int = 6) -> list[GeocodeSuggestion]:
    """
    User type kare "MG Road" ya "Koramangala" -> ye function candidate places
    return karega (Google Maps autocomplete jaisa).
    """
    south, west, north, east = BANGALORE_BBOX
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit,
        # bounded viewbox se Bangalore ke bahar ke irrelevant results kam aayenge
        "viewbox": f"{west},{north},{east},{south}",
        "bounded": 0,   # 0 = bias only, 1 = hard restrict. Bangalore ke bahar ka
                        # bhi valid ho sakta hai (e.g. user Mysore search kare), isliye bias only.
    }
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{NOMINATIM_BASE_URL}/search", params=params, headers=headers)
        resp.raise_for_status()
        results = resp.json()

    suggestions = []
    for r in results:
        suggestions.append(
            GeocodeSuggestion(
                display_name=r.get("display_name", ""),
                latitude=float(r["lat"]),
                longitude=float(r["lon"]),
                place_type=r.get("type"),
                osm_id=str(r.get("osm_id")) if r.get("osm_id") else None,
            )
        )
    return suggestions


async def reverse_geocode(latitude: float, longitude: float) -> str | None:
    """Lat/long diya -> readable address wapas. Map pe pin drop karke 'ye jagah hai' dikhane ke liye."""
    params = {"lat": latitude, "lon": longitude, "format": "jsonv2"}
    headers = {"User-Agent": NOMINATIM_USER_AGENT}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{NOMINATIM_BASE_URL}/reverse", params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    return data.get("display_name")
