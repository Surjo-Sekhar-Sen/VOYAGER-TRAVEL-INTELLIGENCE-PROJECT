import math
import os
import numpy as np
import pandas as pd
from google import genai
from google.genai import types
from src.decision import run_topsis_optimizer
# Direct dynamic reference to your newly finalized matrix rules
from src.pricing import calculate_comprehensive_transit_profile

api_key = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FALLBACK_IF_NOT_SET")
client = genai.Client(api_key=api_key)

def get_location_coordinates(landmark: str):
    geo_database = {
        "hotel hub core": {"lat": 12.2900, "lng": 76.6300},
        "mysore palace sector": {"lat": 12.3051, "lng": 76.6551},
        "mysore zoo terminal": {"lat": 12.3020, "lng": 76.6650},
        "mysore palace": {"lat": 12.3051, "lng": 76.6551},
        "mysore zoo": {"lat": 12.3020, "lng": 76.6650},
        "default": {"lat": 12.2950, "lng": 76.6400}
    }
    key = landmark.lower().strip()
    return geo_database.get(key, geo_database["default"])

def extract_raw_crowdsourced_reviews(landmark: str) -> str:
    raw_reviews_dump = {
        "mysore palace": "Beautiful heritage walk but they don't allow shoes inside, safe shoe counter available near gate 2. Long ticket queues during day time! Better to pay digitally online beforehand. Highly safe area even around late evening hours. Auto drivers can bargain heavily on price. UPI worked fine everywhere but better keep some cash handy for local street vendor maps.",
        "mysore zoo": "Lot of walking required inside the transit loop. Electric buggies available but hard to book. Strict rules: Plastic bottles are strictly banned inside to protect animals! They check bags. Kamat meals nearby is good, but parking gets packed on rainy days."
    }
    clean_key = landmark.lower().strip()
    for key, text in raw_reviews_dump.items():
        if key in clean_key:
            return text
    return "Standard local transit spot. Good connectivity. Local shops accept digital UPI payments seamlessly."

