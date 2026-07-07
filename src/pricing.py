import numpy as np
import pandas as pd
import json
import os
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
        with open(fares_path, "r") as f:
            static_fares = json.load(f)
            
    if os.path.exists(kia_path):
        with open(kia_path, "r") as f:
            kia_routes = json.load(f)
            
    return static_fares, kia_routes

def predict_on_demand_private_fare(distance_km: float, is_peak_hour: int, is_raining: int, transport_mode: str, group_size: int) -> float:
    """
    🧠 Your Upgraded Random Forest Core Engine:
    Handles predictions for private high-variable parameters like Cabs and Autos.
    """
    np.random.seed(42)
    n_samples = 1000
    
    sim_dist = np.random.uniform(1.0, 25.0, n_samples)
    sim_peak = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    sim_rain = np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2])
    sim_group = np.random.randint(1, 5, size=n_samples)
    sim_mode = np.random.choice([0, 1, 2], size=n_samples, p=[0.3, 0.4, 0.3]) # Balanced distribution
    
    # Dynamic generation formula representing the real-world Ola/Uber/Rapido pricing layers
    base_fare = 60 + (sim_dist * 15) + (sim_peak * 35) + (sim_rain * 45)
    for i in range(n_samples):
        if sim_mode[i] == 0:   # Bike Taxi (Rapido Mode)
            base_fare[i] = (15 + (sim_dist[i] * 7) + (sim_peak[i] * 10) + (sim_rain[i] * 15))
        elif sim_mode[i] == 1: # On-Demand Auto (Ola/Uber Auto)
            base_fare[i] = (35 + (sim_dist[i] * 12) + (sim_peak[i] * 20) + (sim_rain[i] * 25))
        elif sim_mode[i] == 2: # Online Cab Split pricing
            base_fare[i] = (80 + (sim_dist[i] * 20) + (sim_peak[i] * 50) + (sim_rain[i] * 60)) / sim_group[i]
            
    X = pd.DataFrame({
        'distance_km': sim_dist,
        'is_peak_hour': sim_peak,
        'is_raining': sim_rain,
        'mode_encoded': sim_mode,
        'group_size': sim_group
    })
    
    model = RandomForestRegressor(n_estimators=40, random_state=42)
    model.fit(X.values, base_fare)
    
    # Mapping logic strings
    mode_map = {'online_bike': 0, 'online_auto': 1, 'online_cab': 2}
    encoded_input_mode = mode_map.get(transport_mode, 2)
    
    input_vector = np.array([[distance_km, is_peak_hour, is_raining, encoded_input_mode, group_size]])
    predicted_fare = model.predict(input_vector)
    
    return float(predicted_fare[0])

