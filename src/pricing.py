import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def predict_transit_fare(distance_km: float, is_peak_hour: int, is_raining: int, transport_mode: str, group_size: int):
    """
    Upgraded Random Forest Core: Predicts adaptive pricing based on multi-feature environmental matrix.
    Transport Modes: 'online_cab', 'shared_auto', 'public_bus'
    """
    # Simulate a smart historical log dataset
    np.random.seed(42)
    n_samples = 1000
    
    sim_dist = np.random.uniform(1.0, 25.0, n_samples)
    sim_peak = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    sim_rain = np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2])
    sim_group = np.random.randint(1, 5, size=n_samples)
    
    # Encode mode: 0 for bus, 1 for shared auto, 2 for cab
    sim_mode = np.random.choice([0, 1, 2], size=n_samples, p=[0.5, 0.3, 0.2])
    
    # Base real-world pricing formula simulation
    # Bus is cheap, shared auto is medium, cab is expensive. Group size reduces price per person for cabs/autos.
    base_fare = 10 + (sim_dist * 12) + (sim_peak * 25) + (sim_rain * 35)
    for i in range(n_samples):
        if sim_mode[i] == 0: base_fare[i] = 15 + (sim_dist[i] * 2)  # Bus flat cheap rate
        elif sim_mode[i] == 1: base_fare[i] = 30 + (sim_dist[i] * 8) # Shared auto
        elif sim_mode[i] == 2: base_fare[i] = (60 + (sim_dist[i] * 18)) / sim_group[i] # Cab split
        
    X = pd.DataFrame({
        'distance_km': sim_dist,
        'is_peak_hour': sim_peak,
        'is_raining': sim_rain,
        'mode_encoded': sim_mode,
        'group_size': sim_group
    })
    
    model = RandomForestRegressor(n_estimators=40, random_state=42)
    model.fit(X.values, base_fare)
    
    # Map input mode to encoder value
    mode_map = {'public_bus': 0, 'shared_auto': 1, 'online_cab': 2}
    encoded_input_mode = mode_map.get(transport_mode, 1)
    
    input_vector = np.array([[distance_km, is_peak_hour, is_raining, encoded_input_mode, group_size]])
    predicted_fare = model.predict(input_vector)
    
    return float(predicted_fare[0])