import os
import subprocess
import sys

def build_simulation_demand():
    """
    Triggers SUMO's randomTrips utility to spawn multi-agent traffic flows
    across the downloaded and compiled high-fidelity Karnataka network grid.
    """
    if "SUMO_HOME" not in os.environ:
        possible_paths = [
            r"C:\Program Files (x86)\Eclipse\Sumo",
            r"C:\Program Files\Eclipse\Sumo",
            os.path.expanduser(r"~\AppData\Local\Programs\Eclipse\Sumo")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                os.environ["SUMO_HOME"] = path
                break

    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        print("❌ Error: SUMO_HOME environment variable not found!")
        return False
        
    random_trips_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    
    net_file = "simulation/karnataka.net.xml"
    route_file = "simulation/karnataka.rou.xml"
    
    print("🚗 Spawning Autonomous Agents into Compiled High-Density Grid...")
    
    # -p 0.3 handles dense multi-agent injection (vehicle spawns every 0.3 seconds)
    cmd = [
        "python", random_trips_path,
        "-n", net_file,
        "-e", "1000",   # Simulate 1000 steps of live traffic streams
        "-p", "0.3",
        "-o", route_file,
        "--validate"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ SUCCESS! Traffic flows generated and saved at: {route_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to run randomTrips utility: {str(e)}")
        return False

if __name__ == "__main__":
    build_simulation_demand()