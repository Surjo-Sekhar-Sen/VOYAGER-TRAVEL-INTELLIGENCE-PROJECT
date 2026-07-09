"""
Saare request/response shapes yaha define hai. Frontend inhi shapes ke JSON
expect karega — isko as-is treat karo as the "API contract".
"""
from typing import Optional
from pydantic import BaseModel, Field


class GeocodeSuggestion(BaseModel):
    """Ek autocomplete suggestion — jab user place type kar raha ho."""
    display_name: str
    latitude: float
    longitude: float
    place_type: Optional[str] = None   # e.g. "restaurant", "suburb", "road"
    osm_id: Optional[str] = None


class GeocodeResponse(BaseModel):
    query: str
    suggestions: list[GeocodeSuggestion]


class NearbyPlace(BaseModel):
    """Ek nearby POI (ATM, mall, etc.) — verification ke baad ka final result."""
    name: str
    latitude: float
    longitude: float
    category: str
    distance_km: float
    osm_id: Optional[str] = None
    tags: dict = Field(default_factory=dict)

    # LLM verification ke baad add hote hai:
    confidence_score: float = 0.0        # 0.0 - 1.0
    verification_note: str = ""          # LLM ne kyu ye score diya (1 line)
    is_recommended: bool = False         # bada/glow wala pin frontend pe


class NearbyRequest(BaseModel):
    latitude: float
    longitude: float
    category: str                        # e.g. "atm", "mall", "petrol pump"
    radius_km: float = 2.0


class NearbyResponse(BaseModel):
    category: str
    origin: dict                         # {"latitude":.., "longitude":..}
    recommended: list[NearbyPlace]
    others: list[NearbyPlace]
    summary: str                         # LLM ka 1-2 line plain-language summary


class KiaFareStop(BaseModel):
    stop_name: str
    fare: float


class KiaRouteInfo(BaseModel):
    route_code: str
    route_info: str
    stops: list[KiaFareStop]


class KiaFareLookupResponse(BaseModel):
    query_stop: str
    matches: list[dict]   # [{route_code, route_info, fare}]
