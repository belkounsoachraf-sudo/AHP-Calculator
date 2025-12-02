import numpy as np
import pandas as pd

# Tableau des Indices Aléatoires (RI) pour n=1 à n=10
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}

def calculate_ahp_detailed(matrix_data):
    """
    Calcule et retourne toutes les étapes détaillées de l'AHP.
    """
    n = matrix_data.shape[0]

    # --- 1. Calcul des Priorités (Vecteur Propre) ---
    
    # Étape A: Calcul des valeurs propres et vecteurs propres
    eigen_values, eigen_vectors = np.linalg.eig(matrix_data)
    
    # Trouver la valeur propre maximale (λ max)
    lambda_max_index = np.argmax(eigen_values.real)
    lambda_max = eigen_values.real[lambda_max_index]
    
    # Extraire le vecteur propre correspondant
    raw_weights = eigen_vectors.real[:, lambda_max_index]
    
    # Normalisation du vecteur propre (Poids finaux)
    weights = raw_weights / np.sum(raw_weights)

    # --- 2. Calcul de la Cohérence (CI) ---
    if n > 1:
        CI = (lambda_max - n) / (n - 1)
    else:
        CI = 0.0

    # --- 3. Calcul du Taux de Cohérence (CR) ---
    ri_value = RI_TABLE.get(n, 1.49) # Utilise la valeur par défaut si n est trop grand
    
    if ri_value > 0 and n > 2:
        CR = CI / ri_value
    else:
        CR = 0.0 

    # --- 4. Conclusion ---
    if CR <= 0.10:
        conclusion = "✅ **Cohérence Acceptable** (CR est inférieur ou égal à 0.10). Les jugements sont cohérents."
    else:
        conclusion = "❌ **Cohérence Inacceptable** (CR est supérieur à 0.10). Les jugements doivent être révisés."
        
    
    # Retourner tous les résultats intermédiaires
    return {
        'n': n,
        'matrix': matrix_data,
        'lambda_max': lambda_max,
        'CI': CI,
        'RI_table': pd.DataFrame(RI_TABLE.items(), columns=['n', 'RI']),
        'RI': ri_value,
        'CR': CR,
        'weights': weights,
        'raw_eigenvector': raw_weights,
        'conclusion': conclusion
    }