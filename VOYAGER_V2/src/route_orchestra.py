import json
from src.agent_core import agent

class RouteOrchestrator:
    def __init__(self, trip_planner):
        self.planner = trip_planner

    async def get_all_paths(self, source, dest):
        # 1. Parallel Execution
        # Direct Path (Live Cab/Auto Data)
        direct_data = await agent.get_live_transit_prices(source, dest)
        
        # Smart/Multi-Leg Path (Topsis Weighted Logic)
        smart_data = await self.planner.get_trip_recommendations(
            source, dest, budget=1000, group_size=1, prefs={'priority': 'budget'}
        )
        
        # 2. Comparison Engine (Merging for Frontend)
        return {
            "direct_path": {
                "title": "Direct Cab/Auto",
                "options": [
                    {"mode": "Cab", "price": direct_data.get('cab_price'), "time": direct_data.get('cab_time')},
                    {"mode": "Auto", "price": direct_data.get('auto_price'), "time": direct_data.get('auto_time')}
                ]
            },
            "smart_path": {
                "title": "Smart Segmented Routes",
                "recommendations": smart_data  # Yeh wahi Topsis ranked list hai
            }
        }