import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ahp_core import calculate_ahp # Assurez-vous que cette fonction est dans ahp_core.py

# --- Configuration et Titre ---
st.set_page_config(layout="wide")

# Utilisation de colonnes pour placer le titre à gauche et le nom à droite
col_title, col_name = st.columns([4, 1])

with col_title:
    st.title("🧮 Calculatrice AHP (Analytic Hierarchy Process)")

with col_name:
    # Affichage du nom plus petit et aligné à droite
    # J'ajoute margin-top: 15px pour un meilleur alignement vertical
    st.markdown("<div style='text-align: right; margin-top: 15px;'><h4 style='font-size: 14px;'>Développé par:<br>Belkounso Achraf</h4></div>", unsafe_allow_html=True)

st.caption("Application interne pour l'aide à la décision multicritère")

# --- Étape 1 : Saisie des Éléments (Critères ou Alternatives) ---
st.header("1. Définition des Éléments")

element_list_str = st.text_area(
    "Liste des Éléments à Comparer (un par ligne, ex: Critère A, Critère B, ...)",
    "Coût\nPerformance\nSécurité"
)

# Convertir la chaîne de caractères en une liste de noms
elements = [e.strip() for e in element_list_str.split('\n') if e.strip()]
n = len(elements)

if n < 2:
    st.warning("Veuillez saisir au moins deux éléments pour la comparaison.")
else:
    st.success(f"Nombre d'éléments détectés : **{n}**")
    
    # --- Étape 2 : Saisie des Jugements (Matrice) ---
    st.header("2. Saisie de la Matrice de Comparaison par Paires (Échelle 1-9)")
    st.info("Saisissez seulement les valeurs au-dessus de la diagonale. Les valeurs inverses sont calculées automatiquement.")

    # Initialisation de la matrice de comparaison
    matrix = np.ones((n, n), dtype=float)
    
    # Création d'une interface de tableau pour la saisie
    df_input = pd.DataFrame(index=elements, columns=elements)

    with st.form("ahp_input_form"):
        
        st.markdown("---") # Séparateur pour la clarté

        # Dictionnaire pour stocker les valeurs saisies avant de reconstruire la matrice
        input_values = {}
        
        # Boucle pour la saisie interactive des inputs (seulement i < j)
        for i in range(n):
            for j in range(i + 1, n):
                
                # --- Crée une ligne de saisie pour la comparaison i vs j ---
                col_left, col_input, col_right = st.columns([1, 2, 1])
                
                # Affiche l'élément de gauche
                with col_left:
                    st.markdown(f"**{elements[i]}**")
                
                # Saisie du jugement (i par rapport à j)
                with col_input:
                    key_id = f"input_{i}_{j}"
                    
                    value = st.number_input(
                        f"Comparaison : {elements[i]} par rapport à {elements[j]}", 
                        min_value=1.0/9.0, max_value=9.0, value=1.0, 
                        step=0.01, format="%.2f", 
                        key=key_id,
                        label_visibility="collapsed" # Cache le label pour plus de compacité
                    )
                    input_values[key_id] = value # Stocke la valeur pour la reconstruction

                # Affiche l'élément de droite (et son inverse)
                with col_right:
                    # Pour éviter l'erreur de division par zéro
                    inverse_val = 1.0 / value if value != 0 else 9.0 
                    st.markdown(f"**{elements[j]}** (Inverse: {inverse_val:.2f})")
                
                st.markdown("---") # Séparateur entre les comparaisons

        submitted = st.form_submit_button("Calculer les Poids et la Cohérence")

    # --- Étape 3 : Affichage des Résultats ---
    if submitted:
        # Reconstruire la matrice complète à partir des inputs (car Streamlit réexécute le script)
        for i in range(n):
            for j in range(i + 1, n):
                key_id = f"input_{i}_{j}"
                value = input_values[key_id]
                matrix[i, j] = value
                matrix[j, i] = 1.0 / value  # Réciproque

        st.header("3. Résultats de l'Analyse AHP")
        
        # Affichage de la Matrice construite
        df_matrix = pd.DataFrame(matrix, index=elements, columns=elements)
        st.subheader("Matrice de Comparaison Complète")
        st.dataframe(df_matrix.style.format("{:.3f}"))

        # Appel à la fonction de calcul AHP
        weights, CR, message = calculate_ahp(matrix)

        # 3.1 Affichage de la Cohérence
        st.subheader("Taux de Cohérence")
        if CR <= 0.10:
            st.success(f"**Taux de Cohérence (CR) :** {CR:.4f}")
        else:
            st.error(f"**Taux de Cohérence (CR) :** {CR:.4f}")
            
        st.markdown(f"**Interprétation :** {message}")

        # 3.2 Affichage des Poids
        st.subheader("Priorités (Poids) des Éléments")
        
        # Créer un DataFrame pour les résultats
        df_results = pd.DataFrame({
            'Élément': elements,
            'Poids (Priorité)': weights.round(4)
        }).sort_values(by='Poids (Priorité)', ascending=False).reset_index(drop=True)
        
        df_results['Poids (%)'] = (df_results['Poids (Priorité)'] * 100).round(2).astype(str) + ' %'
        
        st.dataframe(df_results, hide_index=True)
        
        # --- NOUVEAU : 3.3 Conclusion du Classement ---
        st.subheader("Conclusion du Classement 🥇")
        
        # Le premier élément après le tri est le vainqueur
        top_element = df_results.iloc[0]['Élément']
        top_score = df_results.iloc[0]['Poids (%)']
        
        # Affichage de la conclusion
        st.markdown(f"""
        L'analyse AHP est complétée. Le classement final montre que **{top_element}**
        est l'élément prioritaire avec un score de **{top_score}**.
        
        ---
        
        **Recommandation :** C'est l'élément qui correspond le mieux aux jugements exprimés dans la matrice.
        """)


        # 3.4 Visualisation Graphique (Améliorée)
        st.subheader("Visualisation des Poids")
        
        # On s'assure d'utiliser les couleurs du classement
        # On utilise une palette de couleurs basée sur le classement
        num_elements = len(df_results)
        colors = [('skyblue' if i < 1 else 'lightcoral' if i == num_elements - 1 else 'lightgreen') for i in range(num_elements)]

        fig, ax = plt.subplots()
        ax.bar(df_results['Élément'], df_results['Poids (Priorité)'], color=colors)
        ax.set_ylabel('Priorité / Poids')
        ax.set_title('Distribution des Poids AHP')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Option d'impression simple
        st.markdown("---")
        if st.button("Imprimer la page de Résultats (Ctrl+P ou Cmd+P)"):
            st.balloons()
            st.toast("Utilisez la fonction d'impression de votre navigateur pour générer le PDF.")
