import numpy as np

class TopsisEngine:
    def rank_options(self, options_data, weights):
        if not options_data: return []
        
        # KEY FIX: Default accessibility_score ensure karo
        for o in options_data:
            if 'accessibility_score' not in o:
                o['accessibility_score'] = 5.0 
        
        matrix = np.array([[o['accessibility_score'], o['reliability_score']] for o in options_data])
        weighted_matrix = matrix * np.array(weights)
        
        for i, option in enumerate(options_data):
            option['final_score'] = np.mean(weighted_matrix[i])
        
        return sorted(options_data, key=lambda x: x['final_score'], reverse=True)