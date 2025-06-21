import streamlit as st
import login as log
import session
import sys, io, os
from datetime import datetime
sys.path.append('./Dependencies/')
import tool
import dataprocess as dp 

from dotenv import load_dotenv
from menu import menu

load_dotenv()
CONFIG_FILE = os.getenv('CONFIG_FILE')
SAVING_FILE = os.getenv('SAVING_FILE')
CONFIG_PATH = os.getenv('CONFIG_PATH')

def click_calculate(colpop):
    # Check if 'codifrance' exists in session state and is not None
    if 'codifrance' in st.session_state and st.session_state['codifrance'] is not None:
        st.session_state['codifrance'].reset_main(colB)
    
    # Check if 'segurel' exists in session state and is not None
    if 'segurel' in st.session_state and st.session_state['segurel'] is not None:
        st.session_state['segurel'].reset_main(colB)

st.set_page_config(layout="wide")

menu()
session.init_states()

if st.session_state['segurel'] is None and st.session_state['codifrance'] is None:
    st.switch_page("pages/acquisition.py")

if st.session_state['authentication_status']:

    if st.session_state['codifrance'] is not None:
        code_op = st.session_state['codifrance'].code_op
        date_op = st.session_state['codifrance'].date_op
    
    if st.session_state['segurel'] is not None:
        code_op = st.session_state['segurel'].code_op
        date_op = st.session_state['segurel'].date_op


    col1, col2 = st.columns([12,4])
    col2.image('ressources/Francap.png', use_container_width='auto')
    col1.header(f"Données : {code_op}", divider = True, anchor = False)
    col1.subheader(f"{date_op}", divider = True, anchor = False)

   
    colA, colB = st.columns([1,1])

    if st.session_state['codifrance'] is not None:
        colA.download_button(
                   label=f":material/download: SAISIE_CODIFRANCE_OP{st.session_state['codifrance'].code_op[2:]}.xlsx", 
                   data= st.session_state['codifrance'].set_excel_file(io.BytesIO()),
                   file_name=f"SAISIE_CODIFRANCE_OP{code_op[2:]}_{datetime.now()}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet/xlsx",
                   type = 'primary',
                   use_container_width = True, key=0)
    
    if st.session_state['segurel'] is not None:
        colB.download_button(
                   label=f":material/download: SAISIE_SEGUREL_OP{st.session_state['segurel'].code_op[2:]}.xlsx", 
                   data= st.session_state['segurel'].set_excel_file(io.BytesIO()),
                   file_name=f"SAISIE_SEGUREL_OP{st.session_state['segurel'].code_op[2:]}_{datetime.now()}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet/xlsx",
                   type = 'primary',
                   use_container_width = True, key =1)

    tab = st.tabs([":material/visibility: CODIFRANCE", ":material/visibility: SEGUREL"])


    with tab[0]:
        colA, colB = tab[0].columns([13,3])
        #colB.button(':material/bolt: Re-Traitements', on_click=click_calculate, args =(colB,), type="secondary", disabled=True, use_container_width=True,key=10000)
        if st.session_state['codifrance'] is not None:
            anychangecodi = dp.display_edit_dataframe(st, st.session_state.codifrance.main_df,1)

            if anychangecodi:
                 st.session_state['codifrance'].save(SAVING_FILE + 'codi.pkl')

    with tab[1]:
        colA, colB = tab[1].columns([13,3])
        #colB.button(':material/bolt: Re-Traitements', on_click=click_calculate, args =(colB,), type="secondary", disabled=True, use_container_width=True, key=50000)
        if st.session_state['segurel'] is not None:
            st.session_state.segurel.main_df, anychangesegu = dp.display_edit_dataframe(st, st.session_state.segurel.main_df,2)

            if anychangesegu:
                 st.session_state['segurel'].save(SAVING_FILE + 'segu.pkl')
    