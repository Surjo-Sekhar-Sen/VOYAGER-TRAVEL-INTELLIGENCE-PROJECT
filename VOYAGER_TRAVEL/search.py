"""
Feature 1 ke saare HTTP endpoints yahan hai. Frontend inhi ko call karega.
"""
from fastapi import APIRouter, HTTPException, Query

from app.agents import search_agent
from app.services import geocode_service, fare_service

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
async def search(
    q: str = Query(..., description="User ka search text, e.g. 'Koramangala' ya 'ATMs near me'"),
    latitude: float | None = Query(None, description="User ka current lat (nearby search ke liye zaroori)"),
    longitude: float | None = Query(None, description="User ka current lon (nearby search ke liye zaroori)"),
):
    """
    Feature 1 ka main endpoint. Intent khud detect ho jayega:
    - direct place -> autocomplete suggestions
    - "X near me" / category keyword -> verified nearby POIs
    """
    try:
        result = await search_agent.handle_search(q, latitude, longitude)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reverse-geocode")
async def reverse_geocode(latitude: float, longitude: float):
    """User map pe pin drag kare -> ye batayega vaha ka address kya hai."""
    address = await geocode_service.reverse_geocode(latitude, longitude)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found for this location.")
    return {"latitude": latitude, "longitude": longitude, "address": address}


@router.get("/fare/kia")
async def kia_fare_lookup(stop: str = Query(..., description="Bus stop ka naam, e.g. 'Hebbala'")):
    """KIA airport bus (Vayuvajra) fare lookup by stop name."""
    matches = fare_service.find_fare_by_stop(stop)
    if not matches:
        raise HTTPException(status_code=404, detail=f"No KIA route found passing through '{stop}'.")
    return {"query_stop": stop, "matches": matches}


@router.get("/fare/kia/routes")
async def kia_all_routes():
    """Saare available KIA route codes ki list (debugging/exploration ke liye)."""
    return {"routes": fare_service.list_all_routes()}
