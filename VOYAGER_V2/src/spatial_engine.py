import requests
from geopy.distance import geodesic
from src.data_processor import processor
from src.agent_core import agent
from src.decision import TopsisEngine

class SpatialEngine:
    def __init__(self):
        self.processor = processor
        self.agent = agent
        self.topsis = TopsisEngine()

    # NEW: Overpass API for Google-Maps style details
    def fetch_overpass_details(self, lat, lon, radius=3000):
        overpass_url = "http://overpass-api.de/api/interpreter"
        # Hotel/Lodging ke liye query
        query = f"""
        [out:json][timeout:25];
        (node["tourism"="hotel"](around:{radius},{lat},{lon});
         node["tourism"="guest_house"](around:{radius},{lat},{lon}););
        out body;
        """
        try:
            response = requests.get(overpass_url, params={'data': query})
            return response.json().get('elements', [])
        except:
            return []

    # Nominatim (Location only)
    def fetch_real_places(self, lat, lon, query, radius_km=3.0):
        # 1. Check if it's a 'stay' category for Overpass
        if any(word in query.lower() for word in ['hotel', 'stay', 'lodge', 'resort']):
            overpass_data = self.fetch_overpass_details(lat, lon, radius=radius_km*1000)
            if overpass_data:
                return [{"name": r['tags'].get('name', 'Hotel'), "lat": r['lat'], "lon": r['lon'], "is_stay": True} for r in overpass_data]

        # 2. Default Nominatim Search
        keyword_map = {
            "temple": "hindu_temple", "mandir": "hindu_temple", "masjid": "mosque", 
            "mosque": "mosque", "church": "church", "gurudwara": "gurudwara",
            "hospital": "hospital", "clinic": "clinic", "pharmacy": "pharmacy", 
            "bank": "bank", "atm": "atm"
        }
        search_term = keyword_map.get(query.lower().strip(), query.lower().strip())
        
        url = "https://nominatim.openstreetmap.org/search"
        degree_offset = radius_km / 111.0
        
        params = {'q': search_term, 'format': 'json', 'lat': lat, 'lon': lon, 'bounded': 1, 'viewbox': f"{lon-degree_offset},{lat-degree_offset},{lon+degree_offset},{lat+degree_offset}"}
        headers = {'User-Agent': 'Voyager-Travel-App/1.0'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return [{"name": r.get('display_name', 'Location').split(',')[0], "lat": float(r.get('lat')), "lon": float(r.get('lon')), "is_stay": False} for r in response.json()]
            return []
        except:
            return []

    def search_specific(self, query):
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': f"{query}, India", 'format': 'json', 'limit': 10}
        headers = {'User-Agent': 'Voyager-Travel-App/1.0'}
        response = requests.get(url, params=params, headers=headers)
        return [{"name": r.get('display_name'), "lat": float(r.get('lat')), "lon": float(r.get('lon'))} for r in response.json()]

    def get_nearby_results(self, lat, lon, search_query, radius):
        real_spots = self.fetch_real_places(lat, lon, search_query, radius_km=float(radius))
        if not real_spots: return []
        
        # Scored results logic
        scored_results = []
        for spot in real_spots:
            dist = geodesic((lat, lon), (spot["lat"], spot["lon"])).km
            scored_results.append({
                **spot,
                "distance": round(dist, 2),
                "reliability_score": 7.0 # AI fallback
            })
        return self.topsis.rank_options(scored_results, weights=[0.5, 0.5])

spatial_engine = SpatialEngine()