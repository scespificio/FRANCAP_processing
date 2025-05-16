import pandas as pd
import re, os
import numpy as np
import tool
import nlptools as nlpt

from dotenv import load_dotenv
from spellchecker import SpellChecker
pd.options.mode.copy_on_write = True

load_dotenv()
CONFIG_FILE = os.getenv('CONFIG_FILE')
SAVING_FILE = os.getenv('SAVING_FILE')
CONFIG_PATH = os.getenv('CONFIG_PATH')
#CONFIG_FILE = 'ConfigFRA.xlsx'
DEPARTEMENTS = pd.read_csv(CONFIG_PATH + '/' + 'departements_francais.csv').nom.to_list()
PAYS = pd.read_csv(CONFIG_PATH + '/' + 'liste_pays_fr.csv').nom.to_list()

def output_col(process):
    liste = ['ISFROM_LOGO','CLE', 'CODE OP','DATE OP','MENTION SPECIFIQUE','CATEGORIE','INTITULE','GENCOD','MARQUE','ORIGINE','MECAPROMO','RONDE DES MARQUES',
             'DESCRIPTIF','PRIX AU KG','PVC MAXI','BONUS', 'BONUS EN %', 'RI EN €','RI EN %','PVC NET','LOT VIRTUEL','PRIX AU KG DU LOT VIRTUEL',
             'MARKET_DESCRIPTIF', 'MARKET_PRIX AU KG', 'MARKET_PVC_MAXI', 'MARKET_BONUS','MARKET_BONUS EN %', 'MARKET_RI EN €', 'MARKET_RI EN %', 'MARKET_PVC NET', 'MARKET_LOT VIRTUEL', 'MARKET_PRIX AU KG DU LOT VIRTUEL',
             'FORMAT GV','FORMAT MV','FORMAT MVK','FORMAT PV','PRODUIT DE UNE','PRODUIT EN DER',
             'MISE EN AVANT','VIDE_2','PICTO','SR','SR_SEGU_MARKET','CATALOG','CATALOG_MARKET','AFFICHE','SELECTION FRANCAP','SELECTION CODIFRANCE', 'SELECTION SEGUREL','INFO COMPLEMENTAIRES', 'MARKET_INFO COMPLEMENTAIRES','PHOTO1','PHOTO2','PHOTO3','PHOTO4','PHOTO5','PHOTO6','PHOTO7','PHOTO8','DESCRIPTIF_2','PRIX AU KG_2',
             'PRIX AU KG DU LOT VIRTUEL_2','DESCRIPTIF_3','PRIX AU KG_3','PRIX AU KG DU LOT VIRTUEL_3','DESCRIPTIF_4','PRIX AU KG_4','PRIX AU KG DU LOT VIRTUEL_4','DESCRIPTIF_5',
             'PRIX AU KG_5','PRIX AU KG DU LOT VIRTUEL_5','DESCRIPTIF_6','PRIX AU KG_6','PRIX AU KG DU LOT VIRTUEL_6',
             'MARKET_DESCRIPTIF_2','MARKET_PRIX AU KG_2', 'MARKET_PRIX AU KG DU LOT VIRTUEL_2',
             'MARKET_DESCRIPTIF_3','MARKET_PRIX AU KG_3', 'MARKET_PRIX AU KG DU LOT VIRTUEL_3',
             'MARKET_DESCRIPTIF_4','MARKET_PRIX AU KG_4', 'MARKET_PRIX AU KG DU LOT VIRTUEL_4',
             'MARKET_DESCRIPTIF_5','MARKET_PRIX AU KG_5', 'MARKET_PRIX AU KG DU LOT VIRTUEL_5',
             'MARKET_DESCRIPTIF_6','MARKET_PRIX AU KG_6', 'MARKET_PRIX AU KG DU LOT VIRTUEL_6',
             'SUPER_Page', 'SUPER_Rang','SUPER_Case','EXPRESS_Page','EXPRESS_Rang','EXPRESS_Case','MARKET_Page','MARKET_Rang','MARKET_Case','REGIO_Page','REGIO_Rang','REGIO_Case','SUPER_WP','EXPRESS_WP','MARKET_WP'
            ] 
    if process == 'CODI':
        remove_list = ['SELECTION SEGUREL', 'MARKET_DESCRIPTIF', 'MARKET_PRIX AU KG', 'MARKET_PVC_MAXI', 'MARKET_BONUS','MARKET_BONUS EN %', 'MARKET_RI EN €', 'MARKET_RI EN %', 'MARKET_PVC NET', 'MARKET_LOT VIRTUEL', 'MARKET_PRIX AU KG DU LOT VIRTUEL',
                    'SR_SEGU_MARKET','MARKET_DESCRIPTIF_2','MARKET_PRIX AU KG_2', 'MARKET_PRIX AU KG DU LOT VIRTUEL_2',
             'MARKET_DESCRIPTIF_3','MARKET_PRIX AU KG_3', 'MARKET_PRIX AU KG DU LOT VIRTUEL_3',
             'MARKET_DESCRIPTIF_4','MARKET_PRIX AU KG_4', 'MARKET_PRIX AU KG DU LOT VIRTUEL_4',
             'MARKET_DESCRIPTIF_5','MARKET_PRIX AU KG_5', 'MARKET_PRIX AU KG DU LOT VIRTUEL_5',
             'MARKET_DESCRIPTIF_6','MARKET_PRIX AU KG_6', 'MARKET_PRIX AU KG DU LOT VIRTUEL_6',
             'MARKET_INFO COMPLEMENTAIRES']
        for rem in remove_list:
            liste.remove(rem)
    elif process == 'SEGU':
        remove_list = ['SELECTION CODIFRANCE','FORMAT PV','CATALOG_MARKET']
        for rem in remove_list:
            liste.remove(rem)
    elif process == 'SEGU_M':
        remove_list = ['SELECTION CODIFRANCE','INFO COMPLEMENTAIRES','PHOTO2','PHOTO3','PHOTO4','PHOTO5','PHOTO6','PHOTO7','PHOTO8','DESCRIPTIF_5',
            'PRIX AU KG_5','PRIX AU KG DU LOT VIRTUEL_5','DESCRIPTIF_6','PRIX AU KG_6','PRIX AU KG DU LOT VIRTUEL_6','SUPER_Page','SR_SEGU_MARKET',
            'SUPER_Rang','SUPER_Case','EXPRESS_Page','EXPRESS_Rang','EXPRESS_Case','MARKET_Page','MARKET_Rang','MARKET_Case','REGIO_Page','REGIO_Rang','REGIO_Case','SUPER_WP','EXPRESS_WP','MARKET_WP',
            'MARKET_DESCRIPTIF', 'MARKET_PRIX AU KG', 'MARKET_PVC_MAXI', 'MARKET_BONUS','MARKET_BONUS EN %', 'MARKET_RI EN €', 'MARKET_RI EN %', 'MARKET_PVC NET', 'MARKET_LOT VIRTUEL',
            'MARKET_PRIX AU KG DU LOT VIRTUEL', 'ISFROM_LOGO', 'CLE', 'MECAPROMO','FORMAT PV', 'VIDE_2', 'PHOTO1','CATALOG_MARKET',
            'MARKET_DESCRIPTIF_2','MARKET_PRIX AU KG_2', 'MARKET_PRIX AU KG DU LOT VIRTUEL_2',
            'MARKET_DESCRIPTIF_3','MARKET_PRIX AU KG_3', 'MARKET_PRIX AU KG DU LOT VIRTUEL_3',
            'MARKET_DESCRIPTIF_4','MARKET_PRIX AU KG_4', 'MARKET_PRIX AU KG DU LOT VIRTUEL_4',
            'MARKET_DESCRIPTIF_5','MARKET_PRIX AU KG_5', 'MARKET_PRIX AU KG DU LOT VIRTUEL_5',
            'MARKET_DESCRIPTIF_6','MARKET_PRIX AU KG_6', 'MARKET_PRIX AU KG DU LOT VIRTUEL_6',
            'MARKET_INFO COMPLEMENTAIRES']
        for rem in remove_list:
            liste.remove(rem)
    return liste
    
