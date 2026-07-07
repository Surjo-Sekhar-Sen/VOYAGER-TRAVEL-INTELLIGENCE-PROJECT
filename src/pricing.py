import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def load_transit_data():
    """
    Loads master structural configs from your data_cache directory.
    Failsafe defaults are active if files are missing or incomplete.
    """
    fares_path = "data_cache/transit_fares.json"
    kia_path = "data_cache/KIA_stops_fare_incomplete.json"
    
    static_fares = {}
    kia_routes = {}
    
    if os.path.exists(fares_path):
        try:
            with open(fares_path, "r", encoding="utf-8") as f:
                static_fares = json.load(f)
        except Exception:
            pass
            
    if os.path.exists(kia_path):
        try:
            with open(kia_path, "r", encoding="utf-8") as f:
                kia_routes = json.load(f)
        except Exception:
            pass
            
    return static_fares, kia_routes

def predict_on_demand_private_fare(distance_km: float, is_peak_hour: int, is_raining: int, transport_mode: str, group_size: int) -> float:
    """
    Supervised Machine Learning Layer: Uses Random Forest Regressor to forecast
    high-variable transport modes pricing structure (On-Demand Cabs, Autos, and Bikes).
    """
    np.random.seed(42)
    n_samples = 1000
    
    sim_dist = np.random.uniform(1.0, 25.0, n_samples)
    sim_peak = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    sim_rain = np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2])
    sim_group = np.random.randint(1, 5, size=n_samples)
    sim_mode = np.random.choice([0, 1, 2], size=n_samples, p=[0.3, 0.4, 0.3])
    
    # Base configuration formula matching dynamic on-demand booking surge indexes
    base_fare = 60 + (sim_dist * 15) + (sim_peak * 35) + (sim_rain * 45)
    for i in range(n_samples):
        if sim_mode[i] == 0:   # Ride-share Bike Option
            base_fare[i] = (15 + (sim_dist[i] * 7) + (sim_peak[i] * 10) + (sim_rain[i] * 15))
        elif sim_mode[i] == 1: # On-Demand Connected Auto
            base_fare[i] = (35 + (sim_dist[i] * 12) + (sim_peak[i] * 20) + (sim_rain[i] * 25))
        elif sim_mode[i] == 2: # App-Based Premium Cab Fleet
            base_fare[i] = (80 + (sim_dist[i] * 20) + (sim_peak[i] * 50) + (sim_rain[i] * 60))
            
    X = pd.DataFrame({
        'distance_km': sim_dist,
        'is_peak_hour': sim_peak,
        'is_raining': sim_rain,
        'mode_encoded': sim_mode,
        'group_size': sim_group
    })
    
    model = RandomForestRegressor(n_estimators=40, random_state=42)
    model.fit(X.values, base_fare)
    
    mode_map = {'online_bike': 0, 'online_auto': 1, 'online_cab': 2}
    encoded_input_mode = mode_map.get(transport_mode, 2)
    
    input_vector = np.array([[distance_km, is_peak_hour, is_raining, encoded_input_mode, group_size]])
    raw_predicted_fare = float(model.predict(input_vector)[0])
    
    # 👥 GROUP SIZE PRICING CONTROL POLICY LOGIC MATRIX
    if transport_mode == 'online_cab':
        # Premium cabs fare is split dynamically among co-passengers group grid
        return max(35.0, raw_predicted_fare / group_size)
    elif transport_mode == 'online_auto':
        # Auto fare remains flat per ride contract regardless of group threshold load up to 3
        return raw_predicted_fare
    else:
        # Bike taxi is completely restricted if team co-passengers limit exceeds solo capacity
        return raw_predicted_fare if group_size == 1 else 0.0

def calculate_bmtc_exact_fixed_fare(distance_km: float, passenger_type: str = "adult", gender: str = "male", has_bus_pass: bool = False, is_ac: bool = False, static_fares: dict = None) -> dict:
    """
    🎫 Concession and Policy Rules Subsystem: Evaluates stage-wise pricing brackets,
    Shakti Concession Scheme, and smart card pass parameters.
    """
    if distance_km < 0.1:
        return {"fare": 0.0, "notes": "Negligible transit corridor distance."}
        
    ptype = passenger_type.lower()
    gender_clean = gender.lower()
    
    # 💳 1. CASHLESS COMMUTE SMART PASS BYPASS STATE
    if has_bus_pass:
        return {
            "fare": 0.0, 
            "notes": f"Fare covered under active BMTC {'AC Vajra' if is_ac else 'Ordinary'} Pass concession."
        }

    if is_ac:
        # 🔵 2. AC VAJRA SYSTEM SCHEMAS
        ac_slabs = static_fares.get("bmtc_ac_vajra_slabs", []) if static_fares else []
        matched_slab = ac_slabs[-1] if ac_slabs else {"adult_fare": 65.0, "child_fare": 35.0, "senior_fare": 50.0}
        
        for slab in ac_slabs:
            if distance_km <= slab["max_km"]:
                matched_slab = slab
                break
                
        if ptype == "child":
            fare = float(matched_slab["child_fare"])
        elif ptype == "senior":
            fare = float(matched_slab["senior_fare"])
        else:
            fare = float(matched_slab["adult_fare"])
            
        return {"fare": fare, "notes": "Standard AC Vajra ticket validation matrix active."}

    else:
        # 🟢 3. NON-AC ORDINARY BUS SYSTEM TIER
        # 👩 SHAKTI CONCESSION SCHEME RULES INTERCEPT OVERRIDE
        if gender_clean == "female":
            return {
                "fare": 0.0, 
                "notes": "FREE Ride under Shakti Concession Scheme! Keep any verified Govt Identity Card ready for terminal check."
            }
            
        ordinary_slabs = static_fares.get("bmtc_ordinary_slabs", []) if static_fares else []
        adult_fare = 32.0 if ordinary_slabs else 32.0 
        
        for slab in ordinary_slabs:
            if distance_km <= slab["max_km"]:
                adult_fare = float(slab["fare"])
                break
                
        if ptype == "child":
            return {"fare": round(adult_fare * 0.5), "notes": "Concession Child Half-Ticket applied."}
        elif ptype == "senior":
            if adult_fare == 6.0: senior_f = 5.0
            elif adult_fare == 12.0: senior_f = 9.0
            elif adult_fare == 18.0: senior_f = 14.0
            elif adult_fare in [23.0, 24.0]: senior_f = 18.0
            elif adult_fare == 25.0: senior_f = 19.0
            elif adult_fare == 26.0: senior_f = 20.0
            elif adult_fare == 28.0: senior_f = 21.0
            else: senior_f = 24.0
            return {"fare": senior_f, "notes": "Senior Citizen Concession pricing applied."}
            
        return {"fare": adult_fare, "notes": "Standard Non-AC Adult ticket."}

