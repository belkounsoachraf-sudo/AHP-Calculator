# La fonction de saisie de matrice sera réutilisée, donc nous la définissons à part
def matrix_input_interface(elements, matrix_key, title):
    """
    Interface générique pour la saisie d'une matrice N x N avec l'échelle de Saaty.
    """
    n = len(elements)
    
    # Initialisation de la matrice si elle n'existe pas
    if matrix_key not in st.session_state['current_project']['matrices']:
        st.session_state['current_project']['matrices'][matrix_key] = np.ones((n, n), dtype=float)

    current_matrix = st.session_state['current_project']['matrices'][matrix_key]
    
    st.subheader(title)
    st.info("Utilisez les options pour évaluer l'importance de l'élément de **gauche** par rapport à celui de **droite** selon le critère actuel.")
    
    # Utilisation d'un formulaire pour regrouper la saisie
    with st.form(f"{matrix_key}_form"):
        
        matrix_inputs = {}
        
        # Création de l'interface de saisie des comparaisons (uniquement la moitié supérieure)
        for i in range(n):
            for j in range(i + 1, n):
                elt_i = elements[i]
                elt_j = elements[j]
                
                key = f"{matrix_key}_{elt_i}_vs_{elt_j}"
                
                col_i, col_scale, col_j = st.columns([1, 2, 1])
                
                with col_i:
                    st.markdown(f"**{elt_i}**")
                
                with col_scale:
                    selection = st.selectbox(
                        f"Importance de {elt_i} par rapport à {elt_j}",
                        options=list(SAATY_SCALE.keys()),
                        key=key,
                        label_visibility='collapsed'
                    )
                    value = SAATY_SCALE[selection]
                    matrix_inputs[key] = value

                with col_j:
                    inverse_value = 1.0 / value
                    st.markdown(f"**{elt_j}** (Inverse: **{inverse_value:.3f}**)")

        submitted = st.form_submit_button("Valider cette Matrice")

        if submitted:
            # Remplissage effectif de la matrice
            matrix_data = np.ones((n, n), dtype=float)
            for i in range(n):
                for j in range(i + 1, n):
                    elt_i = elements[i]
                    elt_j = elements[j]
                    key = f"{matrix_key}_{elt_i}_vs_{elt_j}"
                    
                    value = matrix_inputs[key]
                    matrix_data[i, j] = value
                    matrix_data[j, i] = 1.0 / value
            
            # Sauvegarde de la matrice remplie
            st.session_state['current_project']['matrices'][matrix_key] = matrix_data
            st.success(f"Matrice '{title}' sauvegardée avec succès !")
            return True # Indique la validation
        return False # Indique qu'il n'y a pas eu de validation
    return False

def view_input_alternatives():
    """Page pour remplir les N matrices de comparaison des alternatives."""
    project = st.session_state['current_project']
    alternatives = project['alternatives']
    criteria = project['criteria']
    
    st.header(f"📝 Saisie des Matrices d'Alternatives ({project['name']})")
    
    # Utilisation de tabs pour gérer la boucle sur chaque critère
    tabs = st.tabs(criteria)
    
    validation_status = []

    for i, crit_name in enumerate(criteria):
        with tabs[i]:
            matrix_key = f'alt_matrix_{crit_name}'
            title = f"Comparaison des Alternatives selon le Critère : **{crit_name}**"
            
            # Appel de l'interface de saisie pour la matrice spécifique au critère
            is_validated = matrix_input_interface(alternatives, matrix_key, title)
            validation_status.append(is_validated)
            
            # Optionnel : Afficher la matrice sauvegardée
            if matrix_key in project['matrices']:
                st.subheader("Matrice actuelle")
                df_matrix = pd.DataFrame(project['matrices'][matrix_key], index=alternatives, columns=alternatives)
                st.dataframe(df_matrix.style.format("{:.4f}"))
                
                # Calcul de cohérence pour ce critère (aperçu)
                results = calculate_ahp_matrix(project['matrices'][matrix_key])
                st.markdown(f"**Taux de Cohérence (CR) :** {results['CR']:.4f} {results['conclusion']}")

    st.markdown("---")
    # Vérification si toutes les matrices ont été saisies
    all_matrices_ready = all(f'alt_matrix_{c}' in project['matrices'] for c in criteria)
    
    if all_matrices_ready:
        if st.button("Voir les Résultats Finaux et le Classement 🚀"):
            set_view('results')
    else:
        st.warning("Veuillez remplir et valider toutes les matrices (onglets) avant de continuer.")

def view_results():
    """Affiche les scores finaux, le graphique, le CR et l'option d'export."""
    project = st.session_state['current_project']

    if not project or 'criteria_matrix' not in project['matrices'] or not all(f'alt_matrix_{c}' in project['matrices'] for c in project['criteria']):
        st.error("Données incomplètes. Veuillez retourner à la saisie.")
        if st.button("Retour à la Saisie"):
            set_view('input_alternatives')
        return

    st.header(f"🎉 Résultats de l'Analyse AHP : {project['name']}")
    st.markdown("---")
    
    # 1. Calcul des scores finaux
    final_scores_df = calculate_final_scores(project)
    
    # 2. Vérification de la cohérence de la matrice des critères (matrice principale)
    criteria_results = calculate_ahp_matrix(project['matrices']['criteria_matrix'])
    
    st.subheader("⚠️ Cohérence de la Matrice Principale (Critères)")
    if criteria_results['CR'] > 0.10:
        st.error(f"❌ La **Matrice des Critères** a un Taux de Cohérence (CR) de **{criteria_results['CR']:.4f}**. Les jugements sont incohérents et doivent être révisés.")
    else:
        st.success(f"✅ La Matrice des Critères est **Cohérente** (CR = {criteria_results['CR']:.4f}).")
    
    st.markdown("---")

    # 3. Affichage du classement
    st.subheader("🏆 Classement Final des Alternatives")
    final_scores_df['Score (%)'] = (final_scores_df['Score Final'] * 100).round(2).astype(str) + ' %'
    
    # Ajouter la colonne 'Rang'
    final_scores_df.insert(0, 'Rang', range(1, 1 + len(final_scores_df)))

    st.dataframe(final_scores_df, hide_index=True, use_container_width=True)
    
    # 4. Graphique en barres
    import matplotlib.pyplot as plt
    
    st.subheader("📈 Visualisation des Scores")
    
    fig, ax = plt.subplots()
    # Utiliser les valeurs en % pour l'affichage
    scores_percent = final_scores_df['Score Final'] * 100
    
    # Couleurs basées sur le rang (meilleur en vert, moins bon en rouge)
    colors = plt.cm.RdYlGn(np.linspace(1, 0, len(final_scores_df)))
    
    ax.bar(final_scores_df['Alternative'], scores_percent, color=colors)
    ax.set_ylabel('Score Final (%)')
    ax.set_title('Distribution des Scores AHP')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")

    # 5. Exportation (Imprimer la page)
    st.subheader("🖨️ Exportation")
    if st.button("Imprimer les Résultats (PDF/Papier)"):
        # Astuce : Demande à l'utilisateur d'utiliser la fonction d'impression du navigateur
        st.toast("Veuillez utiliser la fonction d'impression de votre navigateur (Ctrl+P ou Cmd+P).")
        st.balloons()

    st.markdown("---")
    
    if st.button("Sauvegarder et Retourner à l'Accueil"):
        # Logique de sauvegarde du projet complété dans st.session_state['projects']
        st.session_state['projects'].append(st.session_state['current_project'])
        set_view('home')
