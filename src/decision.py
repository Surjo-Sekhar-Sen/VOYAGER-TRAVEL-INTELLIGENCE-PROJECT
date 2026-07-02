import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def run_topsis_optimizer(alternatives_matrix: np.ndarray, weights: np.ndarray, benefit_criteria: list, alpha_names: list):
    """
    Advanced 8-Criteria TOPSIS Core.
    Matrix columns: [Cost, Time, Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
    """
    # 1. Vector Normalization
    matrix_comp = alternatives_matrix.astype(float)
    sq_sums = np.sqrt(np.sum(matrix_comp**2, axis=0))
    
    # Avoid zero division
    sq_sums[sq_sums == 0] = 1e-9
    normalized_matrix = matrix_comp / sq_sums

    # 2. Weight Application
    weighted_matrix = normalized_matrix * weights

    # 3. Determine Ideal Best and Ideal Worst
    ideal_best = []
    ideal_worst = []
    
    for i in range(len(benefit_criteria)):
        if benefit_criteria[i]:  # Higher is better (Safety, Availability, Comfort)
            ideal_best.append(np.max(weighted_matrix[:, i]))
            ideal_worst.append(np.min(weighted_matrix[:, i]))
        else:  # Lower is better (Cost, Time, Traffic, Walking)
            ideal_best.append(np.min(weighted_matrix[:, i]))
            ideal_worst.append(np.max(weighted_matrix[:, i]))

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    # 4. Calculate Euclidean Distances
    distance_best = np.sqrt(np.sum((weighted_matrix - ideal_best)**2, axis=1))
    distance_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst)**2, axis=1))

    # 5. Relative Closeness Score
    scores = distance_worst / (distance_best + distance_worst + 1e-9)

    # 6. Rank Results
    ranked_indices = np.argsort(scores)[::-1]
    
    results = []
    for index in ranked_indices:
        results.append({
            "route_name": alpha_names[index],
            "closeness_score": float(scores[index]),
            "raw_metrics_snapshot": alternatives_matrix[index].tolist()
        })
        
    return results

def train_and_inject_sumo_intelligence():
    """
    Trains the Random Forest on active SUMO loops and prepares 
    live testing values for the 8-Criteria TOPSIS matrix.
    """
    log_path = "data_cache/traffic_logs.csv"
    if not os.path.exists(log_path):
        print("❌ Error: SUMO logs not found at data_cache/traffic_logs.csv. Run run_sumo_instance first!")
        return None
        
    print("🌲 Training Random Forest on High-Density SUMO Matrix...")
    df = pd.read_csv(log_path)
    X = df[["step_time", "live_speed_mps"]]
    y = df["congestion_overhead"]
    
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_model.fit(X, y)
    print("✅ Random Forest Model Trained successfully!")
    
    # 🔮 Testing the integration with an example payload injection
    # Sample modes: [PUBLIC_BUS, SHARED_AUTO, ONLINE_CAB]
    # Metrics: [Cost, Time, Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
    sample_alternatives = np.array([
        [40,  45, 0.8, 800, 7, 2, 8, 4],  # Public Bus
        [90,  30, 0.4, 200, 6, 4, 9, 5],  # Shared Auto
        [250, 20, 0.2, 50,  9, 1, 7, 9]   # Online Cab
    ])
    
    # Let's use our SUMO model to dynamically overwrite the 'Traffic_Delay' column (index 2)
    # Predicting delay overhead at step time 250 with average speed 4.5 m/s
    predicted_delay = float(rf_model.predict([[250, 4.5]])[0])
    print(f"Live SUMO Congestion Overhead Predicted: {predicted_delay:.4f}")
    
    # Dynamically inject SUMO prediction into our transit alternatives matrix
    sample_alternatives[:, 2] = predicted_delay * sample_alternatives[:, 2]
    
    # Standard Weights Configuration (Summing to 1)
    weights = np.array([0.15, 0.15, 0.20, 0.10, 0.15, 0.05, 0.10, 0.10])
    benefit_criteria = [False, False, False, False, True, False, True, True]
    mode_names = ["PUBLIC_BUS", "SHARED_AUTO", "ONLINE_CAB"]
    
    print("Triggering 8-Criteria TOPSIS Mathematical Optimizations...")
    ranked_routes = run_topsis_optimizer(sample_alternatives, weights, benefit_criteria, mode_names)
    
    for rank, route in enumerate(ranked_routes, start=1):
        print(f"Rank {rank}: {route['route_name']} (Closeness Score: {route['closeness_score']:.4f})")
        
    return ranked_routes

if __name__ == "__main__":
    train_and_inject_sumo_intelligence()