import os
import sys
import pandas as pd

def execute_agentic_simulation_loop():
    """
    Launches the background simulation grid in binary mode, analyzes micro-agent velocity,
    and drops traffic flow metrics logs directly into the cache directory.
    """
    if "SUMO_HOME" not in os.environ:
        print("❌ Error: Core environment simulation variable paths not set.")
        return

    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    
    try:
        import traci
    except ImportError:
        print("❌ Error: Automation runtime library module link missing.")
        return

    # Internal core simulation config matrix reference paths
    sumo_config = "simulation/karnataka.sumocfg"
    
    print("🚀 Initializing Background Traffic Generation Engine...")
    
    # Explicitly forced to run on silent background command line binary ('sumo') 
    # to avoid popping any visible UI window on front dashboard screen
    traci.start(["sumo", "-c", sumo_config])
    
    traffic_extracted_data = []
    step = 0
    
    while traci.simulation.getMinExpectedNumber() > 0 and step < 600:
        traci.simulationStep()  # Move simulation execution grid forward by 1 step
        
        vehicle_ids = traci.vehicle.getIDList()
        if len(vehicle_ids) > 0:
            for veh in vehicle_ids:
                speed = traci.vehicle.getSpeed(veh)
                
                # Cognitive Logic Layer: Evaluates bottleneck delays from absolute velocity constraints
                traffic_extracted_data.append({
                    "step_time": step,
                    "vehicle_id": veh,
                    "live_speed_mps": round(speed, 2),
                    "congestion_overhead": 1 if speed < 3.5 else 0
                })
        step += 1
        
    traci.close()
    print("🏁 Background Traffic generation tracking completed successfully.")
    
    # Store simulation log frames directly into structural cache storage for Random Forest models training
    df_logs = pd.DataFrame(traffic_extracted_data)
    os.makedirs("data_cache", exist_ok=True)
    df_logs.to_csv("data_cache/traffic_logs.csv", index=False)
    print("📂 Synchronized traffic log sheets successfully saved inside data_cache/ directory.")

if __name__ == "__main__":
    execute_agentic_simulation_loop()