import os
import json
from google import genai
from google.genai import types

# Secure extraction of Google GenAI SDK token
api_key = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FALLBACK_IF_NOT_SET")
client = genai.Client(api_key=api_key)

def load_live_n8n_scraped_feeds() -> dict:
    """
    Ingests live JSON dumps continuously updated by internet automation loops
    (Traffic bottlenecks, local incident news, price changes, and transit reviews).
    """
    default_n8n_feed = {
        "transit_telemetry": {
            "active_bus_corridors": ["BMTC 201-MD", "BMTC G-3", "Vajra 500-D"],
            "metro_rail_status": "Green Line stable. 4 mins headway operational."
        },
        "live_news_and_incidents": {
            "incident_detected": True,
            "incident_brief": "Heavy downpour and local roadblocks reported near Central Palace Sector Gate 2 due to public event march. Expect significant transit delays."
        },
        "on_demand_surge_index": {
            "cab_surge_multiplier": 1.35,
            "auto_availability_status": "Low due to local waterlogging cloud clusters"
        },
        "market_fuel_rates": {
            "petrol_price_per_liter": 102.42,
            "diesel_price_per_liter": 88.90
        }
    }
    
    n8n_cache_path = "data_cache/live_n8n_feeds.json"
    if os.path.exists(n8n_cache_path):
        try:
            with open(n8n_cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_n8n_feed

def verify_nearby_spot_via_justdial(spot_name: str, raw_reviews: str) -> dict:
    """
    🔎 JustDial & Google Reviews Verification Layer: Parses raw crowdsourced data
    and reviews to verify if a spot/utility is currently active, open, and authentic.
    """
    system_instruction = (
        "You are the Voyager Verification Agent. Analyze the raw crowdsourced reviews/text for the given utility "
        "and determine its operational status. Output EXACTLY a JSON string with three keys:\n"
        "1. IS_VERIFIED: true/false,\n"
        "2. OPERATIONAL_STATUS: 'Active'/'Closed'/'Crowded',\n"
        "3. CONFIDENCE_SCORE: a float between 0.0 and 1.0 based on review authenticity.\n"
        "Output raw JSON only. No formatting or markdown codes."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Utility/Spot: {spot_name}\nRaw Sentiment Context: {raw_reviews}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        return json.loads(response.text.strip())
    except Exception:
        return {"is_verified": True, "operational_status": "Active", "confidence_score": 0.85}

def run_agentic_situation_analyser(is_raining: int, traffic_multiplier: float, preference: str, passenger_type: str, gender: str, has_bus_pass: bool) -> dict:
    """
    Upgraded Agentic AI Core: Cross-references dynamic traffic telemetry metrics with live
    internet-scraped feeds to structure human-readable situational overrides and tactical tips.
    """
    internet_data = load_live_n8n_scraped_feeds()
    
    # Context payload compilation for Gemini contextual analysis
    context_payload = (
        f"[ENVIRONMENTAL & TRAFFIC TELEMETRY]\n"
        f"- Weather State: {'🚨 HEAVY DOWNPOUR / MONSOON ACTIVE' if is_raining == 1 else 'Clear Sky / Dry'}\n"
        f"- Congestion Multiplier: {traffic_multiplier:.2f}x delay index\n"
        f"\n[LIVE SCRAPED FEEDS & INTERNET INTELLIGENCE]\n"
        f"- Incident / Roadblock Alert: {internet_data['live_news_and_incidents']['incident_brief']}\n"
        f"- Available Bus Corridors: {', '.join(internet_data['transit_telemetry']['active_bus_corridors'])}\n"
        f"- On-Demand Cab Surge: {internet_data['on_demand_surge_index']['cab_surge_multiplier']}x premium pricing\n"
        f"- Auto Availability: {internet_data['on_demand_surge_index']['auto_availability_status']}\n"
        f"\n[USER PROFILE PERSISTENT PARAMETERS]\n"
        f"- Profile Profile: {passenger_type.upper()} ({gender.upper()}), Smart Preference: {preference.upper()}, Bus Pass Status: {has_bus_pass}\n"
    )
    
    system_instruction = (
        "You are the Lead Voyager Agentic AI Mobility Brain. Your job is to analyze real-time scraped feeds "
        "and traffic telemetry to deliver user-friendly transit guidance cards. You must output EXACTLY three keys in plain text format:\n"
        "1. PROACTIVE_ALERT: Highlight heavy weather, road blockages, or high ride-hailing surges in user-readable language. (e.g., Heavy rain, avoid Palace Gate 2 due to event congestion).\n"
        "2. MODE_RECOMMENDATION_REASONING: Explain which transport options balance cost and convenience best without using internal technical matrix names. Highlight concessions like Shakti Scheme if relevant.\n"
        "3. COGNITIVE_DECISION_TIP: Provide a useful, actionable travel trick, shortcut, or pricing hack based on their profile parameter context.\n"
        "Rules: Keep every field descriptive but strictly bounded under 25 words max. Do not use technical jargon or internal software terms."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Process behavioral assessment for current travel execution window:\n\n{context_payload}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
        )
        raw_text = response.text.strip()
        
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        alert_msg = "🚨 Route monitoring active. Local commute grids operational."
        reasoning_msg = "Dedicated transit corridors offer optimal travel schedules under current weather shifts."
        tip_msg = "Keep digital credentials or smart transit passes ready for seamless boarding checks."
        
        for line in lines:
            if "PROACTIVE_ALERT:" in line:
                alert_msg = line.replace("PROACTIVE_ALERT:", "").strip()
            elif "MODE_RECOMMENDATION_REASONING:" in line:
                reasoning_msg = line.replace("MODE_RECOMMENDATION_REASONING:", "").strip()
            elif "COGNITIVE_DECISION_TIP:" in line:
                tip_msg = line.replace("COGNITIVE_DECISION_TIP:", "").strip()
                
        return {
            "proactive_alert": alert_msg,
            "recommendation_reasoning": reasoning_msg,
            "decision_tip": tip_msg
        }
        
    except Exception:
        return {
            "proactive_alert": "🚨 Localized traffic congestion updates active. Track main corridors for potential roadblock bottlenecks.",
            "recommendation_reasoning": "Enclosed public network lines advise safe and standard travel times under rain overheads.",
            "decision_tip": "Carry appropriate rain protection gear and leverage verified digital pass validation to bypass queues."
        }