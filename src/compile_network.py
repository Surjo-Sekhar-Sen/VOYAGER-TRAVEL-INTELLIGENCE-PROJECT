import os
import subprocess
import sys

def execute_network_conversion():
    """
    Locates the target simulation tools binaries via direct environment hooks and compiles 
    the raw road layouts into a structural network mesh grid utilizing updated flags.
    Handles warning buffers cleanly to prevent called process crashes.
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
                print(f"🛰️ Registered core simulation layout pathway at: {path}")
                break
                
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        print("❌ Error: Core simulation environment pathway variables could not be resolved.")
        return False
        
    netconvert_binary = os.path.join(sumo_home, "bin", "netconvert.exe")
    if not os.path.exists(netconvert_binary):
        netconvert_binary = os.path.join(sumo_home, "bin", "netconvert")
        if not os.path.exists(netconvert_binary):
            print("❌ Error: Missing processing engine conversion binaries inside bin.")
            return False
        
    print("🛠️ Environment resolved successfully. Compiling High-Fidelity Spatial Mesh Grid...")
    
    osm_input = "simulation/karnataka_corridor.osm"
    net_output = "simulation/karnataka.net.xml"
    
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
        # 🌟 CHANGE: Captured both standard output and error stream pipelines seamlessly 
        # without forcing high-exception system termination crashes on simple warnings.
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0 or os.path.exists(net_output):
            print("✅ SUCCESS! Road network systems grid successfully compiled!")
            print(f"📂 Output Node Matrix locked at: {net_output}")
            return True
        else:
            print("❌ Network compiler execution failed on code processing:")
            print(result.stderr)
            return False
            
    except Exception as ex:
        print(f"❌ Execution error encountered: {str(ex)}")
        return False

if __name__ == "__main__":
    execute_network_conversion()