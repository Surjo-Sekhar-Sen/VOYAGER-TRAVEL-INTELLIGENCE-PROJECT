import numpy as np

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