import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def discover_shadow_hubs(trajectory_data: list, n_hubs: int = 2):
    """
    Unsupervised ML Layer: Takes raw travel coordinates logs and extracts 
    optimal dense transit hub coordinates (Centroids) using K-Means clustering.
    """
    if len(trajectory_data) == 0:
        return []
        
    # Convert coordinates snapshots list to DataFrame
    df = pd.DataFrame(trajectory_data) # Expected columns: ['lat', 'lng']
    
    # Initialize and Fit KMeans Model to determine peak density clusters
    kmeans = KMeans(n_clusters=n_hubs, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(df[['lng', 'lat']])
    
    # Extract the mathematical cluster centroids
    centroids = kmeans.cluster_centers_
    
    hubs_output = []
    for index, center in enumerate(centroids):
        hubs_output.append({
            "hub_id": index + 1,
            "lng": float(center[0]),
            "lat": float(center[1]),
            "nomenclature": f"Adaptive Transit Node Terminal 0{index + 1}"
        })
        
    return hubs_output