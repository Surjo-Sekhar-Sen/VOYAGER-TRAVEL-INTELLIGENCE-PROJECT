"""
Search agent — Feature 1 ka "brain". Ye decide karta hai ki user ka query
seedha "place search" hai (e.g. "Koramangala") ya "nearby category" hai
(e.g. "ATMs near me", "petrol pumps nearby").

Abhi ke liye simple rule-based intent detection hai (keyword check). Baad me
isko LLM-based intent classification se replace/upgrade kar sakte ho agar
zyada natural queries handle karni ho (e.g. "kya paas me koi achha cafe hai").
"""
from app.services import geocode_service, nearby_service, llm_verify_service
from app.config import CATEGORY_TO_OSM_TAGS

NEARBY_KEYWORDS = ["near", "nearby", "near me", "paas", "aaspaas", "close to me"]


def detect_category(query: str) -> str | None:
    """Query me se koi known category keyword milta hai kya, check karo."""
    q = query.lower()
    for category in CATEGORY_TO_OSM_TAGS:
        if category in q:
            return category
    return None


def is_nearby_query(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in NEARBY_KEYWORDS) or detect_category(query) is not None


async def handle_search(query: str, latitude: float | None, longitude: float | None):
    """
    Main entrypoint jo router call karega.
    Return shape do types me se ek hoga:
      {"type": "place", "suggestions": [...]}                 -> seedha place search
      {"type": "nearby", "recommended": [...], "others": [...], "summary": "..."}
    """
    if is_nearby_query(query):
        if latitude is None or longitude is None:
            raise ValueError("Nearby search ke liye user ka current location (latitude/longitude) chahiye.")

        category = detect_category(query)
        if not category:
            raise ValueError(
                f"Query se category samajh nahi aayi. Supported categories: "
                f"{list(CATEGORY_TO_OSM_TAGS.keys())}"
            )

        raw_places = await nearby_service.find_nearby(latitude, longitude, category)
        ranked_places, summary = await llm_verify_service.verify_and_rank(raw_places, category)

        recommended = [p for p in ranked_places if p["is_recommended"]]
        others = [p for p in ranked_places if not p["is_recommended"]]

        return {
            "type": "nearby",
            "category": category,
            "origin": {"latitude": latitude, "longitude": longitude},
            "recommended": recommended,
            "others": others,
            "summary": summary,
        }

    # Direct place search
    suggestions = await geocode_service.search_places(query)
    return {"type": "place", "query": query, "suggestions": suggestions}