def col_bool(process):
    liste = ['FORMAT GV','FORMAT MV','FORMAT MVK','FORMAT PV','MISE EN AVANT','RONDE DES MARQUES','SELECTION FRANCAP','SELECTION CODIFRANCE','SELECTION SEGUREL','SR','MISE EN AVANT', 'CATALOG','CATALOG_MARKET']
    if process == 'CODI':
        liste.remove('SELECTION SEGUREL')
    elif process == 'SEGU':
        remove_list = ('SELECTION CODIFRANCE','FORMAT PV','CATALOG_MARKET')
        for rem in remove_list:
            liste.remove(rem)
    elif process == 'SEGU_M':
        remove_list = ['SELECTION CODIFRANCE','FORMAT GV','FORMAT MV','FORMAT PV', 'RONDE DES MARQUES','CATALOG_MARKET']
        for rem in remove_list:
            liste.remove(rem)
    return liste


def col_config(st):

    sheet_names = tool.get_sheet_names(CONFIG_FILE) #list G20 CONFIG Excel FILE sheets
    config_df_dict = {key: pd.read_excel(CONFIG_FILE, sheet_name= key , header=0)  for key in sheet_names}

    column_config={
        'ISFROM_LOGO': (st.column_config.ImageColumn('Produit', help="", width= None), True, False),
        'PHOTO1_PATH': (st.column_config.ImageColumn('Photo', help="", width= None), True, False),
        'CLE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'CODE OP' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'DATE OP' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'MENTION SPECIFIQUE' : (st.column_config.SelectboxColumn(None, help="", width= None, required=False, default= '', options = config_df_dict.get('MENTIONS')['MENTION'].tolist() + ['']), True, True),
        'CATEGORIE' : (st.column_config.SelectboxColumn(None, help="", width= None, required=True, default= None, options = config_df_dict.get('CATEGORIES')['CATEGORIE'].tolist() ), True, True),
        'INTITULE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'GENCOD' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'MARQUE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'ORIGINE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PVC MAXI' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'BONUS' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'BONUS EN %' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'RI EN €' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'RI EN %' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PVC NET' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'LOT VIRTUEL' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'RONDE DES MARQUES' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'FORMAT GV' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'FORMAT MV' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'FORMAT MVK' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'FORMAT PV' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'PRODUIT DE UNE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRODUIT EN DER' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MISE EN AVANT' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'PICTO' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SR' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'CATALOG' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'AFFICHE' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SELECTION FRANCAP' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'SELECTION CODIFRANCE' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'SELECTION SEGUREL' : (st.column_config.CheckboxColumn(None, help="", width= None, required=True), True, True),
        'INFO COMPLEMENTAIRES' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PHOTO1' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO2' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO3' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO4' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO5' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO6' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO7' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PHOTO8' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF_2' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PRIX AU KG_2' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL_2' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF_3' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PRIX AU KG_3' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL_3' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF_4' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PRIX AU KG_4' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL_4' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF_5' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PRIX AU KG_5' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL_5' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'DESCRIPTIF_6' : (st.column_config.TextColumn(None, help="", width= None, required=True), True, True),
        'PRIX AU KG_6' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'PRIX AU KG DU LOT VIRTUEL_6' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_INFO COMPLEMENTAIRES': (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PVC_MAXI' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_BONUS' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_BONUS EN %' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_RI EN €' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_RI EN %' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PVC NET' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_LOT VIRTUEL' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF_2' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG_2' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL_2' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF_3' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG_3' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL_3' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF_4' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG_4' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL_4' :(st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF_5' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG_5' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL_5' :(st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_DESCRIPTIF_6' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG_6' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_PRIX AU KG DU LOT VIRTUEL_6' :(st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SUPER_Page' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SUPER_Rang' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SUPER_Case' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'EXPRESS_Page' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'EXPRESS_Rang' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'EXPRESS_Case' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_Page' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_Rang' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_Case' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'REGIO_Page' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'REGIO_Rang' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'REGIO_Case' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'SUPER_WP' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'EXPRESS_WP' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        'MARKET_WP' : (st.column_config.Column(None, help="", width= None, required=True), True, True),
        }

    return column_config


def drop_columns_na(df):
    # Remplacer les chaînes vides par NaN pour faciliter la suppression
    df.replace('', pd.NA, inplace=True)
    # Supprimer les colonnes où toutes les valeurs sont NaN
    df = df.dropna(axis=1, how='all')
    return df

def clean(df, rename_dict,col2remove, col2add):
    df.columns = [re.sub(r'\n', '', col) for col in df.columns]   # nettoyage des colonnes
    df.columns = ['GENCOD' if col.startswith('gencod') else col for col in df.columns]
    df = df.rename(columns=rename_dict)
    df = df[df['GENCOD'].notna() & (df['GENCOD'] != '')] #clean les lignes sans GENCOD
    df.drop(columns=col2remove, inplace=True)
    for col, i in col2add.items():
        df.insert(i, col, np.nan),
    return df

def correct_descriptif(x):
    x = re.sub(r"(\d)cm",r"\1 cm", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)g",r"\1 g", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)mg",r"\1 mg", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)ml",r"\1 ml", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)cl",r"\1 cl", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)l",r"\1 l", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)(litres?)", r"\1 \2", x)
    x = re.sub(r"(\d)kg",r"\1 kg", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)Kg",r"\1 kg", x, flags=re.IGNORECASE)
    x = re.sub(r"(\d)x",r"\1 x", x)
    x = re.sub(r"x\s*(\d)", r"x \1", x)
    x = re.sub(r'^\n+', '', x)
    x = re.sub(r'^\s*$', '', x, flags=re.MULTILINE)
    x = re.sub(r"\b([Bb]oite)(s?)\b",lambda m: ("Boîte" if m.group(1)[0].isupper() else "boîte") + ("s" if m.group(2) else ""),x)
    x = re.sub(r"sur le produit fini",r"sur produit fini",x)
    x = re.sub(r'\s*%\s*', '% ', x)
    x = re.sub(r'\b([Ll]a poche)\b', 'Le doypack', x)
    x = re.sub(r'Kg', 'kg', x)
    x = re.sub(r'(\d+%)MG(?! sur produit fini)',  # Détecte XX%MG qui n'est pas suivi de "sur produit fini"
                r'\1 M.G. sur produit fini',x)       # Ajoute " M.G. sur produit fini"

      # Capitaliser la première lettre de chaque ligne
    x = "\n".join(line.capitalize() for line in x.splitlines())

    return x 

