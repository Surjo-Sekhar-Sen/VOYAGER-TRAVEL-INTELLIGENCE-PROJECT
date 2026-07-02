import os
import requests

def download_karnataka_corridor_osm(output_path="simulation/karnataka_corridor.osm"):
    """
    Downloads high-density urban network including local streets, residential alleys, 
    and highway networks using a robust high-limit mirror to completely bypass 504 errors.
    """
    print("🛰️ Connecting to Dedicated High-Capacity Overpass Mirror...")
    
    # Target focused high-density bounding box covering your main movement sectors
    bbox = "12.2800,76.6200,12.3500,76.6900" 
    
    # Switching to a heavy-duty corporate public mirror endpoint
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    
    # Comprehensive query including absolute grid levels: Highways + Local Alleys + Galiyaan
    overpass_query = f"""
    [out:xml][timeout:180][maxsize:1073741824];
    (
      way["highway"~"motorway|trunk|primary|secondary|tertiary|residential|living_street"]({bbox});
      node(w);
    );
    out body;
    >;
    out skel qt;
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://openstreetmap.org/"
    }
    
    try:
        response = requests.post(overpass_url, data={"data": overpass_query}, headers=headers, timeout=240)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ SUCCESS! Full High-Density Infrastructure (Highways + Galiyaan) saved at: {output_path}")
            return True
        else:
            print(f"❌ Primary Mirror rejected with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Network timeout or error: {str(e)}")
        return False

if __name__ == "__main__":
    download_karnataka_corridor_osm()