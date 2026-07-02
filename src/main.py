from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
from src.decision import run_topsis_optimizer
from src.pricing import predict_transit_fare
from src.itinerary import generate_interactive_trip_canvas

app = FastAPI(
    title="Voyager Voyager Intelligence Dual-Core Gateway", 
    description="Production-grade AI Travel Engine integrating 8-Criteria MCDM and Random Forest Pricing Pipelines.",
    version="6.0.0"
)

# =====================================================================
# DATA CONTRACTS (PYDANTIC SCHEMAS)
# =====================================================================

class StandaloneRouteRequest(BaseModel):
    user_id: int
    source: str
    destination: str
    preference: str       # "safety", "economy", "balanced"
    time_of_day: str      # "day" or "night"
    is_raining: int       # 1 for Yes, 0 for No
    group_size: int       # Number of co-travellers

class MacroTripCanvasRequest(BaseModel):
    user_id: int
    selected_hotspots: List[str]  # E.g., ["Hotel Hub", "Mysore Palace", "Mysore Zoo"]
    budget: float
    time_of_day: str              # "day" or "night"
    is_raining: int               # 1 for Yes, 0 for No
    group_size: int               # Total passengers in group

# =====================================================================
# SYSTEM ROOT
# =====================================================================
@app.get("/")
def system_health_check():
    return {
        "status": "Active",
        "framework": "Voyager Enterprise Kernel v6.0",
        "PPT_Compliance": "8-Criteria Optimization Model Fully Deployed",
        "gateways": {
            "Feature_1": "/api/v1/optimize-route [Direct Point-to-Point Micro-Router]",
            "Feature_2": "/api/v1/build-dynamic-canvas [Macro Multi-Day Itinerary Planner Canvas]"
        }
    }

# =====================================================================
# FEATURE 1: Standalone Point-to-Point Micro-Router
# =====================================================================
@app.post("/api/v1/optimize-route")
def optimize_standalone_route(request: StandaloneRouteRequest):
    """
    Feature 1 (Micro-Router): Evaluates an explicit route from A to B across 
    3 distinct transport vectors using the 8 PPT criteria matrix.
    """
    distance_simulated = 6.5  # Baseline regional radius distance matrix approximation
    modes = ['public_bus', 'shared_auto', 'online_cab']
    
    alternatives_pool = []
    path_names = []
    
    for mode in modes:
        # Predict dynamic fare from Random Forest
        cost = predict_transit_fare(distance_simulated, 1 if request.time_of_day == "night" else 0, request.is_raining, mode, request.group_size)
        
        if mode == 'public_bus':
            time_taken = 35.0; walking_dist = 0.7; safety = 4.5; availability = 5.0; comfort = 2.0; traffic_delay = 20.0
        elif mode == 'shared_auto':
            time_taken = 22.0; walking_dist = 0.3; safety = 3.5; availability = 4.0; comfort = 3.0; traffic_delay = 12.0
        else: # online_cab booking matrix
            time_taken = 15.0; walking_dist = 0.05; safety = 4.9; availability = 4.5; comfort = 5.0; traffic_delay = 15.0
            
        if request.time_of_day == "night" and mode != 'online_cab':
            safety -= 1.5
            availability -= 2.0
            
        weather_risk = 4.0 if request.is_raining == 1 else 1.0
        alternatives_pool.append([cost, time_taken, traffic_delay, walking_dist, safety, weather_risk, availability, comfort])
        path_names.append(f"Deploy {mode.upper()} Route")

    # 8-Criteria Weights configuration based on direct preferences
    if request.preference == "safety" or request.time_of_day == "night":
        weights = np.array([0.05, 0.10, 0.05, 0.05, 0.45, 0.10, 0.10, 0.10]) # Strong emphasis on safety
    elif request.preference == "economy":
        weights = np.array([0.45, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05]) # Heavy focus on raw cost
    else:
        weights = np.array([0.25, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10]) # Balanced execution
        
    benefit_criteria = [False, False, False, False, True, True, True, True]
    ranked_results = run_topsis_optimizer(np.array(alternatives_pool), weights, benefit_criteria, path_names)

    return {
        "feature_mode": "Point-to-Point Standalone Core Router",
        "source": request.source,
        "destination": request.destination,
        "metrics_resolution": {
            "top_choice": ranked_results[0]['route_name'],
            "score": f"{ranked_results[0]['closeness_score']:.4f}",
            "full_evaluation_matrix": ranked_results
        }
    }

# =====================================================================
# FEATURE 2: Macro Multi-Day Itinerary Canvas
# =====================================================================
@app.post("/api/v1/build-dynamic-canvas")
def build_trip_canvas(request: MacroTripCanvasRequest):
    """
    Feature 2 (Itinerary Planner): Compiles user hotspots, hooks crowdsourced data insights, 
    and triggers Feature 1 Micro-Routing dynamically behind every destination node.
    """
    full_schedule = generate_interactive_trip_canvas(
        user_selected_hotspots=request.selected_hotspots,
        budget_limit=request.budget,
        time_of_day=request.time_of_day.lower(),
        is_raining=request.is_raining,
        group_size=request.group_size
    )
    return {
        "user_id": request.user_id,
        "feature_mode": "Macro Dynamic Trip Timeline Grid Engine",
        "payload": {
            "allocated_budget_limit": f"₹{request.budget:.2f}",
            "itinerary_timeline_nodes": full_schedule
        }
    }