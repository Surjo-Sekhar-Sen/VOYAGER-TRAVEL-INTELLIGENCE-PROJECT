import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.trip_planner import trip_planner
from src.spatial_engine import spatial_engine
from src.agent_core import agent

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class SearchRequest(BaseModel):
    lat: float
    lon: float
    query: str
    radius: float = 3.0

class AnalyzeRequest(BaseModel):
    query: str

@app.post("/api/search")
async def search_nearby(req: SearchRequest):
    # 1. Fetch ranked spots from Spatial Engine
    results = spatial_engine.get_nearby_results(req.lat, req.lon, req.query, req.radius)
    
    print(f"DEBUG: Found {len(results)} spots. Starting enriched summary fetch...")
    
    # 2. Sequential/Parallel Fetching for AI Details (Review + Price + Rating)
    # Hum 'agent.get_spot_details' ka use karenge jo maine bataya tha
    tasks = [agent.get_spot_details(spot['name'], req.query.lower()) for spot in results]
    enriched_data = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Assign AI-enriched details to spots
    for i, spot in enumerate(results):
        data = enriched_data[i]
        
        # Handle exceptions if AI call fails
        if isinstance(data, dict):
            spot['summary'] = data.get('review', 'Sentiment data unavailable.')
            spot['rating'] = data.get('rating', 'N/A')
            spot['price'] = data.get('price', 'N/A')
        else:
            spot['summary'] = "Sentiment data unavailable."
            spot['rating'] = 'N/A'
            spot['price'] = 'N/A'
            
    return {"status": "success", "data": results}

@app.post("/api/analyze_spot")
async def analyze_spot(req: AnalyzeRequest):
    # Fallback for simple analysis
    summary = await agent.get_detailed_summary(req.query)
    return {"summary": summary}

@app.post("/api/search_specific")
async def search_specific(req: AnalyzeRequest):
    results = spatial_engine.search_specific(req.query)
    return {"status": "success", "data": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)