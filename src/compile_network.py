import os
import subprocess
import sys

def execute_network_conversion():
    """
    Locates the SUMO binaries via direct environment hooks and compiles 
    the OSM layout into a structural XML network mesh using updated flags.
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
                print(f"🛰️ Dynamically registered SUMO_HOME at: {path}")
                break
                
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        print("❌ Error: SUMO_HOME environment variable could not be resolved automatically!")
        return False
        
    netconvert_binary = os.path.join(sumo_home, "bin", "netconvert.exe")
    if not os.path.exists(netconvert_binary):
        print(f"❌ Cannot find netconvert.exe inside bin.")
        return False
        
    print("🛠️ Environment Hook resolved successfully. Launching Network Compiler...")
    
    osm_input = "simulation/karnataka_corridor.osm"
    net_output = "simulation/karnataka.net.xml"
    
    # 🌟 UPDATED: Changed --tls.guess-geometry to --tls.guess for SUMO 1.20+ compatibility
    cmd = [
        netconvert_binary,
        "--osm-files", osm_input,
        "-o", net_output,
        "--geometry.remove",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess"
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("✅ SUCCESS! SUMO Network Mesh Compiled Successfully!")
        print(f"📂 Output Node Matrix locked at: {net_output}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Netconvert Execution Failed:")
        print(e.stderr)
        return False
    except Exception as ex:
        print(f"❌ Execution error encountered: {str(ex)}")
        return False

if __name__ == "__main__":
    execute_network_conversion()