def calculate_bmtc_exact_fixed_fare(distance_km: float, passenger_type: str = "adult", gender: str = "male", has_bus_pass: bool = False, is_ac: bool = False, static_fares: dict = None) -> dict:
    """
    🎫 Handles strict stage-wise pricing variations, concessions, 
    Shakti Scheme for women (via valid IDs), and Bus Pass exclusions based on your JSON matrix.
    """
    if distance_km < 0.1:
        return {"fare": 0.0, "notes": "Negligible distance mapping."}
        
    ptype = passenger_type.lower()
    gender_clean = gender.lower()
    
    # 💳 1. ACTIVE BUS PASS BYPASS TRIGGER
    if has_bus_pass:
        return {
            "fare": 0.0, 
            "notes": f"Fare 100% covered under active BMTC {'AC Vajra' if is_ac else 'Ordinary'} Pass. Cashless commute enabled."
        }

    if is_ac:
        # 🔵 2. AC VAJRA SYSTEM (From your fully updated JSON columns)
        ac_slabs = static_fares.get("bmtc_ac_vajra_slabs", [])
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
            
        return {"fare": fare, "notes": "Standard AC Vajra ticket charges apply. Shakti Scheme not applicable."}

    else:
        # 🟢 3. NON-AC ORDINARY SYSTEM (With absolute validation blocks)
        # 👩 SHAKTI SCHEME CONTROL OVERRIDE
        if gender_clean == "female":
            return {
                "fare": 0.0, 
                "notes": "FREE Travel under Shakti Scheme! Please keep any valid Govt ID card (like Aadhaar) ready for confirmation."
            }
            
        ordinary_slabs = static_fares.get("bmtc_ordinary_slabs", [])
        adult_fare = 32.0 if ordinary_slabs else 32.0 # Default max cap safety fallback
        
        for slab in ordinary_slabs:
            if distance_km <= slab["max_km"]:
                adult_fare = float(slab["fare"])
                break
                
        if ptype == "child":
            return {"fare": round(adult_fare * 0.5), "notes": "Concession Child Half-Ticket applied."}
        elif ptype == "senior":
            # Exact mapping from your explicit image table chart
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
    🚀 Unified Multi-Criteria Pricing Gateway:
    Combines machine learning predictions (Cabs/Autos) and static configurations (Metro/Buses)
    into a structured matrix ready for your TOPSIS rank engine layer.
    """
    static_fares, kia_routes = load_transit_data()
    src, dst = source_name.lower(), dest_name.lower()
    ptype = passenger_type.lower()

    # ✈️ CASE A: AIRPORT VAYU VAJRA LOOKUP WITH PROTECTED VICE-VERSA FLOWS
    if "airport" in src or "airport" in dst or "kia" in src or "kia" in dst:
        for route_id, route_data in kia_routes.get("vayu_vajra_kia_routes", {}).items():
            for stop in route_data["stops"]:
                stop_clean = stop["stop_name"].lower()
                
                # Bi-directional tracking execution loop
                if (stop_clean in src and "airport" in dst) or (stop_clean in dst and "airport" in src):
                    base_kia_fare = float(stop["fare"])
                    final_kia = base_kia_fare * 0.5 if ptype == "child" else base_kia_fare
                    return {
                        "vayu_vajra_kia": {
                            "fare": final_kia, 
                            "comfort": 5.0, 
                            "type": "Premium Airport AC Coach",
                            "notes": "Airport route triggered. Pass or Shakti concessions not valid on KIA lines."
                        }
                    }

    # 🚇 CASE B: NAMMA METRO SLAB ROUTER
    metro_fare = 95.0 # Max boundary safety fallback
    metro_slabs = static_fares.get("namma_metro_slabs", [])
    for slab in metro_slabs:
        if distance_km <= slab["max_km"]:
            metro_fare = float(slab["fare"])
            break
    if ptype == "child":
        metro_fare = round(metro_fare * 0.5, 2)

# 🚌 CASE C: BMTC PUBLIC MULTI-TIER MANAGEMENT
    ordinary_metrics = calculate_bmtc_exact_fixed_fare(distance_km, ptype, gender, has_bus_pass, is_ac=False, static_fares=static_fares)
    ac_metrics = calculate_bmtc_exact_fixed_fare(distance_km, ptype, gender, has_bus_pass, is_ac=True, static_fares=static_fares)

    # 🚗 CASE D: ON-DEMAND PRIVATE TRANSPORTATION VIA MACHINE LEARNING FORECAST
    # (Using the accurate function name to sync your Random Forest Regressor)
    cab_fare = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_cab', group_size)
    auto_fare = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_auto', group_size)
    bike_fare = predict_on_demand_private_fare(distance_km, is_peak_hour, is_raining, 'online_bike', group_size) if group_size == 1 else 0.0

    return {
        "namma_metro": {"fare": metro_fare, "comfort": 4.5, "type": "Metro Grid System", "notes": "BMRCL token rules apply."},
        "ordinary_bus": {"fare": ordinary_metrics["fare"], "comfort": 2.0, "type": "Non-AC City Ordinary", "notes": ordinary_metrics["notes"]},
        "ac_vajra_bus": {"fare": ac_metrics["fare"], "comfort": 4.0, "type": "City AC Vajra Bus", "notes": ac_metrics["notes"]},
        "online_cab": {"fare": round(cab_fare, 2), "comfort": 4.8, "type": "On-Demand Sedan/Hatchback", "notes": "ML predicted dynamic pricing based on weather/peak surge."},
        "online_auto": {"fare": round(auto_fare, 2), "comfort": 2.5, "type": "On-Demand Digital Auto", "notes": "ML predicted standard surge rates apply."},
        "online_bike": {"fare": round(bike_fare, 2), "comfort": 1.5, "type": "On-Demand Moto Taxi", "notes": "Available only for solo passenger requests." if group_size == 1 else "Not available for multi-person group sizes."}
    }