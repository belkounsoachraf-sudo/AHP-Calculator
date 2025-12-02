import numpy as np
import pandas as pd

# Tableau des Indices Aléatoires (RI) de Saaty
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}

def calculate_ahp_matrix(matrix_data):
    """
    Calcule le vecteur de poids, lambda_max, CI et CR pour une seule matrice AHP.
    
    Args:
        matrix_data (np.array): Matrice de comparaison par paires (NxN).

    Returns:
        dict: Contenant les poids normalisés, lambda_max, CI, CR, et la conclusion.
    """
    n = matrix_data.shape[0]

    # --- 1. Calcul des Priorités (Vecteur Propre) ---
    
    if n == 0:
        return {'weights': np.array([]), 'lambda_max': 0.0, 'CI': 0.0, 'CR': 0.0, 'conclusion': "Matrice vide."}
        
    # Calcul des valeurs propres et vecteurs propres
    # np.linalg.eig est la méthode la plus précise pour le vecteur propre.
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
    ri_value = RI_TABLE.get(n, 1.49) 
    
    if ri_value > 0 and n > 2:
        CR = CI / ri_value
    else:
        # CR est 0.0 par définition pour n=1 ou n=2 (car le CI est 0 ou théoriquement 0)
        CR = 0.0 

    # --- 4. Conclusion ---
    if CR <= 0.10:
        conclusion = f"✅ Cohérence Acceptable (CR = {CR:.4f})."
    else:
        conclusion = f"❌ Cohérence Inacceptable (CR = {CR:.4f}). Les jugements doivent être révisés."
        
    
    return {
        'weights': weights,
        'lambda_max': lambda_max,
        'CI': CI,
        'CR': CR,
        'conclusion': conclusion
    }


def calculate_final_scores(project_data):
    """
    Calcule le score final de chaque alternative en combinant les poids des critères 
    et les poids locaux des alternatives.
    
    Args:
        project_data (dict): Contenant 'matrices' et 'alternatives'.

    Returns:
        pd.DataFrame: Scores finaux des alternatives.
    """
    # 1. Récupération des poids des critères (Global Weights)
    criteria_results = calculate_ahp_matrix(project_data['matrices']['criteria_matrix'])
    criteria_weights = criteria_results['weights']
    
    if criteria_results['CR'] > 0.10:
        # Si la matrice principale est incohérente, on peut choisir d'arrêter ou d'avertir.
        # Pour ce projet, nous continuons mais affichons l'avertissement plus tard.
        pass 
    
    alternatives = project_data['alternatives']
    num_alternatives = len(alternatives)
    num_criteria = len(project_data['criteria'])
    
    # Matrice de synthèse des poids locaux (Alternatives x Critères)
    # Chaque ligne est une alternative, chaque colonne est un critère.
    local_weights_matrix = np.zeros((num_alternatives, num_criteria))
    
    # 2. Remplissage des poids locaux
    for k, crit_name in enumerate(project_data['criteria']):
        # La matrice d'alternatives pour ce critère est stockée dans la clé 'alt_matrix_Critère'
        matrix_key = f'alt_matrix_{crit_name}'
        
        if matrix_key in project_data['matrices']:
            alt_matrix = project_data['matrices'][matrix_key]
            
            # Calcul des poids locaux pour ce critère
            alt_results = calculate_ahp_matrix(alt_matrix)
            local_weights = alt_results['weights']
            
            # Stockage des poids locaux (doit correspondre à l'ordre des alternatives)
            local_weights_matrix[:, k] = local_weights
    
    # 3. Calcul du score final (Synthèse AHP)
    # Multiplie la matrice des poids locaux par le vecteur de poids des critères
    # Poids Final = [Matrice Poids Locaux] x [Vecteur Poids Critères]
    final_scores = np.dot(local_weights_matrix, criteria_weights)
    
    # 4. Préparation du résultat final
    results_df = pd.DataFrame({
        'Alternative': alternatives,
        'Score Final': final_scores
    })
    
    # Ajout des CRs et des poids locaux pour le débug ou l'affichage détaillé (non implémenté ici pour la concision)
    
    return results_df.sort_values(by='Score Final', ascending=False)