def clean_intitule(x):
    if isinstance(x,(float,int)):
        return ''
    if x.isupper():
        return x.lower().capitalize().strip()
    else:
        return x.strip()

def correct_categorie(x,cat_liste, match_dict, status_bar= None):

    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    intitule_specifique = ["brosse", "bougie"]

    for intitule in intitule_specifique:
        if re.findall(rf"\b{intitule}s?\*?\b", str(x.INTITULE) , re.IGNORECASE):
            return "Non alimentaire"
        
    if x.CATEGORIE in cat_liste:
        return x.CATEGORIE
    else:
        x.CATEGORIE = re.sub(r'\s+', ' ', str(x.CATEGORIE))
        x.CATEGORIE = re.sub(r'\s*([:/-])\s*', r' \1 ', x.CATEGORIE)
        x.CATEGORIE = re.sub(r"œ", r"oe", x.CATEGORIE)

        acronymes = ["BOF", "BSA", "Dph"]

        dict_mot_francais_ambigue = {'surgelé':'surgelés', 'tufs':'oeufs'}
        if x.CATEGORIE not in acronymes:
            x.CATEGORIE = nlpt.correct_orth(x.CATEGORIE.lower())

        for k, v in dict_mot_francais_ambigue.items():
            x.CATEGORIE = x.CATEGORIE.replace(k,v)

        x.CATEGORIE = match_dict.get(x.CATEGORIE, x.CATEGORIE).lower()

        return tool.texte_le_plus_similaire_tfidf_spacy(x.CATEGORIE, cat_liste)

