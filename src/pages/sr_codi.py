import streamlit as st
import login as log
import session
import sys, io, os
from datetime import datetime
sys.path.append('./Dependencies/')

from dotenv import load_dotenv
from menu import menu
import dataprocess as dp 
import codiprocess as cp

load_dotenv()
CONFIG_FILE = os.getenv('CONFIG_FILE')
SAVING_FILE = os.getenv('SAVING_FILE')
CONFIG_PATH = os.getenv('CONFIG_PATH')

st.set_page_config(layout="wide")

menu()
session.init_states()

if st.session_state['codifrance'] is not None:
    data= st.session_state['codifrance'].main_df
    data_g = cp.apply_sr_process(data)


    column_config = dp.col_config(st)

    st.header(f"Stop Rayon et Degroupements :", divider = True, anchor = False)
    st.image('ressources/CodiFrance.png', use_container_width='auto')
    
  
    
    default_col = ['CLE','SR','CATALOG','GENCOD','INTITULE','MARQUE','DESCRIPTIF']
    colonnes  = st.multiselect('Sélectionnez les colonnes à afficher', options = [item[0] for item in column_config.items() if item[1][2]], default = default_col,key=10001)
    edit_column_config = {item[0]: item[1][0] for item in column_config.items() if (item[0] in colonnes and item[1][2])}
    
    data_g[colonnes] = st.data_editor(data_g[colonnes] ,column_config = edit_column_config, 
                                    num_rows="dynamic",  hide_index = True, height=900)

   
   