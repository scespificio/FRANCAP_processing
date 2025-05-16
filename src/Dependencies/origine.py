import os

import numpy as np
from dotenv import load_dotenv
import pandas as pd
from unidecode import unidecode

import re

load_dotenv()

CONFIG_FILE = os.getenv('CONFIG_FILE')
CONFIG_PATH = os.getenv('CONFIG_PATH')
TERROIR = pd.read_excel(CONFIG_FILE, sheet_name="TERROIR", header=0).TERROIR.to_list() \
    + pd.read_csv(CONFIG_PATH + '/' + 'departements_francais.csv').nom.to_list()
    
PAYS = pd.read_csv(CONFIG_PATH + '/' + 'liste_pays_fr.csv').nom.to_list()
PAYS = ['France', 'UE', 'Écosse'] + [p for p in PAYS if p != 'France']

#REMOVE_FROM_ORIGINE
PREFIX = [r'(FABRIQUÉ|TRANSFORMÉ|TRANSFORME) (EN|AUX)']
REMOVE =[r'PRÉPARÉ[S]? (EN|AUX)', r'^ORIGINE']
RENAME_DICT = {'Pays - Bas': 'Pays-Bas',
               'union européenne' : 'UE',
               'union-europeenne' : 'UE',
               'UNION EUROPEENNE' : 'UE',
               'Europe' : 'UE',
               "l'UE)" : 'UE',


               'USA': 'États-Unis',
               'Poland':'Pologne',
               'Italy':'Italie',
               'Pays Bas':'Pays-Bas',
               'GB':'Royaume-Uni',
               'Royaume Uni' :'Royaume-Uni',
               'Greece': 'Grèce',
               'Ireland' : 'Irlande',	
               'Haut de France':'HAUTS-DE-FRANCE',
               'Hauts de France':'HAUTS-DE-FRANCE',
               'Elaboré' : 'Fabriqué'
               }
VIANDE_DICT = {
    'VBF' : 'VIANDE BOVINE',
    '-VBF' : 'VIANDE BOVINE',
    'BOVINE' : 'VIANDE BOVINE',
    'BOEUF' : 'VIANDE BOVINE',
    'BŒUF' : 'VIANDE BOVINE',
    'PORC' : 'VIANDE DE PORC',
    'VPF' : 'VIANDE DE PORC',
    '-VPF': 'VIANDE DE PORC',
    'VOLAILLE' : 'VIANDE DE VOLAILLE',
}

def rename(chaine, rename_d):
    for k,v in rename_d.items():
        chaine = chaine.replace(k.upper(),v.upper())
    return chaine

def clean(chaine, clean_l):
    for pattern in clean_l:
        text = re.sub(pattern, '', chaine)
    return text

def get_prefix(chaine, prefix_l):
    for pattern in prefix_l:
        if re.search(pattern, chaine) is not None:
            return re.search(pattern, chaine).group()
    return ''

def get_pays(chaine, pays_l):
    pays = []
    for p in pays_l:
        match = re.search(rf"\b({p.upper()}|{unidecode(p.upper())})\b", chaine)
        if match:
            pays.append(unidecode(match.group()))
    if len(pays)==0:
        return ''
    elif len(pays) ==1:
        return pays[0]
    elif len(pays) ==2:
        if pays[0]=='FRANCE' and pays[1]=='UE':
            return 'FRANCE'
        else:
            return f"{pays[0]} OU {pays[1]}"
    else:
        label = ''
        for p in pays[:-1]:
            label= f'{p}, ' + label
        return label + f' OU {pays[-1]}'

def get_dep(chaine, dep_l):
    for d in sorted(dep_l, key=len, reverse=True): # Trier les départements par longueur décroissante pour privilégier les plus longs
        match = re.search(rf"\b({re.escape(d.upper())}|{re.escape(unidecode(d.upper()))})\b", chaine)
        if match:
            return unidecode(match.group())
    return None

def get_viande(chaine, viande_d, pays, origin):
    mots = chaine.split()
    viande= ''

    for m in ['FRANCAIS', 'FRANCAISE','-VPF','VPF','VBF','-VBF']:
        if m in mots:
            if pays == 'FRANCE':
                origin = ''
            elif pays == '':
                pays = 'FRANCE'
            else:
                origin = 'ORIGINE FRANCE'

    for mot in mots:
        if mot in viande_d.keys():
            viande = viande_d.get(mot.upper())
            break

    if viande == '' and 'VIANDE' in mots:
        viande = 'VIANDES'
    
    if viande == '':
        return '', pays
    else:
        return viande + origin, pays
   

def get_origine(chaine):
    resultat = re.search(r'ORIGINE[^\w]*\s*(\w+)', chaine)
    if resultat is not None:
        return ' ORIGINE ' + get_pays(resultat.group(1), PAYS)
    else:
        return ''
    

def decode_origine(x, status_bar= None):  
 
    chaine = x.upper()
    chaine = re.sub(r'[^\w\s\-_\'"]', '', chaine) # Regex pour supprimer toutes les ponctuations sauf '  - et _

    chaine = rename(chaine, RENAME_DICT)

    origin= unidecode(get_origine(chaine))
    chaine =clean(chaine, REMOVE)
    
    prefix = unidecode(get_prefix(chaine, PREFIX))
    pays = get_pays(chaine,PAYS)
    dep = get_dep(chaine, TERROIR)
    viande, pays= get_viande(unidecode(chaine),VIANDE_DICT, pays, origin)
    #print(pays)
    if (pays =='' or pays=='FRANCE') and dep is not None:
        return f"{prefix} FRANCE {dep}".strip()
    elif dep is None and pays == 'FRANCE':
        print(1)
        return f"{prefix} FRANCE {viande}".strip()
    elif pays != '':
        return f"{prefix} {pays} {viande}".strip()
    else:
        return unidecode(chaine).strip()
    