def correct_mention(x, mentions, categories_dict, intitule_dict):
    # On accède aux colonnes de la ligne de DataFrame
    mention_specifique = x['MENTION SPECIFIQUE']
    categorie = x['CATEGORIE']
    intitule = x['INTITULE']
       
    # Vérifie si 'MENTION SPECIFIQUE' est dans mentions
    if mention_specifique in mentions:
        return mention_specifique

    # Vérifie si 'CATEGORIE' est dans categories_dict
    elif categorie in categories_dict:
        return categories_dict.get(categorie)

    # Vérifie si des mots comme 'bière' sont dans 'INTITULE' (insensible à la casse)
    elif isinstance(intitule, str) and 'sans alcool' in intitule.lower():
        return ''
    elif isinstance(intitule, str) and any(mot in intitule.lower() for mot in ['bière', 'bières']):
        return 'ALCOOL'
    else:
    
        if isinstance(intitule, str):
            for mot in intitule_dict.keys():
                if mot in intitule.lower():
                    return intitule_dict.get(mot)
            return ''
        else:
            return ''

def correct_pxkg_lotvirtuel(x, status_bar):

    #x = re.sub(r'\s+', ' ', str(x))
    x = nlpt.correct_orth(str(x))
    x = re.sub(r" - ", r"\n", x)
    x = x.replace("KILOS", "kilo")
    x = re.sub(r'\b[A-ZÀ-ÖØ-Ý]+\b', lambda x: x.group(0).lower(), x)
    x = x.replace("au lieu de", "Au lieu de")
    x = re.sub(r"(?<! )€", " €", x)
    x = re.sub(r"(?<=\d)\,(?=\d)", r".", x)
    x = re.sub(r"(\d+\.\d)(?!\d)", r"\g<1>0", x)
    x = re.sub(r'\s*:\s*', ' : ', x)

    status_bar.increment()
    status_bar.display()

    return x