def run_agentic_review_synthesizer(landmark: str):
    raw_context = extract_raw_crowdsourced_reviews(landmark)
    
    numeric_traffic_modifier = 1.0
    numeric_comfort_penalty = 0.0
    
    if "queues" in raw_context.lower() or "packed" in raw_context.lower():
        numeric_traffic_modifier = 1.4  
    if "walking" in raw_context.lower():
        numeric_comfort_penalty = 1.5   
        
    system_instruction = (
        "You are the Agentic Travel Intelligence Assistant for VOYAGER. "
        "Analyze the raw crowdsourced reviews of the landmark and summarize EXACTLY 3 points "
        "(maximum 12 words per point) strictly covering: "
        "1. Verified Payment Mode, 2. Local Compliance Rules, 3. Crowd Density/Waiting Alert. "
        "Do not invent facts or output generic placeholder texts. Be highly specific."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Landmark Hub: {landmark}\nScraped Data Feed: {raw_context}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        ai_brief = response.text.strip()
    except Exception:
        ai_brief = "• Payment: UPI/Cash active.\n• Rules: Standard entry checks.\n• Alert: Normal flow stable."

    return {
        "ai_brief": ai_brief,
        "traffic_modifier": numeric_traffic_modifier,
        "comfort_penalty": numeric_comfort_penalty
    }

def compute_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def fetch_sumo_traffic_delay_multiplier():
    log_path = "data_cache/traffic_logs.csv"
    if not os.path.exists(log_path): return 1.0
    try:
        df = pd.read_csv(log_path)
        if len(df) > 0:
            return float(1.0 + (df["congestion_overhead"].mean() * 1.5))
    except Exception: pass
    return 1.0

# =====================================================================
# UPGRADED TRIP TIMELINE CANVAS ENGINE (INTEGRATED WITH MASTER CHANNELS)
# =====================================================================
def generate_interactive_trip_canvas(user_selected_hotspots: list, budget_limit: float, time_of_day: str, is_raining: int, group_size: int, passenger_type: str = "adult", gender: str = "male", has_bus_pass: bool = False):
    canvas_itinerary = []
    
    sumo_multiplier = fetch_sumo_traffic_delay_multiplier()
    
    for i in range(len(user_selected_hotspots) - 1):
        current_stop = user_selected_hotspots[i]
        next_stop = user_selected_hotspots[i+1]
        
        coord_curr = get_location_coordinates(current_stop)
        coord_next = get_location_coordinates(next_stop)
        distance = compute_haversine_distance(coord_curr['lat'], coord_curr['lng'], coord_next['lat'], coord_next['lng'])
        if distance == 0: distance = 3.2 
        
        current_sim_peak = 1 if time_of_day == "night" else 0
        agentic_intel = run_agentic_review_synthesizer(current_stop)
        
        # 🔗 SYNC STEP: Dynamic Profile loading straight from pricing.py rules engine
        profile_matrix = calculate_comprehensive_transit_profile(
            source_name=current_stop,
            dest_name=next_stop,
            distance_km=distance,
            is_peak_hour=current_sim_peak,
            is_raining=is_raining,
            passenger_type=passenger_type,
            gender=gender,
            has_bus_pass=has_bus_pass,
            group_size=group_size
        )
        
        alternatives_pool = []
        path_names = []
        notes_mapping = {}
        
        # Expand mapping tracking parameters for all 6 core available modes
        for mode, data in profile_matrix.items():
            cost = data["fare"]
            comfort = data["comfort"]
            notes_mapping[mode.upper()] = data.get("notes", "")
            
            # Static performance vector mapping for multidimensional criteria evaluation
            if mode == 'namma_metro':
                time_taken = distance * 2.0; walking_dist = 0.5; safety = 4.9; availability = 4.8; traffic_delay = 5.0
            elif mode == 'ordinary_bus':
                time_taken = distance * 4.0; walking_dist = 0.8; safety = 4.2; availability = 5.0; traffic_delay = 25.0
            elif mode == 'ac_vajra_bus':
                time_taken = distance * 3.5; walking_dist = 0.7; safety = 4.6; availability = 4.2; traffic_delay = 22.0
            elif mode == 'vayu_vajra_kia':
                time_taken = distance * 2.2; walking_dist = 0.3; safety = 4.9; availability = 4.0; traffic_delay = 15.0
            elif mode == 'online_auto':
                time_taken = distance * 2.5; walking_dist = 0.1; safety = 3.5; availability = 4.0; traffic_delay = 15.0
            else: # online_cab
                time_taken = distance * 1.8; walking_dist = 0.05; safety = 4.8; availability = 4.5; traffic_delay = 18.0
                
            # Env conditions parameter modifiers
            if time_of_day == "night":
                traffic_delay = max(2.0, traffic_delay - 10.0)
                if mode in ['ordinary_bus', 'online_auto']:
                    safety -= 1.2
                    availability -= 1.5
                    
            traffic_delay = traffic_delay * sumo_multiplier * agentic_intel["traffic_modifier"]
            comfort = max(1.0, comfort - agentic_intel["comfort_penalty"])
            weather_risk = 4.0 if is_raining == 1 else 1.0
            
            alternatives_pool.append([cost, time_taken, traffic_delay, walking_dist, safety, weather_risk, availability, comfort])
            path_names.append(mode.upper())

        # Benefit filters index (True means Maximize, False means Minimize)
        benefit_criteria = [False, False, False, False, True, False, True, True]
        
        # Weights tuning matrix
        if time_of_day == "night":
            weights = np.array([0.10, 0.10, 0.05, 0.05, 0.40, 0.10, 0.10, 0.10])
        elif is_raining == 1:
            weights = np.array([0.15, 0.15, 0.10, 0.30, 0.10, 0.10, 0.05, 0.05])
        else:
            weights = np.array([0.25, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10])

        all_ranked_alternatives = run_topsis_optimizer(np.array(alternatives_pool), weights, benefit_criteria, path_names)
        
        # 🤖 GENERATING SMART COMPARATIVE SUGGESTIONS FOR THE UNIFIED WEB VIEW
        smart_suggestions_list = []
        for rank_idx, item in enumerate(all_ranked_alternatives):
            mode_name = item['route_name']
            fare_est = item['raw_metrics_snapshot'][0]
            
            custom_note = notes_mapping.get(mode_name, "")
            note_str = f" ({custom_note})" if custom_note else ""
            
            if mode_name == "NAMMA_METRO":
                desc = f"Rank #{rank_idx+1}: Metro Grid System (₹{fare_est:.1f}). Speed high hogi, traffic delays zero honge.{note_str}"
            elif mode_name == "ORDINARY_BUS":
                desc = f"Rank #{rank_idx+1}: Non-AC Bus Option (₹{fare_est:.1f}). High crowd delay possible hai.{note_str}"
            elif mode_name == "AC_VAJRA_BUS":
                desc = f"Rank #{rank_idx+1}: AC Vajra Grid (₹{fare_est:.1f}). Premium seating with standard comfort.{note_str}"
            elif mode_name == "VAYU_VAJRA_KIA":
                desc = f"Rank #{rank_idx+1}: Premium Airport Shuttles (₹{fare_est:.1f}). Direct airport connectivity execution.{note_str}"
            elif mode_name == "ONLINE_AUTO":
                desc = f"Rank #{rank_idx+1}: Digital Ola/Uber Auto (₹{fare_est:.1f}). Micro-mobility scaling operations."
            else:
                desc = f"Rank #{rank_idx+1}: Private Cab Split (₹{fare_est:.1f}). Premium luxury safe weather shielding."
                
            smart_suggestions_list.append(desc)

        node_block = {
            "current_location_hub": current_stop,
            "next_planned_target": next_stop,
            "agentic_ai_layer": {
                "source_verification": "CONNECTED (Google-GenAI Pipeline Active)",
                "live_assistant_brief": agentic_intel["ai_brief"]
            },
            "transit_recommendations_pool": {
                "best_recommended_choice": all_ranked_alternatives[0]['route_name'],
                "full_ranked_alternatives_list": all_ranked_alternatives,
                "assistant_comparative_suggestions": smart_suggestions_list
            }
        }
        canvas_itinerary.append(node_block)
        
    return {
        "budget_constraint_allocated": f"₹{budget_limit:.2f}",
        "itinerary_timeline_nodes": canvas_itinerary
    }