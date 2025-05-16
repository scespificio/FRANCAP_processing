import streamlit as st
import sys, io, os, re
#import session
import pandas as pd
from datetime import datetime
import locale
import spacy
nlp = spacy.load("fr_core_news_md")

from sklearn.feature_extraction.text import TfidfVectorizer  # Pour la vectorisation TF-IDF
from sklearn.metrics.pairwise import cosine_similarity  # Pour le calcul de la similarité de cosinus
import numpy as np  # Pour le traitement des index et des tableaux

#locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
#session.init_states()

def add_minus_to_percentage(text):
    text = re.sub(r'\s+%', '%', text)
    pattern = r'(?<![-\d])(\d+(\.\d+)?%)'
    updated_text = re.sub(pattern, r'-\1', text)     # Ajouter un "-" devant les pourcentages détectés
    return updated_text

def isnull(x):
    if x is None:
        return True
    elif isinstance(x, float) and (np.isnan(x) or x==0):
        return True
    elif isinstance(x, int) and (np.isnan(x) or x==0):
        return True
    elif isinstance(x,str):
        return x.strip()==''
    else:
        return False

def extract_dates(date_range: str):
    # Utilisation d'une expression régulière pour capturer les dates au format dd/mm/yyyy
    date_pattern = r'(\d{2}/\d{2}/\d{4})'
    dates = re.findall(date_pattern, date_range)

    # Vérification si deux dates ont bien été trouvées
    if len(dates) != 2:
        raise ValueError("Le format de l'intervalle de dates n'est pas valide. Assurez-vous d'avoir 'dd/mm/yyyy au dd/mm/yyyy'.")

    # Conversion des dates en objets datetime
    start_date = datetime.strptime(dates[0], "%d/%m/%Y")
    end_date = datetime.strptime(dates[1], "%d/%m/%Y")

    return (start_date, end_date)

def get_d_label(d):
    if d[0].year == d[1].year:
        if d[0].month == d[1].month:
            return f"Du {d[0].day} au {d[1].day} {d[0].strftime('%B')} {d[0].year}"
        else:
            return f"Du {d[0].day} {d[0].strftime('%B')} au {d[1].day} {d[1].strftime('%B')} {d[0].year}"
    else:
        return f"Du {d[0].day} {d[0].strftime('%B')} {d[0].year} au {d[1].day} {d[1].strftime('%B')} {d[1].year}"

def set_month_in_french(texte):
    mois_traduction = {
        "January": "Janvier",
        "February": "Février",
        "March": "Mars",
        "April": "Avril",
        "May": "Mai",
        "June": "Juin",
        "July": "Juillet",
        "August": "Août",
        "September": "Septembre",
        "October": "Octobre",
        "November": "Novembre",
        "December": "Décembre"
    }
    
    # Remplacer chaque mois anglais par sa traduction française
    for mois_anglais, mois_francais in mois_traduction.items():
        texte = texte.replace(mois_anglais, mois_francais)

    return texte

    
def split_descriptions(text):
    # Définition des séparateurs à utiliser : 'ou' ou 'Existe aussi en'
    separators = r"[oO]u en|[eE]xiste aussi en|\b[Oo]u\b|(?<!\d),(?!\d)"

    # Utilisation de re.split pour diviser le texte selon les séparateurs définis
    split_result = re.split(separators, text)
    split_result = [part.capitalize() for part in split_result if part]

    #if '\n' in text:
    if any(('\n' in element and not element.endswith('\n')) for element in split_result):
        pattern = r'(\d+(?:[\.,]\d+)?)\s(cm|g|mg|ml|cl|l|kg)|\sx\s*(\d+(?:\,\d+)?)'
        id = next((i for i, split in enumerate(split_result) if ('\n' in split and re.search(pattern,split))))
        contenant = '\n'.join(split_result[id].split('\n')[1:])
        split_result[id] = split_result[id].split('\n')[0]
        result = []
        matches = re.findall(pattern, contenant)
        if matches[0][0] != '':
            contenant = contenant.replace(matches[0][0],'').replace(matches[0][1],'').strip()
            default_size = matches[0][0] + ' ' + matches[0][1]
        elif matches[0][2] != '':
            contenant = contenant.replace('x ','').replace(matches[0][2],'')
            default_size = 'x ' + matches[0][2]

        for i, part in enumerate(split_result):
            matches = re.findall(pattern, part)

            if len(matches) !=0:
                if matches[0][0] != '':
                    result.append(f'{contenant} {matches[0][0]} {matches[0][1]}')
                elif matches[0][2] != '':
                    result.append(f'{contenant}x {matches[0][2]}')
            else:
                result.append(f'{contenant}x {default_size}')           
        return [(part.strip()+'\n'+res).capitalize() for part, res in zip(split_result, result)]
    else:
        return split_result
    
