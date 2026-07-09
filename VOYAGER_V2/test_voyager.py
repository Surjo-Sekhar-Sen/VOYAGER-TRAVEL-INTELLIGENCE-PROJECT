import sys
import os

# Ab imports karo
from src.spatial_engine import spatial_engine
from src.agent_core import agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.spatial_engine import spatial_engine

print("Imports successful!")
print("DEBUG: API Key detected:", os.getenv("GEMINI_API_KEY") is not None)

def run_test():
    print("--- Voyager Intelligence Test ---")
    # test_voyager.py ke andar
    # test_voyager.py mein
    results = spatial_engine.get_nearby_results(12.9716, 77.5946, "bank")
    print(f"DEBUG: Total results received: {len(results)}")
    for r in results:
        print(f"-> {r['name']} | Score: {r['final_score']}")    


    print("\n--- Test Complete ---")

if __name__ == "__main__":
    run_test()