import streamlit as st
import pandas as pd

# Importez vos fonctions de calcul AHP dès qu'elles seront prêtes
# from ahp_core import calculate_ahp_complete 

# --- INITIALISATION DE L'ÉTAT DE SESSION ---
# Le st.session_state est l'outil de Streamlit pour stocker des variables entre les exécutions.
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home' # La vue initiale
if 'projects' not in st.session_state:
    st.session_state['projects'] = [] # Liste de tous les projets enregistrés
if 'current_project' not in st.session_state:
    st.session_state['current_project'] = None # Le projet que l'utilisateur est en train de modifier

# --- FONCTIONS DE GESTION DE VUE ---

def set_view(view_name, project_data=None):
    """Change la vue et charge les données du projet si nécessaire."""
    st.session_state['current_view'] = view_name
    st.session_state['current_project'] = project_data
    st.rerun() # Force la ré-exécution du script pour afficher la nouvelle vue

# --- VUES DE L'APPLICATION ---

def view_home():
    """Affiche la page d'accueil avec les projets existants."""
    st.title("🏡 Bienvenue dans l'Analyse Hiérarchique (AHP)")
    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕ Créer un nouveau projet AHP", use_container_width=True):
            set_view('create')

    st.header("📋 Projets Existants")

    if not st.session_state['projects']:
        st.info("Aucun projet n'a encore été créé. Commencez par en créer un !")
    else:
        # Affichage des projets dans un tableau
        project_data = []
        for p in st.session_state['projects']:
            project_data.append({
                'Nom du Projet': p['name'],
                'Critères': len(p.get('criteria', [])),
                'Alternatives': len(p.get('alternatives', [])),
                'Dernière Modif': 'Aujourd\'hui' # Pour l'exemple
            })
        
        df_projects = pd.DataFrame(project_data)
        st.dataframe(df_projects, hide_index=True, use_container_width=True)
        
        # Option pour charger un projet (simple pour l'instant)
        st.markdown("**Fonctionnalité à implémenter :** Cliquer sur un projet pour le charger.")
    
def view_create():
    """Page pour nommer le projet et définir les critères/alternatives."""
    
    st.header("Création et Définition du Projet")
    if st.button("← Retour à l'Accueil"):
        set_view('home')
    st.markdown("---")
    
    # Formulaire de base
    with st.form("project_setup"):
        project_name = st.text_input("Nom du Projet", value="Mon Projet AHP")
        project_desc = st.text_area("Descriptif du Projet", "Aide à la décision pour...")
        
        st.subheader("Définition des Critères (lignes à comparer)")
        # Saisie dynamique des critères
        criteria_str = st.text_area(
            "Liste des Critères (un par ligne, Max 10)",
            "Coût\nQualité\nDélai"
        )
        
        st.subheader("Définition des Alternatives (choix possibles)")
        # Saisie dynamique des alternatives
        alternatives_str = st.text_area(
            "Liste des Alternatives (un par ligne, Max 12)",
            "Choix A\nChoix B\nChoix C"
        )
        
        submitted = st.form_submit_button("Continuer vers la Saisie des Jugements")
        
        if submitted:
            criteria = [c.strip() for c in criteria_str.split('\n') if c.strip()]
            alternatives = [a.strip() for a in alternatives_str.split('\n') if a.strip()]
            
            if len(criteria) < 2 or len(alternatives) < 2:
                st.error("Veuillez saisir au moins 2 critères et 2 alternatives.")
            else:
                # Sauvegarde des données initiales et passage à la vue de saisie
                project_data = {
                    'name': project_name,
                    'description': project_desc,
                    'criteria': criteria,
                    'alternatives': alternatives,
                    'matrices': {} # Pour stocker les matrices plus tard
                }
                set_view('input_criteria', project_data)

def view_input_criteria():
    """Page pour remplir la matrice de comparaison des critères."""
    if st.button("← Retour aux définitions"):
        set_view('create') # Simplification : retourne à la page de création pour modification
        st.stop()

    if not st.session_state['current_project']:
        set_view('home')
        st.stop()
        
    project = st.session_state['current_project']
    st.header(f"⚖️ Saisie Matrice : Poids des Critères ({project['name']})")
    st.subheader("Comparaison des Critères entre eux")
    
    # ----------------------------------------------------
    # Ici, nous allons créer l'interface pour la matrice N x N
    # Le code sera similaire à celui du 'app.py' précédent mais adapté.
    # ----------------------------------------------------
    
    # Début d'un exemple d'interface (à compléter)
    criteria = project['criteria']
    n = len(criteria)
    
    # Simulation de la création de la matrice N x N
    if 'criteria_matrix' not in project['matrices']:
        project['matrices']['criteria_matrix'] = np.ones((n, n), dtype=float)

    # st.write("Interface de saisie N x N à implémenter ici...")

    if st.button(f"Continuer vers les {len(criteria)} Matrices d'Alternatives"):
         # Simuler la sauvegarde de la matrice de critères remplie
         # project['matrices']['criteria_matrix'] = ...
         set_view('input_alternatives', project)

def view_input_alternatives():
    """Page pour remplir les N matrices de comparaison des alternatives."""
    st.header("📝 Saisie Matrice : Poids des Alternatives")
    st.markdown("**Fonctionnalité à implémenter :** Boucler sur chaque critère pour remplir la matrice des alternatives.")
    
    if st.button("Voir les Résultats"):
        set_view('results')

def view_results():
    """Affiche les scores finaux, le graphique, le CR et l'option d'export."""
    st.header("🎉 Résultats de l'Analyse AHP")
    st.markdown("**Fonctionnalité à implémenter :** Afficher le classement, le CR et les options d'export.")
    
    if st.button("Sauvegarder et Retourner à l'Accueil"):
        # Logique de sauvegarde du projet complété dans st.session_state['projects']
        st.session_state['projects'].append(st.session_state['current_project'])
        set_view('home')

# --- LOGIQUE PRINCIPALE DE ROUTAGE ---

if st.session_state['current_view'] == 'home':
    view_home()
elif st.session_state['current_view'] == 'create':
    view_create()
elif st.session_state['current_view'] == 'input_criteria':
    view_input_criteria()
elif st.session_state['current_view'] == 'input_alternatives':
    view_input_alternatives()
elif st.session_state['current_view'] == 'results':
    view_results()
