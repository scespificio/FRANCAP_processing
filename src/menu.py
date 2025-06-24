import streamlit as st
import session


def authenticated_menu():

    session.init_states()
    col1, col2 = st.sidebar.columns([1,1])
    col1.image('./ressources/LOGO_AREV.png', use_container_width='auto')
    col2.image('./ressources/Francap.png', use_container_width='auto')

    st.sidebar.title('Menu')
    

    st.sidebar.subheader('Acquisition de données', divider=True)
    st.sidebar.page_link("pages/acquisition.py", label="Acquisition des données", icon=":material/upload:")
    disabling_condition = st.session_state['codifrance'] is None or st.session_state['segurel'] is None
    st.sidebar.page_link("pages/visualisation.py", label="Consulter la données", icon=":material/visibility:", disabled = disabling_condition)

    st.sidebar.subheader('Fonctions', divider=True)
    st.sidebar.page_link("pages/valid_origine.py", label="corriger les origines", icon=":material/pin:")
    st.sidebar.page_link("pages/sr_codi.py", label="Stop Rayon et Degrouper Codifrance", icon=":material/arrow_split:")
    #st.sidebar.page_link("pages/valid_origine.py", label="Stop Rayon et Groupement Segurel", icon=":material/mediation:")

    st.sidebar.subheader('Paramètres', divider=True)
    st.sidebar.page_link("pages/config.py", label="Configuration", icon=":material/build:")
   
    st.sidebar.subheader('Profil', divider=True)
    st.sidebar.page_link("pages/logout.py", label="Déconnexion", icon=":material/logout:")
    st.sidebar.page_link("pages/reset_pwd.py", label="mot de passe", icon="⚙️")
    
def unauthenticated_menu():
    st.sidebar.image('./LOGO_AREV.png',width=150, use_column_width='auto')
    st.sidebar.title('Veuillez-vous authentifier')

def menu():
    session.init_states()
    if not st.session_state["authentication_status"]:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("app.py")
    menu()
