import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def generate_live_transit_map(output_path="templates/transit_map.html"):
    """
    Parses consolidated coordinates and builds an active geographical map layer.
    """
    print("🌍 Initializing Interactive Bengaluru Mapping Framework...")
    
    # 1. Base Map Setup (Bengaluru Center Point)
    blr_center = [12.9716, 77.5946]
    transit_map = folium.Map(location=blr_center, zoom_start=12, control_scale=True)
    
    metro_file = "data_cache/bengaluru_metro_network.csv"
    bmtc_master_file = "data_cache/bmtc_all_stops_master.csv"
    
    # 🚇 LAYER A: NAMMA METRO STATIONS & CONNECTING LINES
    if os.path.exists(metro_file):
        print("🚇 Plotting Namma Metro station anchors and lines...")
        metro_df = pd.read_csv(metro_file)
        
        # Plot circles markers for metro
        for _, row in metro_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=row['line_color'],
                fill=True,
                fill_color=row['line_color'],
                fill_opacity=0.8,
                popup=f"<b>Metro Station:</b> {row['station_name']}<br><b>Line:</b> {row['line']}"
            ).add_to(transit_map)
            
            # Connect tracks logic
            if pd.notna(row['next_station_code']) and row['next_station_code'] != "NULL":
                next_node = metro_df[metro_df['station_code'] == row['next_station_code']]
                if not next_node.empty:
                    next_coords = [next_node.iloc[0]['latitude'], next_node.iloc[0]['longitude']]
                    folium.PolyLine(
                        locations=[[row['latitude'], row['longitude']], next_coords],
                        color=row['line_color'],
                        weight=4,
                        opacity=0.8
                    ).add_to(transit_map)
                    
    # 🚌 LAYER B: BMTC UNIFIED MASTER STOPS CLUSTERING
    if os.path.exists(bmtc_master_file):
        print("🚌 Injecting Master BMTC coordinates data cluster...")
        bmtc_df = pd.read_csv(bmtc_master_file)
        
        # Marker cluster limits lagging for thousands of items
        bus_cluster = MarkerCluster(name="BMTC Bus Network Layout").add_to(transit_map)
        
        for _, row in bmtc_df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                icon=folium.Icon(color="blue", icon="bus", prefix="fa"),
                popup=f"<b>Bus Stop:</b> {row['Stop Name']}"
            ).add_to(bus_cluster)
            
    # Add layer visibility toggle window
    folium.LayerControl().add_to(transit_map)
    
    # Save compilation directly to target directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    transit_map.save(output_path)
    print(f"🚀 HTML Live Map compiled successfully at: {output_path}")

if __name__ == "__main__":
    generate_live_transit_map()