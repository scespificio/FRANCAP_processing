import streamlit as st
import login as log
import sys, io, os
from datetime import datetime, timedelta, date
import locale
from dotenv import load_dotenv
import pickle
import time


from menu import menu
import pandas as pd

sys.path.append('./Dependencies/')

import session
import tool
from op import Codifrance, Segurel

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.set_page_config(layout="wide")
menu()
session.init_states()

acquisition_type_dict = {"1. Charger un projet à partir des listes clients" : 'new'}


load_dotenv('../.env')
SAVING_FILE = os.getenv('SAVING_FILE')

ready2downloadcodi, ready2downloadsegu = False, False

if st.session_state['authentication_status']:   ## execute only on authentification.
    
    ######################################## SET PAGINATION
    st.header('Acquisition des données', divider = True, anchor = False)
    #colreset.button(':material/refresh:', help = 'Réinitialise tout le traitement', on_click = session.reset, args=[st,])
    if os.path.exists(SAVING_FILE + 'segu.pkl'):
        try:
            with open(SAVING_FILE + 'segu.pkl', 'rb') as file:
                segurel = pickle.load(file)
                projet_name = f'{segurel.code_op} {segurel.date_op}'
        except Exception as e:
            print(f'echec dans la récuperation du projet_id / ouverture object segurel: {e}')
            projet_name = 'inderterminé'

        acquisition_type_dict[f"2. Continuer avec les données sauvegardées du projet en cours {projet_name}"] = 'keepgoing'
        acquisition_type_dict[f"3. Charger une mise à jours des données du projet en cours {projet_name}"] = 'update'

        st.info(f'Le projet {projet_name} est sauvegardé.', icon="ℹ️")

        acquisition_type_label = st.selectbox("Quelle type d'acquisition souhaitée vous faire?", list(acquisition_type_dict.keys()),index=None)
        acquisition_type = acquisition_type_dict.get(acquisition_type_label)
    else:
        acquisition_type_label, acquisition_type  = next(iter(acquisition_type_dict.items()))
        
    if acquisition_type_label is not None:
        st.subheader(acquisition_type_label, divider = True, anchor = False)

    if acquisition_type == 'new':    #################################################   1. Charger les listes clients"
       
        with st.expander(":heavy_exclamation_mark: Précautions d'utilisation"): ##################### PRECAUTION D4UTILISATION
            st.markdown('''
                :one: La feuille de données de la liste Francap doit s'appeler:
                     \n- A
            ''')
            st.warning('''
                :two: La feuille de données de la liste Codifrance doit s'appeler:
                       \n- FINALE
            ''')            
            st.markdown('''
                :three: Les feuilles de données de la liste Segurel doivent s'appeler:
                        \n- COCCINELLE agence
                        \n- CMK agence
                        \n- EP
            ''')
            st.warning('''
                :four: La feuille EP définit les Encart Produits Segurel. Elle doit être listée dans un tableau unique avec une colonne 'pageligne', comme dans l'image ci-dessous:
            ''')
            st.image('ressources/EP.png', use_container_width='auto')
            #st.image('ressources/EP.png', use_column_width='auto')
    
    
        #francap_file = st.file_uploader(label = ":one: Importer la liste Francap",type=['xls','xlsx','xlsm'], 
        #                                     on_change=None, args=None)

        colA, colB, colC = st.columns([2,1,1])   
        cb, cc = colB.container(border=True), colC.container(border=True) 
        col1, col2 = st.columns([1,1])     
        c1, c2 = col1.container(border=True), col2.container(border=True),  
        col = st.columns([1])[0]
        col3, col4 = st.columns([1,1])    

        code_op = cb.text_input( ":one: Entrer le code OP", max_chars= 30, key = 'Input',
                            help = 'ex: 12 OP12', placeholder= 'PRyy##')
        code_op_isvalid = len(code_op)==6 and code_op[:2]=='PR' and code_op[2:].isdigit()
        if not code_op_isvalid and code_op != '':
            cb.warning('code op invalide. Veuillez le ressaisir')     

 ######################################## PERIOD WIDGET
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        inamonth = datetime.now() + timedelta(days=40)
        next_week = inamonth + timedelta(days=7)
           
        period = cc.date_input(
                            ":two: Sélectionner la période de l'opération",
                            value = (datetime.now() + timedelta(days=40), datetime.now() + timedelta(days=52)),
                            min_value = date(2020, 1, 1),
                            max_value = date(datetime.now().year + 1, 12, 31),
                            format="DD.MM.YYYY",
                            help= 'selectionner une date de debut et une date de fin')
        
        dateisvalid = len(period)>1

        if not len(period)>1:
            cc.warning("Veuillez entrez au moins deux dates")

        codi_file = c1.file_uploader(label = ":two: Importer la liste Codifrance",type=['xls','xlsx','xlsm'], 
                                             on_change=None, args=None)

        segu_file = c2.file_uploader(label = ":three: Importer la liste Segurel",type=['xls','xlsx','xlsm'], 
                                         on_change=None, args=None, disabled = False)

        ready2processCodi = codi_file is not None
        ready2processSegu = segu_file is not None and code_op_isvalid and dateisvalid
        label =f"Du {period[0].strftime('%d/%m/%Y')} au {period[1].strftime('%d/%m/%Y')}"

        if ready2processSegu:
            print(f'ACQUISITION DE NOUVELLES DONNEES SEGUREL par {st.session_state.name}, le {datetime.now()}')
            segurel = Segurel()
            segurel.code_op = code_op
            segurel.date_op = f"Du {period[0].strftime('%d/%m/%Y')} au {period[1].strftime('%d/%m/%Y')}"
            segurel.get_new_list_from_customer(segu_file)
            segurel.init_main(col2)
            segurel.set_main(col2)
            log = segurel.save(SAVING_FILE + 'segu.pkl')
            st.session_state['segurel'] = segurel
            print(f'sauvegarde object Segurel: {log}')
            ready2downloadsegu = True

        if ready2processCodi:
            print(f'ACQUISITION DE NOUVELLES DONNEES CODIFRANCE par {st.session_state.name}, le {datetime.now()}')
            codifrance = Codifrance()
            codifrance.get_new_list_from_customer(codi_file)
            codifrance.set_main(col1)
            log = codifrance.save(SAVING_FILE + 'codi.pkl')
            st.session_state['codifrance'] = codifrance
            print(f'sauvegarde object codifrance: {log}')
            ready2downloadcodi = True

    elif acquisition_type == 'keepgoing':
        print(f'CHARGEMENT DES DONNEES SAUVEGARDEES par {st.session_state.name}, le {datetime.now()}')
        try:
            with open(SAVING_FILE + 'segu.pkl', 'rb') as file:  
                st.session_state['segurel'] = pickle.load(file)
                print(f'Chargement object Segurel: ok')
        except Exception as e:
            print(f'Chargement object Segurel: {e}')
            st.exception(e)

        try:
            with open(SAVING_FILE + 'codi.pkl', 'rb') as file:
                st.session_state['codifrance'] = pickle.load(file)
                print(f'Chargement object Codifrance: ok')
        except Exception as e:
            print(f'Chargement object Codifrance: {e}')
            st.exception(e)

        

        time.sleep(2)
        st.switch_page("pages/visualisation.py")


    elif acquisition_type == 'update':

        try:
            with open(SAVING_FILE + 'segu.pkl', 'rb') as file:
                st.session_state['segurel'] = pickle.load(file)
                print(f'Chargement object Segurel: ok')
        except Exception as e:
            print(f'Chargement object Segurel: {e}')
            st.exception(e)

        try:
            with open(SAVING_FILE + 'codi.pkl', 'rb') as file:
                st.session_state['codifrance'] = pickle.load(file)
                print(f'Chargement object Codifrance: ok')
        except Exception as e:
            print(f'Chargement object Codifrance: {e}')
            st.exception(e)

        col1, col2 = st.columns([1,1])     
        c1, c2 = col1.container(border=True), col2.container(border=True),  

        codi_update = c1.file_uploader(label = "CODIFRANCE: Importer la mise à jour ",type=['xls','xlsx'], 
                                             on_change=None, args=None)

        segu_update = c2.file_uploader(label = "SEGUREL: Importer la mise à jour",type=['xls','xlsx'], 
                                         on_change=None, args=None)
        
        if codi_update is not None:
            st.session_state['codifrance'].main_df = pd.read_excel(codi_update, sheet_name=0, header=0)
            #st.session_state['codifrance'].reset_main(col1)
            st.session_state['codifrance'].main_df[st.session_state['codifrance'].main_df['GENCOD'].notna() & (st.session_state['codifrance'].main_df['GENCOD'] != '')]
            log = st.session_state['codifrance'].save(SAVING_FILE + 'codi.pkl')

            log = st.session_state['segurel'].save(SAVING_FILE + 'segu.pkl')
            ready2downloadcodi = True

        if segu_update is not None:
            st.session_state['segurel'].main_df = pd.read_excel(segu_update, sheet_name=0, header=0)

            ready2downloadsegu = True

    if acquisition_type is not None:

        col1, col2 = st.columns([1,1])     
        c1, c2 = col1.container(border=True), col2.container(border=True),

        if ready2downloadcodi:
            c1.success(f":heavy_check_mark: Données Codifrance dans SAISIE_CODIFRANCE_OP{st.session_state['codifrance'].code_op[2:]}.xlsx")
            
        if ready2downloadsegu:
            c2.success(f":heavy_check_mark: Données Segurel  dans SAISIE_CODIFRANCE_OP{st.session_state['segurel'].code_op[2:]}")

        if ready2downloadsegu or ready2downloadcodi:
            time.sleep(2)
            st.switch_page("pages/visualisation.py")


