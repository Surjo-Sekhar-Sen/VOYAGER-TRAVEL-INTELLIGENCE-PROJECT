import os
import sys
import pandas as pd

def execute_agentic_sumo_loop():
    if "SUMO_HOME" not in os.environ:
        print("❌ Error: SUMO_HOME environment variable not set.")
        return

    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    
    try:
        import traci
    except ImportError:
        print("❌ Error: traci module library not found. Install it via pip if needed.")
        return

    sumo_config = "simulation/karnataka.sumocfg"
    
    # 🌟 RUNNING SUMO IN BACKGROUND BINARY MODE
    print("🚀 Initializing Live Multi-Agent Traffic Simulation Instance...")
    
    # Using 'sumo' for fast background simulation. Change to 'sumo-gui' if you want to see the 2D window visualizer popup!
    traci.start(["sumo", "-c", sumo_config])
    
    traffic_extracted_data = []
    step = 0
    
    while traci.simulation.getMinExpectedNumber() > 0 and step < 600:
        traci.simulationStep()  # Move simulation forward by 1 tick
        
        vehicle_ids = traci.vehicle.getIDList()
        if len(vehicle_ids) > 0:
            for veh in vehicle_ids:
                speed = traci.vehicle.getSpeed(veh)
                
                # Dynamic Logic Hook: Simulating micro-congestion delays based on speed indices
                traffic_extracted_data.append({
                    "step_time": step,
                    "vehicle_id": veh,
                    "live_speed_mps": round(speed, 2),
                    "congestion_overhead": 1 if speed < 3.5 else 0
                })
        step += 1
        
    traci.close()
    print("🏁 Simulation Matrix Run Completed successfully.")
    
    # Dump simulation data logs directly into cache layer for Random Forest training
    df_logs = pd.DataFrame(traffic_extracted_data)
    os.makedirs("data_cache", exist_ok=True)
    df_logs.to_csv("data_cache/traffic_logs.csv", index=False)
    print("📊 SUCCESS! Real-world traffic logs saved at data_cache/traffic_logs.csv!")

if __name__ == "__main__":
    execute_agentic_sumo_loop()