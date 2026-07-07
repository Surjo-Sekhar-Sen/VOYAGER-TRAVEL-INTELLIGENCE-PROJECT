import os
import  sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pydantic import BaseModel
from typing import List
import numpy as np
import pandas as pd

# Import our verified active subsystems
from src.decision import run_topsis_optimizer
from src.itinerary import generate_interactive_trip_canvas, get_location_coordinates
from src.mapping import generate_live_transit_map
from src.pricing import calculate_comprehensive_transit_profile
from src.agent_core import run_agentic_situation_analyser

app = FastAPI(
    title="Voyager Intelligent Mobility Gateway Core", 
    description="Production-grade AI Travel Engine integrating 8-Criteria MCDM and Agentic Data Pipeline Feeds.",
    version="6.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# DATA CONTRACTS (DUAL CORE ROUTING SCHEMAS)
# =====================================================================
class StandaloneRouteRequest(BaseModel):
    user_id: int
    source: str
    destination: str
    preference: str       
    time_of_day: str      
    is_raining: int       
    group_size: int       
    passenger_type: str = "adult" 
    gender: str = "male"          
    has_bus_pass: bool = False

class MacroTripCanvasRequest(BaseModel):
    user_id: int
    selected_hotspots: List[str]  
    budget: float
    time_of_day: str              
    is_raining: int               
    group_size: int               
    passenger_type: str = "adult"
    gender: str = "male"
    has_bus_pass: bool = False

def fetch_traffic_delay_multiplier():
    log_path = "data_cache/traffic_logs.csv"
    if not os.path.exists(log_path):
        return 1.0
    try:
        df = pd.read_csv(log_path)
        if len(df) > 0:
            mean_overhead = df["congestion_overhead"].mean()
            return float(1.0 + (mean_overhead * 1.5))
    except Exception:
        pass
    return 1.0

# =====================================================================
# 🌐 INTEGRATED FRONTEND ROOT APPLICATION ROUTE
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def serve_frontend_dashboard(request: Request):
    index_html_path = "templates/index.html"
    if not os.path.exists(index_html_path):
        return HTMLResponse(content="<h3>Error: templates/index.html layout not found. Verify structure.</h3>", status_code=404)
        
    with open(index_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# =====================================================================
# LIVE IFRAME MAP ENDPOINT WITH COORDINATES INJECTION
# =====================================================================
@app.get("/map", response_class=HTMLResponse)
async def get_interactive_transit_map(request: Request, src: str = None, dest: str = None):
    map_html_path = "templates/transit_map.html"
    
    # 📍 Ingest dynamic geometry markers if parameters arrays are detected
    source_lat, source_lng = None, None
    dest_lat, dest_lng = None, None
    
    if src and dest:
        coord_src = get_location_coordinates(src)
        coord_dst = get_location_coordinates(dest)
        source_lat, source_lng = coord_src["lat"], coord_src["lng"]
        dest_lat, dest_lng = coord_dst["lat"], coord_dst["lng"]

    generate_live_transit_map(
        output_path=map_html_path,
        source_lat=source_lat,
        source_lng=source_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng
    )
    
    if not os.path.exists(map_html_path):
        return HTMLResponse(content="<h3>Error: Map trajectory compilation failed. Check system paths.</h3>", status_code=500)
        
    with open(map_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# =====================================================================
# FEATURE 1: STANDALONE MICRO ROUTER GATEWAY
# =====================================================================
@app.post("/api/v1/optimize-route")
def optimize_standalone_route(request: StandaloneRouteRequest):
    distance_simulated = 5.4  
    traffic_multiplier = fetch_traffic_delay_multiplier()
    current_sim_peak = 1 if request.time_of_day == "night" else 0
    
    profile_matrix = calculate_comprehensive_transit_profile(
        source_name=request.source,
        dest_name=request.destination,
        distance_km=distance_simulated,
        is_peak_hour=current_sim_peak,
        is_raining=request.is_raining,
        passenger_type=request.passenger_type,
        gender=request.gender,
        has_bus_pass=request.has_bus_pass,
        group_size=request.group_size
    )
    
    alternatives_pool = []
    path_names = []
    
    bus_fare = profile_matrix["ordinary_bus"]["fare"]
    cab_fare = profile_matrix["online_cab"]["fare"]
    
    sub_modes_breakdown = {
        "Dedicated Bus & Metro Grid Network": {
            "ordinary_bus_fare": float(bus_fare),
            "ac_vajra_bus_fare": float(profile_matrix["ac_vajra_bus"]["fare"]),
            "metro_rail_fare": float(profile_matrix["namma_metro"]["fare"])
        },
        "On-Demand Cabs & Auto Aggregates": {
            "moto_ride_mobility": float(profile_matrix["online_bike"]["fare"]),
            "auto_aggregate_hub": float(profile_matrix["online_auto"]["fare"]),
            "prime_cab_premium": float(cab_fare)
        }
    }
    
    # [Cost, Time, Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
    alternatives_pool.append([bus_fare, distance_simulated * 3.5, 20.0 * traffic_multiplier, 0.6, 4.4, 3.0 if request.is_raining else 1.0, 4.8, 3.5])
    path_names.append("Dedicated Bus & Metro Grid Network")
    
    alternatives_pool.append([cab_fare, distance_simulated * 1.8, 15.0 * traffic_multiplier, 0.05, 4.8, 1.0, 4.5, 5.0])
    path_names.append("On-Demand Cabs & Auto Aggregates")

    if request.time_of_day == "night":
        alternatives_pool[0][4] -= 1.0  
        alternatives_pool[0][6] -= 1.5  

    if request.preference == "safety" or request.time_of_day == "night":
        weights = np.array([0.05, 0.10, 0.05, 0.05, 0.45, 0.10, 0.10, 0.10]) 
    elif request.preference == "economy":
        weights = np.array([0.45, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05]) 
    else:
        weights = np.array([0.25, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10]) 
        
    benefit_criteria = [False, False, False, False, True, False, True, True]
    ranked_results = run_topsis_optimizer(np.array(alternatives_pool), weights, benefit_criteria, path_names)

    agent_insights = run_agentic_situation_analyser(
        is_raining=request.is_raining,
        traffic_multiplier=traffic_multiplier,
        preference=request.preference,
        passenger_type=request.passenger_type,
        gender=request.gender,
        has_bus_pass=request.has_bus_pass
    )

    return {
        "feature_mode": "Point-to-Point Micro-Router Core",
        "source": request.source,
        "destination": request.destination,
        "traffic_congestion_metrics": "STABLE_DATA_CORRIDOR",
        "agentic_ai_layer": agent_insights,
        "sub_modes_breakdown": sub_modes_breakdown,
        "metrics_resolution": {
            "top_choice": ranked_results[0]['route_name'],
            "score": f"{ranked_results[0]['topsis_score']:.4f}",
            "full_evaluation_matrix": ranked_results
        }
    }

# =====================================================================
# FEATURE 2: MACRO TRIP TIMELINE CANVAS GATEWAY
# =====================================================================
@app.post("/api/v1/build-dynamic-canvas")
def build_trip_canvas(request: MacroTripCanvasRequest):
    traffic_multiplier = fetch_traffic_delay_multiplier()
    
    full_schedule = generate_interactive_trip_canvas(
        user_selected_hotspots=request.selected_hotspots,
        budget_limit=request.budget,
        time_of_day=request.time_of_day.lower(),
        is_raining=request.is_raining,
        group_size=request.group_size,
        passenger_type=request.passenger_type,
        gender=request.gender,
        has_bus_pass=request.has_bus_pass
    )
    
    agent_insights = run_agentic_situation_analyser(
        is_raining=request.is_raining,
        traffic_multiplier=traffic_multiplier,
        preference="balanced",
        passenger_type=request.passenger_type,
        gender=request.gender,
        has_bus_pass=request.has_bus_pass
    )
    
    justdial_utilities_scraped = [
        {"utility_name": "SBI Bank ATM Hub", "category": "ATM/Banking", "proximity": "Adjacent to Mysore Palace Gate 1", "status": "Operational"},
        {"utility_name": "Canara Bank Branch", "category": "Bank Branch", "proximity": "450m from Mysore Zoo Transit Hub", "status": "Open / Low Crowds"}
    ]
    
    return {
        "user_id": request.user_id,
        "feature_mode": "Macro Dynamic Trip Timeline Grid Engine",
        "agentic_ai_layer": agent_insights,
        "justdial_scraped_utilities": justdial_utilities_scraped,
        "payload": {
            "allocated_budget_limit": f"₹{request.budget:.2f}",
            "itinerary_timeline_package": full_schedule
        }
    }