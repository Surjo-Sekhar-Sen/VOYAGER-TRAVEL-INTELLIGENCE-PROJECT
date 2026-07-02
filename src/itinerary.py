from src.map_gateway import get_location_coordinates, compute_haversine_distance
from src.pricing import predict_transit_fare
from src.decision import run_topsis_optimizer
import numpy as np

def fetch_historical_hotspots_data(landmark: str):
    """
    Simulation of Crowdsourced/Historical Data Mining Layer.
    Returns highly rated local food, stay, and extra activity hubs near a landmark.
    """
    recommendations_db = {
        "Mysore Palace": {
            "food": ["Hotel RRR (Famous Mutton Biryani) - ₹400/person", "Mylari Hotel (Legendary Benne Dosa) - ₹150/person"],
            "stay": ["Radisson Blu Plaza", "Hotel Mayura Hoysala (KSTDC)"],
            "nearby_explore": ["Chamundi Hills (Great view around 5 PM)", "Devaraja Market (Local Heritage Walk)"]
        },
        "Mysore Zoo": {
            "food": ["Kamat Madhuban (North Karnataka Meals) - ₹200/person"],
            "stay": ["Grand Mercure Mysore"],
            "nearby_explore": ["Karanji Lake (Boating & Bird Watching)"]
        }
    }
    # Fallback default framework if landmark isn't directly cached
    return recommendations_db.get(landmark, {
        "food": ["Local Regional Veg Meals Hub - ₹150/person"],
        "stay": ["Verified Premium Homestay Layer"],
        "nearby_explore": ["Local Scenic Viewpoint"]
    })

def generate_interactive_trip_canvas(user_selected_hotspots: list, budget_limit: float, time_of_day: str, is_raining: int, group_size: int):
    """
    Macro Iteration Engine with Contextual 8-Criteria Micro-Routing & Local Recommendations Node.
    """
    canvas_itinerary = []
    
    # Modes loop to evaluate options explicitly (Public, Local, and Online bookings)
    modes = ['public_bus', 'shared_auto', 'online_cab']
    
    for i in range(len(user_selected_hotspots) - 1):
        current_stop = user_selected_hotspots[i]
        next_stop = user_selected_hotspots[i+1]
        
        # 1. Fetch Spatial Metrics
        coord_curr = get_location_coordinates(current_stop)
        coord_next = get_location_coordinates(next_stop)
        distance = compute_haversine_distance(coord_curr['lat'], coord_curr['lng'], coord_next['lat'], coord_next['lng'])
        if distance == 0: 
            distance = 3.2 # Intra-city transit baseline approximation
        
        # 2. Extract Contextual Historical Recommendations Data Logs
        local_insights = fetch_historical_hotspots_data(current_stop)
        
        # 3. Process Live Environmental Data & PPT Criteria Simulation
        current_sim_peak = 1 if time_of_day == "night" else 0
        
        alternatives_pool = []
        path_names = []
        
        # 4. Inject FEATURE 1 Pipeline over 8 PPT Criteria
        # Matrix Columns: [Cost, Time, Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
        for mode in modes:
            # Criteria 2: Cost predicted via upgraded Random Forest Engine
            cost = predict_transit_fare(distance, current_sim_peak, is_raining, mode, group_size)
            
            # Criteria 1, 4, 5, 6, 7, 8 adjustments based on PPT parameters
            if mode == 'public_bus':
                time_taken = distance * 4.0        # Criteria 1: Time duration
                walking_dist = 0.8                 # Criteria 6: Walking distance overhead
                safety = 4.5                       # Criteria 8: Basic path safety
                availability = 5.0                 # Criteria 5: Available transport index
                comfort = 2.0                      # Criteria 7: Group size adaptation index
                traffic_delay = 25.0               # Criteria 4: Traffic/Crowd delay matrix
            elif mode == 'shared_auto':
                time_taken = distance * 2.5
                walking_dist = 0.3
                safety = 3.5
                availability = 4.0
                comfort = 3.0
                traffic_delay = 15.0
            else: # online_cab booking matrix
                time_taken = distance * 1.8
                walking_dist = 0.05
                safety = 4.9
                availability = 2.5 if distance > 15.0 else 4.5 # Outstation cab availability drops
                comfort = 5.0
                traffic_delay = 18.0
                
            # Night context risk parameters modulation
            if time_of_day == "night":
                traffic_delay -= 10.0 # Clear night roads
                if mode != 'online_cab':
                    safety -= 1.5      # Night safety drops for non-bookings
                    availability -= 2.0
            
            # Criteria 3: Weather Situation Risk
            weather_risk = 4.0 if is_raining == 1 else 1.0
            
            alternatives_pool.append([cost, time_taken, traffic_delay, walking_dist, safety, weather_risk, availability, comfort])
            path_names.append(f"Take {mode.upper()} to {next_stop}")

        # Benefit flags layout for 8 Columns: Lower is better for first 4, Higher is better for last 4
        benefit_criteria = [False, False, False, False, True, True, True, True]
        
        # Multi-Objective Weights Allocation Based on Real-Time Environmental Status
        if time_of_day == "night":
            # Safety and comfort are prioritized heavily during night shifts
            weights = np.array([0.10, 0.10, 0.05, 0.05, 0.40, 0.10, 0.10, 0.10])
        elif is_raining == 1:
            # Weather risk and lower walking requirements prioritized
            weights = np.array([0.15, 0.15, 0.10, 0.30, 0.10, 0.10, 0.05, 0.05])
        else:
            # Balanced standard profile
            weights = np.array([0.25, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10])

        # Execute Upgraded TOPSIS Core Hook
        optimized_routes = run_topsis_optimizer(np.array(alternatives_pool), weights, benefit_criteria, path_names)
        
        # Assemble nested node grid structure with 100% preservation of original blueprint
        node_block = {
            "current_location_hub": current_stop,
            "next_planned_target": next_stop,
            "historical_crowd_insights": {
                "highly_frequented_food_spots": local_insights["food"],
                "recommended_stay_layers": local_insights["stay"],
                "optional_side_activities": local_insights["nearby_explore"]
            },
            "feature_1_transit_activation": {
                "distance_gap": f"{distance:.2f} KM",
                "recommended_transit_path": optimized_routes[0]['route_name'],
                "predicted_base_fare": f"₹{optimized_routes[0]['raw_metrics_snapshot'][0]:.2f}",
                "walking_overhead": f"{optimized_routes[0]['raw_metrics_snapshot'][3]:.2f} KM",
                "full_alternatives_ranking": optimized_routes
            }
        }
        canvas_itinerary.append(node_block)
        
    return {
        "budget_constraint_allocated": f"₹{budget_limit:.2f}",
        "itinerary_timeline_nodes": canvas_itinerary
    }