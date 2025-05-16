import streamlit as st
import login as log

import os, sys
from dotenv import load_dotenv

from menu import menu
import session
import locale
from datetime import datetime, timedelta, date
import pandas as pd

sys.path.append('./Dependencies/')
import tool

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


load_dotenv()
CONFIG_FILE = os.getenv('CONFIG_FILE')

st.set_page_config(layout="wide")
#log.login()
menu()

session.init_states()


def on_change_matrice():
    pass

def click_save(categories, match_categories,match_mentions, mentions, marques, terroirs):
    with pd.ExcelWriter(CONFIG_FILE, engine='openpyxl') as writer:
        categories.to_excel(writer, sheet_name='CATEGORIES', index=False)
        match_categories.to_excel(writer, sheet_name='MATCH_CATEGORIE', index=False)
        match_mentions.to_excel(writer, sheet_name='MATCH_MENTION', index=False)
        mentions.to_excel(writer, sheet_name='MENTIONS', index=False)
        marques.to_excel(writer, sheet_name='MARQUES', index=False)
        terroirs.to_excel(writer, sheet_name='TERROIR', index=False)


def click_calculate(stcol):

    # Check if 'codifrance' exists in session state and is not None
    if 'codifrance' in st.session_state and st.session_state['codifrance'] is not None:
        st.session_state['codifrance'].reset_main(stcol)
    
    # Check if 'segurel' exists in session state and is not None
    if 'segurel' in st.session_state and st.session_state['segurel'] is not None:
        st.session_state['segurel'].reset_main(stcol)


    

if st.session_state['authentication_status']:
    coltitle, coledit, colbutton = st.columns([4,1,1])
    coltitle.info(" Le fichier ConfigFRA.xls est stocké dans le dossier _ESPIFIO", icon=":material/info:")
    modifiable = coledit.toggle(":material/edit: Edit matrice", value=False)
    
    coltitle.subheader('Configuration', divider = True, anchor = False)

    sheet_names = tool.get_sheet_names(CONFIG_FILE) #list G20 CONFIG Excel FILE sheets
    config_df_dict = {key: pd.read_excel(CONFIG_FILE, sheet_name= key , header=0)  for key in sheet_names}

    tab = st.tabs(['LISTES (Mentions, Categories et Terroirs)', 'CAS PARTICULIERS',  'CORRECTION des Marques' ])


#TAB CATEGORIE ET TERRIRS ####################################################################################
    col1, col2, col3 = tab[0].columns([1,1,1])

#################################################
    col1.subheader('MENTIONS', divider = True)
    if modifiable:
        mention = col1.data_editor(config_df_dict.get('MENTIONS'), on_change = on_change_matrice, num_rows="dynamic",  hide_index = True)
    else:
        col1.dataframe(config_df_dict.get('MENTIONS'),hide_index = True)

#################################################
    col2.subheader('CATEGORIES', divider = True)
    column_config={
        'CATEGORIE': st.column_config.TextColumn(None, help="", width= None),
        'MENTION' : st.column_config.SelectboxColumn(None, help="", width= None, 
                                                    required=False, 
                                                    default= '', 
                                                    options = config_df_dict.get('MENTIONS')['MENTION'].tolist() + [''])
    }
    if modifiable:
        categories = col2.data_editor(config_df_dict.get('CATEGORIES'),column_config= column_config, on_change = on_change_matrice,\
                                       num_rows="dynamic",  hide_index = True, height = 500)
    else:
        col2.dataframe(config_df_dict.get('CATEGORIES'),column_config= column_config, hide_index = True, height = 500)
    

    col3.subheader('TERROIR', divider = True)
    if modifiable:
        terroirs = col3.data_editor(config_df_dict.get('TERROIR'), on_change = on_change_matrice, num_rows="dynamic",  hide_index = True)
    else:
        col3.dataframe(config_df_dict.get('TERROIR'),hide_index = True)


    col1,col2 = tab[1].columns([1,1])
    #################################################
    col1.subheader('INTULES/CATEGORIES', divider = True)
    column_config={
            'INTITULE': st.column_config.TextColumn(None, help="", width= None),
            'CATEGORIE' : st.column_config.SelectboxColumn(None, help="", width= None, 
                                                           required=True, 
                                                           default= None, 
                                                           options = config_df_dict.get('CATEGORIES')['CATEGORIE'].tolist())
        }

    if modifiable:
        match_categorie = col1.data_editor(config_df_dict.get('MATCH_CATEGORIE'),column_config= column_config,
                                            on_change = on_change_matrice, num_rows="dynamic",  hide_index = True)
    else:
        col1.dataframe(config_df_dict.get('MATCH_CATEGORIE'),
                       column_config= column_config,
                       hide_index = True)

    col2.subheader('INTULES/MENTIONS', divider = True)
    column_config={
        'INTITULE': st.column_config.TextColumn(None, help="", width= None),
        'MENTION' : st.column_config.SelectboxColumn(None, help="", width= None, 
                                                       required=True, 
                                                       default= None, 
                                                       options = config_df_dict.get('MENTIONS')['MENTION'].tolist())
    }

    if modifiable:
        match_mention = col2.data_editor(config_df_dict.get('MATCH_MENTION'),column_config= column_config,
                                            on_change = on_change_matrice, num_rows="dynamic",  hide_index = True)
    else:
        col2.dataframe(config_df_dict.get('MATCH_MENTION'),
                       column_config= column_config,
                       hide_index = True)












#TAB CORRECTIONS####################################################################################
    col1,col2 = tab[2].columns([10,1])
    col1.subheader('MARQUES', divider = True)
    column_config={
        'Nom': st.column_config.TextColumn(None, help="", width= 300),
        'Correction' : st.column_config.TextColumn(None, help="", width= 300)
    }
    if modifiable:
        marques = col1.data_editor(config_df_dict.get('MARQUES'), on_change = on_change_matrice, num_rows="dynamic",  hide_index = True)
    else:
        col1.dataframe(config_df_dict.get('MARQUES'),hide_index = True)


############################ 
    if modifiable:
         colbutton.button(':material/save: Save', on_click=click_save, args =(categories, match_categorie,match_mention, mention, marques,terroirs), type="primary", disabled=False, use_container_width=True)
         colbutton.button(':material/bolt: Re-Traitements', on_click=click_calculate, args =(colbutton,), type="secondary", disabled=True, use_container_width=True)