def calculate_comprehensive_transit_profile(source_name: str, dest_name: str, distance_km: float, is_peak_hour: int = 0, is_raining: int = 0, passenger_type: str = "adult", gender: str = "male", has_bus_pass: bool = False, group_size: int = 1) -> dict:
    """
    🚀 High-Performance Travel Pricing Gateway: Consolidates predictions across ML networks 
    and configurations layout to serve the multi-criteria TOPSIS selector.
    """
    static_fares, kia_routes = load_transit_data()
    src, dst = source_name.lower(), dest_name.lower()
    ptype = passenger_type.lower()

    # ✈️ SECTOR A: PREMIUM AIRPORT REVENUE BUS ROUTING
    if "airport" in src or "airport" in dst or "kia" in src or "kia" in dst:
        for route_id, route_data in kia_routes.get("vayu_vajra_kia_routes", {}).items():
            for stop in route_data["stops"]:
                stop_clean = stop["stop_name"].lower()
                if (stop_clean in src and "airport" in dst) or (stop_clean in dst and "airport" in src):
                    base_kia_fare = float(stop["fare"])
                    final_kia = (base_kia_fare * 0.5 if ptype == "child" else base_kia_fare) * group_size
                    return {
                        "vayu_vajra_kia": {
                            "fare": final_kia, 
                            "comfort": 5.0, 
                            "type": "Premium Airport AC Coach Service",
                            "notes": "Airport express routing active. Smart passes/Shakti concessions are invalid on KIA corridor lines."
                        }
                    }

    # 🚇 SECTOR B: URBAN RAILWAY NETWORKS SLAB ROUTER (NAMMA METRO)
    metro_base = 60.0 
    metro_slabs = static_fares.get("namma_metro_slabs", []) if static_fares else []
    for slab in metro_slabs:
        if distance_km <= slab["max_km"]:
            metro_base = float(slab["fare"])
            break
    if ptype == "child":
        metro_base = round(metro_base * 0.5, 2)
    total_metro_fare = metro_base * group_size

    # 🚌 SECTOR C: FIXED-ROUTE LOCAL BUS CONCESSIONS CHANNELS
    ordinary_metrics = calculate_bmtc_exact_fixed_fare(distance_km, ptype, gender, has_bus_pass, is_ac=False, static_fares=static_fares)
    ac_metrics = calculate_bmtc_exact_fixed_fare(distance_km, ptype, gender, has_bus_pass, is_ac=True, static_fares=static_fares)

    # 🚗 SECTOR D: ON-DEMAND PRIVATE TRANSPORT FORECAST LOOPS (RANDOM FOREST REGRESSOR)
    cab_total = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_cab', group_size)
    auto_total = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_auto', group_size)
    bike_total = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_bike', group_size) if group_size == 1 else 0.0

    return {
        "namma_metro": {
            "fare": 30.0 * group_size, 
            "time": distance_km * 2.0, 
            "traffic_delay": 0.0, # Metro has no traffic delay
            "comfort": 4.5, 
            "type": "Rapid Transit", 
            "notes": "BMRCL protocols active."
        },
        "ordinary_bus": {
            "fare": 20.0 * group_size, 
            "time": distance_km * 4.0, 
            "traffic_delay": 25.0, 
            "comfort": 2.0, 
            "type": "Ordinary Bus", 
            "notes": "High crowd."
        },
        "ac_vajra_bus": {
            "fare": 40.0 * group_size, 
            "time": distance_km * 3.5, 
            "traffic_delay": 22.0, 
            "comfort": 4.0, 
            "type": "AC Vajra", 
            "notes": "Weather shielded."
        },
        "online_cab": {
            "fare": round(cab_total, 2), 
            "time": distance_km * 1.8, 
            "traffic_delay": 18.0, 
            "comfort": 4.8, 
            "type": "Premium Cab", 
            "notes": "Dynamic predictive pricing."
        },
        "online_auto": {
            "fare": round(auto_total, 2), 
            "time": distance_km * 2.5, 
            "traffic_delay": 15.0, 
            "comfort": 2.5, 
            "type": "Auto Rickshaw", 
            "notes": "Quick micro-mobility."
        }
    }