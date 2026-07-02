import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def discover_shadow_hubs(trajectory_data: list, n_hubs: int = 2):
    """
    Unsupervised ML Layer: Takes raw GPS coordinate dicts and extracts 
    optimal dense transit hub coordinates (Centroids) using K-Means.
    """
    if len(trajectory_data) == 0:
        return []
        
    # Convert list of dicts to DataFrame
    df = pd.DataFrame(trajectory_data) # Expected columns: ['lat', 'lng']
    
    # Initialize and Fit KMeans Model
    kmeans = KMeans(n_clusters=n_hubs, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(df[['lng', 'lat']])
    
    # Extract the mathematical cluster centroids
    centroids = kmeans.cluster_centers_
    
    hubs_output = []
    for index, center in enumerate(centroids):
        hubs_output.append({
            "hub_id": index + 1,
            "lng": float(center[0]),
            "lat": float(center[1])
        })
        
    return hubs_output