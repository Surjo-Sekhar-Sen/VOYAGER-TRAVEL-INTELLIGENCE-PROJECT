import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np

class DataProcessor:
    def __init__(self):
        # Datasets ko load karna
        self.bmtc_stops = pd.read_csv("data_cache/bmtc_all_stops_master.csv")
        self.metro_stops = pd.read_csv("data_cache/bengaluru_metro_network.csv")
        self.ride_data = pd.read_csv("data_cache/bangalore_ride_data.csv")
        
        # Spatial Indexing (KDTree/BallTree for fast proximity search)
        self.bmtc_tree = self._build_tree(self.bmtc_stops)

    def _build_tree(self, df):
        # Lat/Lon ko radians mein convert karke BallTree banana
        coords = np.radians(df[['Latitude', 'Longitude']].values)
        return BallTree(coords, metric='haversine')

    def find_nearby_stops(self, lat, lon, radius_km=0.5):
        # User ki location ke aaspaas bus stops dhoondna
        query = np.radians([[lat, lon]])
        # 6371 is Earth's radius in KM
        indices = self.bmtc_tree.query_radius(query, r=radius_km/6371.0)
        return self.bmtc_stops.iloc[indices[0]]

# Initialize globally to use across the app
processor = DataProcessor()