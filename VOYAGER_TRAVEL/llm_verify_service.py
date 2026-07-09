"""
LLM verification/ranking service — ye wahi "agentic" part hai jo tumne bataya tha:
raw OSM POIs le kar, unke tags dekh kar decide karta hai ki konsi jagah
"recommend karne layak" hai aur konsi "shaky/unreliable" hai.

Reviews/JustDial live scrape nahi kar rahe (paid + ToS issue), isliye signal
yaha OSM ke tags se aata hai:
  - disused:*, was:*, abandoned:* tags -> jagah band ho chuki
  - name missing / generic -> data quality low
  - opening_hours missing -> uncertain
  - fully tagged + name present -> zyada trustworthy

Jab tum future me Google Places API key add karoge, isi function ke andar
rating/review_count bhi tags dict me daal ke pass kar dena — LLM prompt already
generic hai, extra fields ko bhi consider kar lega.
"""
import json
import httpx
from app.config import GEMINI_API_KEY, GEMINI_API_URL

SYSTEM_INSTRUCTION = """You are a location-verification assistant for a Bangalore \
navigation app. You will receive a list of OpenStreetMap POIs (candidate places) \
near a user's location, each with raw tags. Your job: decide which ones are \
genuinely likely to exist and be usable right now, versus ones that look \
unreliable, closed, or low-quality data.

Rules:
- Base your judgement ONLY on the tags/fields given (name, opening_hours, \
disused/was/abandoned prefixes, operator, brand, etc.) plus general knowledge \
of what makes OSM data trustworthy. Do not invent facts you were not given.
- A missing name, or tags starting with "disused:"/"was:"/"abandoned:" -> low confidence.
- A place with a proper name, brand/operator, and no disused markers -> high confidence.
- confidence_score is a float 0.0 to 1.0.
- is_recommended = true only for confidence_score >= 0.6.
- verification_note: ONE short plain sentence, in simple language, no jargon, \
explaining the confidence (this will be user-facing).

Return ONLY valid JSON, no markdown, no preamble, matching exactly this shape:
{
  "results": [
    {"osm_id": "<same osm_id as input>", "confidence_score": 0.0, "is_recommended": false, "verification_note": "..."}
  ],
  "summary": "one short plain-language sentence summarizing what was found overall"
}
"""


async def verify_and_rank(places: list[dict], category: str) -> tuple[list[dict], str]:
    """
    places: raw list from nearby_service.find_nearby()
    Returns: (places with confidence_score/is_recommended/verification_note added, summary text)
    """
    if not GEMINI_API_KEY:
        # API key nahi hai to fail-open: sabko medium confidence de do, app crash na ho.
        for p in places:
            p["confidence_score"] = 0.5
            p["is_recommended"] = False
            p["verification_note"] = "Verification skipped (no LLM API key configured)."
        return places, "LLM verification is not configured yet."

    if not places:
        return [], f"No {category} found nearby."

    compact_places = [
        {"osm_id": p["osm_id"], "name": p["name"], "distance_km": p["distance_km"], "tags": p["tags"]}
        for p in places
    ]

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{
            "parts": [{
                "text": f"Category searched: {category}\nCandidates JSON:\n{json.dumps(compact_places, ensure_ascii=False)}"
            }]
        }],
        "generationConfig": {"response_mime_type": "application/json"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
        )
        resp.raise_for_status()
        raw = resp.json()

    try:
        text = raw["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        # LLM response garbled ho gaya -> fail-open, crash mat karo
        for p in places:
            p["confidence_score"] = 0.5
            p["is_recommended"] = False
            p["verification_note"] = "Could not verify this place right now."
        return places, f"Verification had an issue ({e}); showing unranked results."

    score_by_id = {r["osm_id"]: r for r in parsed.get("results", [])}
    for p in places:
        r = score_by_id.get(p["osm_id"])
        if r:
            p["confidence_score"] = float(r.get("confidence_score", 0.5))
            p["is_recommended"] = bool(r.get("is_recommended", False))
            p["verification_note"] = r.get("verification_note", "")
        else:
            p["confidence_score"] = 0.5
            p["is_recommended"] = False
            p["verification_note"] = "Not evaluated."

    places.sort(key=lambda p: p["confidence_score"], reverse=True)
    return places, parsed.get("summary", "")
