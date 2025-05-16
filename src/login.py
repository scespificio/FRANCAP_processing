import streamlit as st
import streamlit_authenticator as stauth
import yaml, os
from yaml.loader import SafeLoader
from dotenv import load_dotenv

################################################## SET UP
load_dotenv()
AUTH_FILE = os.getenv('AUTH_FILE')

def login():

    if "users" not in st.session_state:
        with open(AUTH_FILE) as file:
            st.session_state['users'] = yaml.load(file, Loader=SafeLoader)

    stauth.Hasher.hash_passwords(st.session_state['users']['credentials'])

    if "authenticator" not in st.session_state:
            
        st.session_state['authenticator'] = stauth.Authenticate(
            st.session_state['users']['credentials'],
            st.session_state['users']['cookie']['name'],
            st.session_state['users']['cookie']['key'],
            st.session_state['users']['cookie']['expiry_days'],
            st.session_state['users']['pre-authorized'],
            auto_hash = False
        )
    try:
        st.session_state.authenticator.login(captcha = True)

        if st.session_state['authentication_status'] is None:
            st.warning('Please enter your username and password')
        elif not st.session_state['authentication_status']:
            st.error('Username/password is incorrect')

    except Exception as e:
        st.error(e)



def logout():
    st.session_state['authenticator'].logout(location = 'unrendered')


