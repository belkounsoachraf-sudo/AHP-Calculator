# Échelle de Saaty pour la clarté de l'interface
SAATY_SCALE = {
    'Égal': 1,
    'Légèrement Préféré (3)': 3,
    'Fortement Préféré (5)': 5,
    'Très Fortement Préféré (7)': 7,
    'Absolument Préféré (9)': 9
}

def view_input_criteria():
    """Page pour remplir la matrice de comparaison des critères."""
    if st.button("← Retour aux définitions"):
        set_view('create')
        st.stop()

    if not st.session_state['current_project']:
        set_view('home')
        st.stop()
        
    project = st.session_state['current_project']
    st.header(f"⚖️ Saisie Matrice : Poids des Critères ({project['name']})")
    st.subheader("Comparaison des Critères entre eux")
    
    criteria = project['criteria']
    n = len(criteria)
    
    # Initialisation de la matrice si elle n'existe pas encore
    if 'criteria_matrix' not in project['matrices']:
        project['matrices']['criteria_matrix'] = np.ones((n, n), dtype=float)
        
    # Utilisation d'un formulaire pour regrouper la saisie et le bouton de validation
    with st.form("criteria_matrix_form"):
        
        # Le contenu de la matrice est stocké dans un dictionnaire pour Streamlit
        matrix_inputs = {} 
        
        # Instructions claires
        st.markdown("Pour chaque paire, déterminez l'importance du critère de **gauche (ligne)** par rapport au critère de **droite (colonne)** en utilisant l'échelle de Saaty.")
        st.info("Par exemple : si 'Qualité' est Fortement Préféré (5) à 'Coût', la valeur sera 5. Si 'Coût' est Fortement Préféré à 'Qualité', la valeur sera 1/5.")
        
        # Création de l'interface de saisie des comparaisons (uniquement la moitié supérieure)
        for i in range(n):
            for j in range(i + 1, n):
                crit_i = criteria[i]
                crit_j = criteria[j]
                
                key = f"{crit_i} vs {crit_j}"
                
                # Création d'une ligne de comparaison
                col_i, col_scale, col_j = st.columns([1, 2, 1])
                
                with col_i:
                    st.markdown(f"**{crit_i}**")
                
                with col_scale:
                    # Liste déroulante pour le jugement
                    # Nous utilisons les clés (texte) pour la lisibilité et les valeurs (nombre) pour le calcul
                    selection_key = f"selection_{i}_{j}"
                    selection = st.selectbox(
                        f"Importance de {crit_i} par rapport à {crit_j}",
                        options=list(SAATY_SCALE.keys()),
                        key=selection_key,
                        label_visibility='collapsed'
                    )
                    
                    # Déterminer la valeur numérique pour le calcul
                    value = SAATY_SCALE[selection]
                    matrix_inputs[key] = value

                with col_j:
                    # Affichage de l'inverse pour le critère opposé
                    # Ceci aide l'utilisateur à comprendre la réciprocité
                    inverse_value = 1.0 / value
                    st.markdown(f"**{crit_j}** (Inverse: **{inverse_value:.3f}**)")

        # Bouton pour valider la matrice des critères
        submitted = st.form_submit_button("Calculer les Poids des Critères et Continuer")
        
        if submitted:
            # Remplissage effectif de la matrice
            matrix_data = np.ones((n, n), dtype=float)
            
            # Remplissage à partir des inputs
            for i in range(n):
                for j in range(i + 1, n):
                    crit_i = criteria[i]
                    crit_j = criteria[j]
                    key = f"{crit_i} vs {crit_j}"
                    
                    value = matrix_inputs[key]
                    matrix_data[i, j] = value
                    matrix_data[j, i] = 1.0 / value
            
            # Sauvegarde de la matrice remplie dans l'état de session
            project['matrices']['criteria_matrix'] = matrix_data
            
            # Passage à la vue de calcul des poids et des matrices d'alternatives
            set_view('input_alternatives', project)
