import streamlit as st
import login as log
import session
import sys, io, os
from datetime import datetime
sys.path.append('./Dependencies/')
from origine import decode_origine
import tool
import dataprocess as dp 
import pandas as pd

from dotenv import load_dotenv
from menu import menu

load_dotenv()
CONFIG_FILE = os.getenv('CONFIG_FILE')
SAVING_FILE = os.getenv('SAVING_FILE')
CONFIG_PATH = os.getenv('CONFIG_PATH')

import pandas as pd

st.set_page_config(layout="wide")
menu()
session.init_states()

def change_origine(df_source, source_col, df_mapping, mapping_col, replacement_col):
    mapping_dict = df_mapping.set_index(mapping_col)[replacement_col].to_dict()
    df_source[source_col] = df_source[source_col].map(mapping_dict).fillna(df_source[source_col]) 
    return df_source

def apply_correction(df_source_l, df):
    st.session_state['codifrance'].main_df = change_origine(df_source_l[0], 'ORIGINE',df[df.VALID], 'ORIGINE','CALCULE')
    st.session_state['segurel'].main_df = change_origine(df_source_l[1], 'ORIGINE',df[df.VALID], 'ORIGINE','CALCULE')


if st.session_state['segurel'] is None or st.session_state['codifrance'] is None:
    st.switch_page("pages/acquisition.py")

if st.session_state['authentication_status']:
    
    
    
    column_config={
            'ORIGINE' : st.column_config.TextColumn(None, help="", width= 400, disabled = True),
            'CALCULE' : st.column_config.TextColumn(None, help="", width= 400, required=True),
            'VALID' : st.column_config.CheckboxColumn(None, help="", width= 100, required=True)
            }

    # creation du df ORIGINE
    origine = list(pd.concat([st.session_state['codifrance'].main_df.ORIGINE,
                              st.session_state['segurel'].main_df.ORIGINE ]).unique())
    if "" in origine:
        origine.remove("")
    calcul = [decode_origine(str(item),None) for item in origine]
    valid = [ True if calc == item else False for item, calc in zip(origine, calcul)]
    
    df = pd.DataFrame({'ORIGINE': origine,
                       'CALCULE': calcul,
                       'VALID': valid}).dropna(subset=['ORIGINE'])
    # Optionally enforce specific dtypes for each column
    df = df.astype({
        'ORIGINE': 'string',  # String dtype for ORIGINE
        'CALCULE': 'string',  # String dtype for CALCULE
        'VALID': 'bool'       # Boolean dtype for VALID
    })

    c1 = st.container()

    st.header(f"{st.session_state['segurel'].code_op} {len(df)} origines différentes", divider = True, anchor = False)

    df = st.data_editor(df ,column_config = column_config, num_rows="fixed", hide_index = True, height=600)

    c1.button(':material/bolt: Appliquer', on_click=apply_correction, 
              args =([st.session_state['codifrance'].main_df, st.session_state['segurel'].main_df],df[df.VALID]),
              type="primary", use_container_width=True,key=10000)





def display_edit_dataframe(st, df, id):

    def on_change_matrix():
        return df, True
    
    colmultiselect, coledit = st.columns([13,3])

    image_dict = {0:'static/Francap.png', 1:'static/codifrance.png', 2:'static/segurel.png'} 

    column_config= col_config(st)

    codi_col = output_col('CODI') 
    segu_col = output_col('SEGU')
    
    segu_config = {key : val for key, val in column_config.items() if key in segu_col}
    codi_config = {key : val for key, val in column_config.items() if key in codi_col}

    if id == 1:
        column_config = codi_config
        
    else:
        column_config = segu_config

    modifiable = coledit.toggle(":material/edit: Edit matrice", value=False, key=(id+1)*100)
    if not modifiable:
         default_col = ['ISFROM_LOGO','GENCOD','INTITULE','CATEGORIE','MARQUE','DESCRIPTIF', 'MENTION SPECIFIQUE']
         colonnes  = colmultiselect.multiselect('Sélectionnez les colonnes à afficher',
                                         options = [item[0] for item in column_config.items() if item[1][1]], default = default_col,key=(id+1)*10 )
         fix_column_config = {item[0]: item[1][0] for item in column_config.items() if (item[0] in colonnes and item[1][1])}
        # st.warning( [item[0] for item in column_config.items() if item[1][1]])
         st.dataframe(df[colonnes], column_config = fix_column_config, hide_index = True, height=800)  
         return df, False
    else:
         default_col = ['GENCOD','INTITULE','CATEGORIE','MARQUE','DESCRIPTIF', 'MENTION SPECIFIQUE']
         colonnes  = colmultiselect.multiselect('Sélectionnez les colonnes à afficher',
                                         options = [item[0] for item in column_config.items() if item[1][2]], default = default_col,key=(id+1)*10)
         edit_column_config = {item[0]: item[1][0] for item in column_config.items() if (item[0] in colonnes and item[1][2])}
         df[colonnes] = st.data_editor(df[colonnes] ,column_config = edit_column_config, on_change = on_change_matrix, num_rows="dynamic",  hide_index = True, height=900)
         return df, False
    
  




    