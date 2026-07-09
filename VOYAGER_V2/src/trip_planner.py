import pandas as pd
import json

class TripPlanner:
    def __init__(self):
        # 1. Load Static Datasets (Fix data)
        self.data_cache = "data_cache/"
        self.bmtc = pd.read_csv(f"{self.data_cache}bmtc_all_stops_master.csv")
        self.metro = pd.read_csv(f"{self.data_cache}bengaluru_metro_network.csv")
        with open(f"{self.data_cache}transit_fares.json", 'r') as f:
            self.fares = json.load(f)
            
    def prepare_decision_matrix(self, source, dest, group_size, budget):
        # Yahan hum saare options ka ek table banayenge
        # Options: [Metro, Bus, Cab, Bike]
        # Columns: [Cost, Time, Safety, Comfort]
        matrix = [] 
        return matrix

trip_planner = TripPlanner()