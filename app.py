import streamlit as st
import numpy as np
import pandas as pd
from ahp_core import calculate_ahp_detailed

# --- Configuration et Titre ---
st.set_page_config(layout="wide")
st.title("🎓 Calculatrice AHP Didactique")
st.caption("Projet Académique : Aide à la Décision Multicritère")

# --- 1. Saisie des Éléments (Critères) ---
st.header("1. Définition et Saisie des Critères")

element_list_str = st.text_area(
    "Veuillez insérer les noms des Critères à comparer (un par ligne) :",
    "Coût\nPerformance\nSécurité"
)

# Préparation de la liste
elements = [e.strip() for e in element_list_str.split('\n') if e.strip()]
n = len(elements)

if n < 2:
    st.warning("Veuillez saisir au moins deux critères pour la comparaison AHP.")
    st.stop()
    
st.success(f"Nombre de critères détectés : **{n}**")

# --- 2. Saisie des Jugements (Matrice) ---
st.header("2. Matrice de Comparaison par Paires")
st.info("Utilisez l'échelle de Saaty (1-9) pour comparer les critères. Les valeurs réciproques sont calculées automatiquement.")

# Initialisation de la matrice de comparaison
matrix = np.ones((n, n), dtype=float)

# Interface de saisie dans un formulaire Streamlit
with st.form("ahp_input_form"):
    
    # Création des colonnes pour un affichage lisible
    cols = st.columns(n)
    
    # Boucle pour la saisie interactive (seulement i < j)
    for i in range(n):
        for j in range(i + 1, n):
            with cols[j]:
                # Saisie de la valeur
                value = st.number_input(
                    f"{elements[i]} vs {elements[j]}", 
                    min_value=1.0/9.0, max_value=9.0, value=1.0, 
                    step=0.01, format="%.2f", 
                    key=f"input_{i}_{j}",
                    help=f"Si {elements[i]} est 3 fois plus important que {elements[j]}, entrez 3. Si {elements[j]} est 3 fois plus important, entrez 1/3 (≈0.33)."
                )
                # Remplissage de la matrice et de son inverse
                matrix[i, j] = value
                matrix[j, i] = 1.0 / value  

    submitted = st.form_submit_button("Calculer les Poids et la Cohérence (Détaillé) 🚀")

# --- 3. Affichage des Résultats Détaillés ---
if submitted:
    
    # Appel de la fonction de calcul détaillée
    results = calculate_ahp_detailed(matrix)
    
    # --- Étape 3.1 : Affichage de la Matrice Complète ---
    st.header("Étape 3.1 : Matrice de Comparaison Complète")
    df_matrix = pd.DataFrame(results['matrix'], index=elements, columns=elements)
    st.dataframe(df_matrix.style.format("{:.4f}"))
    
    st.markdown("---")

    # --- Étape 3.2 : Calcul des Priorités (Vecteur Propre) ---
    st.header("Étape 3.2 : Calcul du Score de Priorité (Vecteur Propre)")
    
    # Affichage de la valeur propre maximale
    st.subheader("A. Valeur Propre Maximale ($\lambda_{\\text{max}}$)")
    st.info(f"$$\\lambda_{{\\text{{max}}}} = {results['lambda_max']:.4f}$$")
    st.info(f"$$\\lambda_{{\\text{{max}}}} = {results['lambda_max']:.4f}$$")
    



    
    # Affichage du Vecteur Propre brut (non normalisé)
    st.subheader("B. Vecteur Propre (Poids Brut)")
    df_raw_weights = pd.DataFrame({
        'Critère': elements,
        'Vecteur Propre Brut': results['raw_eigenvector'].round(4)
    })
    st.dataframe(df_raw_weights, hide_index=True)

    # Affichage des poids finaux (normalisés)
    st.subheader("C. Scores de Priorité des Critères")
    st.markdown("Les scores finaux (poids) sont obtenus en **normalisant** le Vecteur Propre brut, assurant que la somme des poids soit égale à 1 (ou 100%).")
    df_weights = pd.DataFrame({
        'Critère': elements,
        'Poids (Priorité)': results['weights'].round(4),
        'Poids (%)': (results['weights'] * 100).round(2).astype(str) + ' %'
    }).sort_values(by='Poids (Priorité)', ascending=False).reset_index(drop=True)
    
    st.dataframe(df_weights, hide_index=True)
    
    st.markdown("---")

    # --- Étape 3.3 : Calcul de l'Indice de Cohérence (CI) ---
    st.header("Étape 3.3 : Calcul de l'Indice de Cohérence (CI)")
    st.markdown("L'Indice de Cohérence ($CI$) mesure l'écart entre la cohérence parfaite ($\lambda_{\\text{max}} = n$) et vos jugements.")
    
    # Formule CI
    st.latex(f"CI = \\frac{{\\lambda_{{\\text{{max}}}} - n}}{{n - 1}} = \\frac{{{results['lambda_max']:.4f} - {results['n']}}}{{{results['n']} - 1}}")
    
    st.info(f"**Indice de Cohérence (CI) :** {results['CI']:.4f}")

    st.markdown("---")

    # --- Étape 3.4 : Calcul du Taux de Cohérence (CR) ---
    st.header("Étape 3.4 : Calcul du Taux de Cohérence (CR)")
    
    st.subheader("A. Tableau des Indices Aléatoires (RI)")
    st.markdown("Le $CR$ est calculé en divisant le $CI$ par la valeur de l'Indice Aléatoire ($RI$) correspondant à la taille de la matrice ($n$).")
    
    # Affichage du tableau RI
    df_ri = results['RI_table'].set_index('n').transpose()
    df_ri.columns.name = 'Taille (n)'
    df_ri.index.name = 'Index'
    st.dataframe(df_ri)
    
    st.markdown(f"**Valeur $RI$ utilisée pour $n={results['n']}$ :** {results['RI']:.2f}")

    st.subheader("B. Taux de Cohérence Final (CR)")
    
    # Formule CR
    st.latex(f"CR = \\frac{{CI}}{{RI}} = \\frac{{{results['CI']:.4f}}}{{{results['RI']:.2f}}}")

    # Conclusion finale
    if results['CR'] <= 0.10:
        st.success(f"**Taux de Cohérence (CR) : {results['CR']:.4f}**")
    else:
        st.error(f"**Taux de Cohérence (CR) : {results['CR']:.4f}**")

    # --- Conclusion Finale ---
    st.header("Conclusion Finale 🏁")
    st.markdown(results['conclusion'])
    
    # Visualisation Graphique
    st.subheader("Synthèse Graphique des Scores")
    fig, ax = plt.subplots()
    ax.bar(df_weights['Critère'], df_weights['Poids (Priorité)'], color=['#3CB371', '#FFD700', '#FF6347', '#4682B4'])
    ax.set_ylabel('Priorité / Poids')
    ax.set_title('Distribution Finale des Priorités AHP')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    st.pyplot(fig)