def get_photo1_path(x,op, status_bar):
    PORT = os.getenv('PORT')  
    path2verify = f'static/PR{op[2:]}'

    if not os.path.exists(path2verify):
        raise FileNotFoundError(f"Le répertoire {path2verify} n'existe pas depuis {os.getcwd()} {os.listdir('./static')}")

    photopath =  [fichier for fichier in os.listdir(path2verify) if os.path.isfile(os.path.join(path2verify, fichier)) and fichier.startswith(str(x))]
        
    status_bar.increment()
    status_bar.display()                                                                
    if len(photopath)!=1:
        return None
    else:
        return f'http://localhost:{PORT}/app/static/PR{op[2:]}/{photopath[0]}'

def get_logo_path(x):
    PORT = os.getenv('PORT')

    # Utilisation de .loc pour accéder aux valeurs
    if 'SELECTION FRANCAP' in x and x['SELECTION FRANCAP']:
        return f'http://localhost:{PORT}/app/static/Francap.png'
    
    elif 'SELECTION CODIFRANCE' in x and x['SELECTION CODIFRANCE']:
        return f'http://localhost:{PORT}/app/static/codifrance.png'
    
    else:
        return f'http://localhost:{PORT}/app/static/segurel.png'


def set_picto(x, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    if pd.notna(x.get('PICTO')) and x['PICTO'] is not None and x['PICTO'] != '':
        return x['PICTO']
    elif any(word in x.INTITULE.lower() for word in ['chat', 'chien']):
        return 'ANIMAUX'
    elif x['CATEGORIE'] == 'Surgelés':
        return 'SURGELÉS'
    else:
        return ''

def correct_origine(x, status_bar= None):

    if status_bar is not None:
        status_bar.increment()
        status_bar.display()
    
    #if x.CATEGORIE in ['Ultra Frais', 'Charcuterie', 'Crèmerie - BOF', 'Patisserie Industrielle', 'Traiteur - Volaille Gibier Viande']:
    #    return 'XXX'
    if tool.isnull(x.ORIGINE) or isinstance(x.ORIGINE, int) or pd.isna(x.ORIGINE):
        return ''
    else:
        return x.ORIGINE
    
def correctpxkl(x):
    x = re.sub(r"(?<! )€", " €", str(x).strip())
    x = re.sub(" kg ", " kilo ", x)
    x = re.sub(" L ", " litre", x)
    return x

def dissociategroup(x, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    if not x.SR and x.CATALOG:
        #split descriptif
        descr = tool.split_descriptions(x.DESCRIPTIF)
        for i, des in enumerate(descr):
            if i == 0:
                x[f'DESCRIPTIF'] = des
            elif i == 5:
                x[f'DESCRIPTIF_6'] = ' ou '.join(descr[5:])
            else:
                x[f'DESCRIPTIF_{i+1}'] = des
        pxkl = tool.split_pxkl(x['PRIX AU KG'])    
        for i, px in enumerate(pxkl):
            if i == 0:
                x['PRIX AU KG'] = px
            else:
                x[f'PRIX AU KG_{i+1}'] = px


        pxkllv = tool.split_pxkllv(x['PRIX AU KG DU LOT VIRTUEL'])    
        for i, px in enumerate(pxkllv):
            if i == 0:
                x['PRIX AU KG DU LOT VIRTUEL'] = px
            else:
                x[f'PRIX AU KG DU LOT VIRTUEL_{i+1}'] = px
    return x


def dissociatephoto(x, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    photos, gencod = tool.split_photos(x)
    x['GENCOD'] = gencod.zfill(13)

    for i, photo in enumerate(photos[0:8]):
        x[f'PHOTO{i+1}'] = str(photo).split('.')[0].zfill(13)
        if tool.isnull(x[f'PHOTO{i+1}']):
            x[f'PHOTO{i+1}'] = ''
    
    return x

def adjust_rdm(x, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()
    if 'X' in x['RONDE DES MARQUES']:
        txt = nlpt.correct_orth(x['RONDE DES MARQUES'])
        mecapromo = re.sub(r"[X()]", "", txt)
        pourc = re.search(r"-?\d+(\.\d+)?%",txt)
        x['RONDE DES MARQUES']=True
        x['MECAPROMO']= mecapromo
        if mecapromo.lower().startswith('remise'):
            x['RI EN %'] = pourc
        elif mecapromo.lower().startswith('avantage'):
            x['BONUS'] = pourc
        elif any([mecapromo.startswith(dis) for dis in ['2ème', '3ème']]):
            x['LOT VIRTUEL'] = mecapromo
    else:
        x['RONDE DES MARQUES']=False
    return x




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
    

def capitalize_lines(text):
    """
    Met une majuscule à la première lettre de chaque ligne dans un texte donné.
    
    :param text: Le texte d'entrée (chaîne de caractères)
    :return: Le texte avec une majuscule au début de chaque ligne
    """
    # Séparer le texte en lignes, capitaliser la première lettre de chaque ligne, puis les réassembler
    lines = text.splitlines()
    capitalized_lines = [line.capitalize() for line in lines]
    return "\n".join(capitalized_lines)


def verifGencod(status, df, len_df):
    if status is not None:
        status_bar = tool.ProgressBar(status, len_df, '......vérification des GENCOD')
    df['GENCOD'] = df['GENCOD'].astype('str').apply(lambda x: x.split('.')[0]) #Stabiliser le type GENCODE en chaine de caractère d'un entier
    df['GENCOD'] = df['GENCOD'].apply(lambda x: x.zfill(13))  
    
    if status is not None:
        status_bar.display(float(1))
    return df