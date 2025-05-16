import streamlit as st
import login as log
import yaml
from yaml.loader import SafeLoader
from menu import menu

log.login()
menu()


if st.session_state['authentication_status']:
    try:
        if st.session_state['authenticator'].reset_password(st.session_state['username']):
            st.success('Password modified successfully')

            with open('./.streamlit/users.yaml', 'w') as file:
                yaml.dump(st.session_state['users'], file, default_flow_style=False)
    except Exception as e:
        st.error(e)
