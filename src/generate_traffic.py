import os
import subprocess

def build_simulation_demand():
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
        print("❌ Error: Multi-agent execution pathway triggers not found.")
        return False
        
    random_trips_path = os.path.join(sumo_home, "tools", "randomTrips.py")
    if not os.path.exists(random_trips_path):
        print("❌ Error: Trip layout automation utilities scripts missing inside tools corridor.")
        return False
    
    net_file = "simulation/karnataka.net.xml"
    route_file = "simulation/karnataka.rou.xml"
    
    print("🚗 Spawning Autonomous Agents into Compiled High-Density Grid...")
    
    cmd = [
        "python", random_trips_path,
        "-n", net_file,
        "-e", "1000",
        "-p", "0.3",
        "-o", route_file,
        "--allow-fringe", # 🌟 FORCE FRINGE: Custom borders edges use allow karega taaki crash na ho
        "--validate"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ SUCCESS! Travel demand trajectories mapped and saved at: {route_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to compile traffic generation stream flows: {str(e)}")
        return False

if __name__ == "__main__":
    build_simulation_demand()