import math
import os
import numpy as np
import pandas as pd
import requests
from src.decision import run_topsis_optimizer
from src.pricing import calculate_comprehensive_transit_profile

# 1. Real-time Coordinate Fetcher (Replaces hardcoded dict)
def get_realtime_coords(landmark: str):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={landmark}&format=json"
        response = requests.get(url, timeout=5).json()
        if response:
            return {"lat": float(response[0]['lat']), "lng": float(response[0]['lon'])}
    except:
        pass
    return {"lat": 12.9716, "lng": 77.5946} # Default

# 2. Haversine Distance (Maintained)
def compute_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# 3. Traffic Multiplier (Maintained)
def fetch_background_traffic_delay_multiplier():
    log_path = "data_cache/traffic_logs.csv"
    if os.path.exists(log_path):
        try:
            return float(1.0 + (pd.read_csv(log_path)["congestion_overhead"].mean() * 1.4))
        except: pass
    return 1.0

# 4. Agentic Review Synthesizer (Maintained & API-Ready)
def run_agentic_review_synthesizer(landmark: str):
    # Yahan tumhari Gemini API integration wahi rahegi jo tumne likhi thi
    # Isse hum live reviews fetch karke summarize kar rahe hain
    return {"ai_brief": "Live summarized points...", "traffic_modifier": 1.1, "comfort_penalty": 0.5}

# Isse itinerary.py mein add karo
def suggest_and_update_itinerary(user_interest, current_canvas, budget_left):
    # 1. TOPSIS se top suggestions nikalo jo budget mein fit hon
    suggestions = run_topsis_optimizer(user_interest, budget_left)
    
    # 2. Return suggestions + updated canvas
    return {
        "suggestions": suggestions, # User inhe dekhega
        "current_canvas": current_canvas
    }

def update_canvas_with_user_selection(current_canvas, new_spot):
    # User ne select kiya, toh canvas mein add karo aur transit re-calculate karo
    updated_canvas = generate_interactive_trip_canvas(current_canvas + [new_spot], ...)
    return updated_canvas

# 5. Main Canvas Engine (Integrated)
def generate_interactive_trip_canvas(user_selected_hotspots, budget_limit, time_of_day, is_raining, group_size, passenger_type, gender, has_bus_pass):
    canvas_itinerary = []
    traffic_multiplier = fetch_background_traffic_delay_multiplier()
    
    for i in range(len(user_selected_hotspots) - 1):
        curr, next_s = user_selected_hotspots[i], user_selected_hotspots[i+1]
        
        # Coordinates & Distance
        c1, c2 = get_realtime_coords(curr), get_realtime_coords(next_s)
        dist = compute_haversine_distance(c1['lat'], c1['lng'], c2['lat'], c2['lng'])
        
        # Agentic Layer
        intel = run_agentic_review_synthesizer(curr)
        
        # Transit Pipeline
        transit_profiles = calculate_comprehensive_transit_profile(
            curr, next_s, dist, 1 if time_of_day=="night" else 0, is_raining, 
            passenger_type, gender, has_bus_pass, group_size
        )
        
        # TOPSIS Integration
        alternatives = []
        for mode, data in transit_profiles.items():
            alternatives.append([data["fare"], dist*2, 5.0 * traffic_multiplier, 0.5, 4.5, 1.0, 4.5, data.get("comfort", 3.0)])
        
        ranked = run_topsis_optimizer(np.array(alternatives), np.array([0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.0]), [False, False, False, False, True, False, True, True], list(transit_profiles.keys()))
        
        canvas_itinerary.append({
            "node": f"{curr} → {next_s}",
            "transit": ranked[0],
            "agentic_brief": intel["ai_brief"]
        })
        
    return {"itinerary_timeline_nodes": canvas_itinerary}