def split_pxkl(text):
    separators = r"[sS]oit "
    split_result = re.split(separators, text)
    return ['Soit '+ part for part in split_result if part]

def split_pxkllv(text):
    separators = r"[lL]es "
    split_result = re.split(separators, text)
    return ['Les '+ part for part in split_result if part]


def split_photos(x):
    gencod = r"(?<!\d)\d{8,13}(?!\d)"

    match_gen = re.findall(gencod, x.GENCOD)
    if isnull(x.DESCRIPTIF):
        x.DESCRIPTIF = ''

    match_desc = re.findall(gencod, x.DESCRIPTIF)

    if len(match_desc) > 0 :
        return match_desc, match_gen[0]
    else:
        return match_gen, match_gen[0]
    

def process_log(status, status_txt, txt):
    status_txt.append(txt)
    if status is not None:
        status.write(txt)
    return status, status_txt

def get_sheet_names(file_path):
    # Ouvrir le fichier Excel
    excel_file = pd.ExcelFile(file_path)
    # Extraire la liste des feuilles
    sheet_names = excel_file.sheet_names
    return sheet_names


def on_change_matrice(id):
    if id == 0:
        st.session_state['change_count_francap'] += 1
    elif id == 1:
        st.session_state['change_count_codifrance'] += 1
    else:
        st.session_state['change_count_segurel'] += 1


def lemmatiser_texte_spacy(texte):
    """
    Lemmatisation du texte en utilisant le modèle linguistique de `spaCy`.
    
    Args:
    texte (str): Le texte à lemmatiser.
    
    Retourne:
    str: Le texte lemmatisé.
    """

    doc = nlp(texte.lower())  # Conversion en minuscules et traitement avec spacy
    tokens_lemmatise = [token.lemma_ for token in doc if token.is_alpha]  # Lemmatiser et filtrer les mots alphabétiques
    return " ".join(tokens_lemmatise)

def texte_le_plus_similaire_tfidf_spacy(texte, liste_textes):
    """
    Trouve l'élément textuel le plus similaire dans une liste de textes en utilisant `TfidfVectorizer` et `spaCy`.
    
    Args:
    texte (str): Le texte de référence.
    liste_textes (list): La liste des textes dans laquelle chercher la similarité.
    
    Retourne:
    str: L'élément textuel de la liste le plus similaire.
    """
    if not liste_textes:
        return "La liste des textes est vide."

    # Lemmatisation des textes avec spaCy
    texte_lemmatise = lemmatiser_texte_spacy(texte)  # Lemmatisation du texte de référence
    liste_textes_lemmatisees = [lemmatiser_texte_spacy(t) for t in liste_textes]  # Lemmatisation des candidats
 
    
    # Ajoute le texte de référence à la liste pour la vectorisation
    textes = [texte_lemmatise] + liste_textes_lemmatisees
    
    # Initialisation du TfidfVectorizer
    vecteur = TfidfVectorizer()
    
    # Calcul des vecteurs TF-IDF pour tous les textes
    tfidf_matrix = vecteur.fit_transform(textes)
    
    # Calcul de la similarité de cosinus entre le texte de référence (index 0) et les autres
    similarites = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Trouver l'index de la phrase la plus similaire
    index_similaire = np.argmax(similarites)
    
    # Retourne l'élément de la liste correspondant
    return liste_textes[index_similaire]  if np.max(similarites)> 0.1 else None# Utiliser la liste originale pour conserver la casse d'origine

@st.fragment
def frag_download_button(label, data, file_name, type):
    st.download_button(
               label=label, 
               data= data,
               file_name= file_name,
               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet/xlsx",
               type = type,
               use_container_width = True)


class ProgressBar:
    def __init__(self, st, size, text):
        self.size = size
        self.cnt = 0
        self.bar = st.progress(0)
        self.text = text

    def increment(self):
        self.cnt += 1

    def display(self,nb = None):
        if nb is None:
            self.bar.progress(min(1,self.cnt / self.size), text = self.text)
        else:
            self.bar.progress(nb, text = self.text)



            