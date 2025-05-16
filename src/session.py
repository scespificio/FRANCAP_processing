import streamlit as st
from datetime import datetime, timedelta, date


def init_states():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = True
        
    if 'name' not in st.session_state:
        st.session_state['name'] = 'Steve'
    
    if 'segurel' not in st.session_state:
        st.session_state['segurel'] = None

    if 'codifrance' not in st.session_state:
        st.session_state['codifrance'] = None

    if 'change_count_francap' not in st.session_state:
        st.session_state['change_count_francap'] = 0
    
    if 'change_count_cofifrance' not in st.session_state:
        st.session_state['change_count_codifrance'] = 0

    if 'change_count_segurel' not in st.session_state:
        st.session_state['change_count_segurel'] = 0
    


def reset(st):
    pass