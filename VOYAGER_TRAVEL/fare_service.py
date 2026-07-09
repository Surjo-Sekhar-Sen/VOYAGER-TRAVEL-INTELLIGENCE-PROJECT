"""
KIA (airport) Vayuvajra bus fare lookup — pichli baar clean kiya hua dataset use kar raha hai.
Simple in-memory load hai, DB ki zaroorat nahi (data chhota + static hai).
"""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "kia_routes_fare_full.json"

_cache: dict | None = None


def _load() -> dict:
    global _cache
    if _cache is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _cache = json.load(f)["vayu_vajra_kia_routes"]
    return _cache


def find_fare_by_stop(stop_name: str) -> list[dict]:
    """
    User ek stop ka naam de (jaise "Hebbala") -> saare routes jo us stop se
    guzarte hai, unka fare wapas karo. Case-insensitive partial match.
    """
    routes = _load()
    query = stop_name.strip().lower()
    matches = []
    for route_code, info in routes.items():
        for stop in info["stops"]:
            if query in stop["stop_name"].lower():
                matches.append({
                    "route_code": route_code,
                    "route_info": info["route_info"],
                    "stop_name": stop["stop_name"],
                    "fare": stop["fare"],
                })
    return matches


def get_route(route_code: str) -> dict | None:
    routes = _load()
    return routes.get(route_code)


def list_all_routes() -> list[str]:
    return list(_load().keys())
