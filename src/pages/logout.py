import streamlit as st
import login as log

from menu import menu

log.login()

if st.session_state['authentication_status']:
    st.session_state['authenticator'].logout(location = 'unrendered')
    st.switch_page("app.py")


