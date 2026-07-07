import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def run_topsis_optimizer(matrix: np.ndarray, weights: np.ndarray, benefit_criteria: list, path_names: list) -> list:
    """
    Advanced 8-Criteria TOPSIS Core Optimization Engine.
    Matrix columns: [Cost, Time, Live_Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
    """
    # 1. Vector Normalization Layer
    matrix_comp = matrix.astype(float)
    sq_sums = np.sqrt(np.sum(matrix_comp**2, axis=0))
    
    # Avoid zero division scenario
    sq_sums[sq_sums == 0] = 1e-9
    normalized_matrix = matrix_comp / sq_sums

    # 2. Weight Application Matrix
    weighted_matrix = normalized_matrix * weights

    # 3. Determine Ideal Best ($A^*) and Ideal Worst ($A^-$)
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

    # 5. Relative Closeness Score Sync
    scores = distance_worst / (distance_best + distance_worst + 1e-9)

    # 6. Rank Results sorting descending
    ranked_indices = np.argsort(scores)[::-1]
    
    results = []
    for index in ranked_indices:
        results.append({
            "route_name": path_names[index],
            "topsis_score": float(scores[index]),
            "raw_metrics_snapshot": matrix[index].tolist()
        })
        
    return results

def train_and_inject_traffic_intelligence():
    """
    Trains the Random Forest Regressor on active background traffic log loops 
    and prepares live congestion multipliers for decision tracking grids.
    """
    log_path = "data_cache/traffic_logs.csv"
    if not os.path.exists(log_path):
        print("⚠️ Warning: Traffic logs not found at data_cache/traffic_logs.csv. Running baseline defaults.")
        os.makedirs("data_cache", exist_ok=True)
        df_mock = pd.DataFrame({"step_time": [100, 200, 300], "live_speed_mps": [12.0, 8.5, 4.0], "congestion_overhead": [0.1, 0.4, 0.8]})
        df_mock.to_csv(log_path, index=False)
        
    print("🌲 Training Random Forest on High-Density Traffic Grid Matrix...")
    df = pd.read_csv(log_path)
    X = df[["step_time", "live_speed_mps"]]
    y = df["congestion_overhead"]
    
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_model.fit(X.values, y.values)
    print("✅ Random Forest Model Trained successfully inside Traffic Core!")
    
    # User friendly choice mapping matching frontend configuration cards
    # Columns: [Cost, Time, Live_Traffic_Delay, Walking_Dist, Safety, Weather_Risk, Availability, Group_Comfort]
    sample_alternatives = np.array([
        [25.0,  55.0, 0.7, 0.85, 4.2, 3.5, 5.0, 2.0],  # Dedicated Bus & Metro Grid Network
        [145.0, 25.0, 0.3, 0.05, 4.8, 1.2, 3.0, 5.0]   # On-Demand Cabs & Auto Aggregates
    ])
    
    # Predict delay overhead at standard step time with average speed index
    predicted_delay = float(rf_model.predict([[250, 4.5]])[0])
    print(f"Live Congestion Overhead Predicted: {predicted_delay:.4f}")
    
    # Overwrite the Live_Traffic_Delay parameter column dynamically (Index 2)
    sample_alternatives[:, 2] = predicted_delay * sample_alternatives[:, 2]
    
    # Standard Criteria Weights Configuration (Summing to 1)
    weights = np.array([0.20, 0.15, 0.15, 0.10, 0.15, 0.05, 0.10, 0.10])
    benefit_criteria = [False, False, False, False, True, False, True, True]
    
    mode_names = ["Dedicated Bus & Metro Grid Network", "On-Demand Cabs & Auto Aggregates"]
    
    print("Triggering 8-Criteria TOPSIS Mathematical Optimizations...")
    ranked_routes = run_topsis_optimizer(sample_alternatives, weights, benefit_criteria, mode_names)
    
    for rank, route in enumerate(ranked_routes, start=1):
        print(f"Rank {rank}: {route['route_name']} (TOPSIS Score: {route['topsis_score']:.4f})")
        
    return ranked_routes

if __name__ == "__main__":
    train_and_inject_traffic_intelligence()