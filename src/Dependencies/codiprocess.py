
import pandas as pd
import re, os
import numpy as np
import tool
import nlptools as nlpt
import dataprocess as dp 

from dotenv import load_dotenv
from spellchecker import SpellChecker
pd.options.mode.copy_on_write = True

load_dotenv(dotenv_path='../.env')
CONFIG_PATH = os.getenv('CONFIG_PATH')
#CONFIG_FILE = 'ConfigFRA.xlsx'
DEPARTEMENTS = pd.read_csv(CONFIG_PATH + '/' + 'departements_francais.csv').nom.to_list()
PAYS = pd.read_csv(CONFIG_PATH + '/' + 'liste_pays_fr.csv').nom.to_list()

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
    df = df.copy()
    return df

def adjust_intitule(x, dict_etoile, dict_rdm, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    if tool.isnull(x['MECAPROMO']):
        meca = ''
    else:
        meca = x['MECAPROMO']

    intitule = x['INTITULE']
    if x['RONDE DES MARQUES']:
        if any([element in intitule for element in list(dict_rdm.keys())]):
            intitule =  dict_rdm.get(intitule)
        else:
            intitule = "sur les " + dp.mettre_au_pluriel_phrase(intitule).lower() + ' ' + x['MARQUE']
    
    if x['MENTION SPECIFIQUE'] in list(dict_etoile.keys()):
        intitule = intitule + dict_etoile.get(x['MENTION SPECIFIQUE'])
    if x['RONDE DES MARQUES']:
        intitule = meca +' '+ intitule
    x['INTITULE'] = intitule
    return x

def correct_pxkg_lotvirtuel(x, status_bar):

    if pd.isna(x['PRIX AU KG DU LOT VIRTUEL']):
        return ''
    else:
        x['PRIX AU KG DU LOT VIRTUEL'] = nlpt.correct_orth(str(x['PRIX AU KG DU LOT VIRTUEL']))
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r" - ", r"\n", x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = x['PRIX AU KG DU LOT VIRTUEL'].replace("KILOS", "kilo")
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r'\b[A-ZÀ-ÖØ-Ý]+\b', lambda match: match.group(0).lower(), x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = x['PRIX AU KG DU LOT VIRTUEL'].replace("au lieu de", "Au lieu de")
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r"(?<! )€", " €", x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r"(?<=\d)\,(?=\d)", r".", x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r"(\d+\.\d)(?!\d)", r"\g<1>0", x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = re.sub(r'\s*:\s*', ':', x['PRIX AU KG DU LOT VIRTUEL'])
        x['PRIX AU KG DU LOT VIRTUEL'] = x['PRIX AU KG DU LOT VIRTUEL'].replace("Au lieu de :", "Au lieu de")
        x['PRIX AU KG DU LOT VIRTUEL'] = x['PRIX AU KG DU LOT VIRTUEL'].replace('.',',') 
        existedanspxkllv = re.findall(r"^((?:Soit|soit)\b.*€)", x['PRIX AU KG DU LOT VIRTUEL'])       
        if not existedanspxkllv:
            existedanspxkl = re.findall(r"^((?:Soit|soit)\b.*€)", str(x['PRIX AU KG']))
            if existedanspxkl:
                lines = x['PRIX AU KG DU LOT VIRTUEL'].splitlines()
                if len(lines) >= 2:
                    lines.insert(2, existedanspxkl[0])  # Insère après la 2e (à l'index 2)
                    x['PRIX AU KG DU LOT VIRTUEL'] = '\n'.join(lines)

    status_bar.increment()
    status_bar.display()

    return x['PRIX AU KG DU LOT VIRTUEL']


def correct_origine(x, status_bar= None):

    if status_bar is not None:
        status_bar.increment()
        status_bar.display()
    
    if x.CATEGORIE in ['Ultra Frais', 'Charcuterie', 'Crèmerie - BOF', 'Patisserie Industrielle', 'Traiteur - Volaille Gibier Viande']:
        return 'XXX'
    else:
        x.ORIGINE = re.sub(r'\s+', ' ', str(x.ORIGINE).upper())
        x.ORIGINE = re.sub(r'FRANCE\s*\((\w+)\)', r'FRANCE \1', x.ORIGINE)
        x.ORIGINE = x.ORIGINE.replace('ORIGINE ','')
        x.ORIGINE = x.ORIGINE.replace('FABRIQUÉ EN ','')
        x.ORIGINE = x.ORIGINE.replace("FABRIQUÉ DANS L'",'').replace("FABRIQUÉ DANS LA",'').replace("FABRIQUÉ DANS LE",'').strip()
    
        if x.ORIGINE in [pays.upper () for pays in PAYS]:
            return x.ORIGINE.upper()
        if x.ORIGINE in [dep.upper () for dep in DEPARTEMENTS]:
            return 'FRANCE ' + x.ORIGINE.upper()

        try:
            x.ORIGINE = nlpt.correct_orth(x.ORIGINE)
        except:
            return ''
        return x.ORIGINE.upper()
    
def correctpxkl(x):
    x = re.sub(r"(?<! )€", " €", str(x).strip())
    x = re.sub(" kilo ", " kg ", x)
    x = re.sub(" L ", " litre", x)
    m = re.findall(r'\d+[.,]?\d*', x)
    if m:
        x = re.sub(m[0], rf'{float(m[0].replace(",", ".")):.2f}', x)
    return x.replace(".", ",")


def productnumbers(x):
    return len(tool.split_descriptions(x.DESCRIPTIF))




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
            x['BONUS EN %'] = pourc
            x['BONUS'] = pourc
        elif any([mecapromo.startswith(dis) for dis in ['2ème', '3ème']]):
            x['LOT VIRTUEL'] = mecapromo
    else:
        x['RONDE DES MARQUES']=False
    return x

def set_lot_virtuel(x):
    x = x.lower().strip()
    print(x)
    if x=='':
        return x
    elif '2 achetés' in x or '2+1' in x:
        return "2+1(5) OFFERT".upper()
    elif '1 acheté' in x:
        pourc = re.findall(r'(\d+)\s*(?=%)', x)[0]
        return f"-{pourc}%(4) SUR LE 2e".upper()
    else:
        return tool.add_minus_to_percentage(x).upper()


def set_selection(x, liste_nat):
    if x['GENCOD'].split('/')[0] in liste_nat:  ###mettre provenance du produit selon le parametre d'entrée
        x['SELECTION FRANCAP'], x['SELECTION CODIFRANCE'] = 'X', ''
    else:
        x['SELECTION FRANCAP'], x['SELECTION CODIFRANCE'] = '', 'X'
    return x


def apply_codi_process(self, df, isfrom = None , reset=False):

    load_dotenv()
    CONFIG_FILE = os.getenv('CONFIG_FILE')
    #CONFIG_FILE = 'ConfigFRA.xlsx'

    columns = df.columns
    len_df = len(df)
    output_col = dp.output_col('CODI')


    dict_label = {'NAT': 'Traitement de la liste Nationale...',
                  'CODI': 'Traitement de la liste Codifrance...',
                  None : 'Recalcul'}
    
    if not reset:
        df.drop(['RADIO', 'FACEBOOK', 'INSTAGRAM', 'SITE WEB COCCI', 'LINKEDIN', 'AUTRES SUPPORTS', 'ENCART FOURNISSEUR'], axis=1, inplace=True)
        rename_dict = {'STOP RAYON': 'SR', 'FORMAT SUPER':'FORMAT GV','FORMAT EXPRESS':'FORMAT MV','FORMAT COCCIMARKET':'FORMAT MVK','bonus':'BONUS',
                   'bonus %': 'BONUS EN %','BONUS €':'BONUS','BONUS %': 'BONUS EN %','FORMAT REGIONAL pv':'FORMAT PV','PRIX AU KG/L':'PRIX AU KG', 'PRIX AU KG OU L AVEC ET SANS RI':'PRIX AU KG'}
        df = df.rename(rename_dict, axis=1)
        columns = df.columns
        missing_cols = [col for col in output_col if col not in columns]
        missing_df = pd.DataFrame({col: None for col in missing_cols}, index=df.index) # Crée un DataFrame avec ces colonnes et None comme valeur
        df = pd.concat([df, missing_df], axis=1) # Combine proprement : on garde l'ordre de output_col
        df = df.reindex(columns=output_col)
        df = df.copy() # Défragmente
    columns = df.columns
    len_df = len(df)


    with self.st.status(dict_label.get(isfrom), expanded=True) as status:
        df['CODE OP'] = self.code_op
        df['DATE OP'] = tool.set_month_in_french(tool.get_d_label(tool.extract_dates(self.date_op)))
        df['CATALOG'] = 'X' # Mettre tout les produits en catalogue par default

        ####### transformer les colonnes booléènnes (celle qui utilise X pour Vrai)
        col_bool = dp.col_bool('CODI')
        col_bool.remove('RONDE DES MARQUES')
        col_bool.remove('CATALOG')
        for col in col_bool:
            df[col] = df[col].apply(lambda x : True if str(x).strip() in ['X', 'x'] else False)

        ####AFFICHE
        #df['AFFICHE'] = df['AFFICHE']
        df['PVC MAXI'] = df['PVC MAXI'].apply(lambda x: None if x is None or x in ['',' '] else float(x)) ### PVC MAXI
        df['PVC NET'] = df['PVC NET'].apply(lambda x: None if x is None or x in ['',' '] else float(x)) ### PVC MAXI

        df = dp.verifGencod(status, df, len_df) #Verification et formattage des GENCOD
  
        status_bar = tool.ProgressBar(status, len_df, '......répartitions des PHOTOS')
        df = df.apply(lambda x: dp.dissociatephoto(x,status_bar), axis=1)
        for i in range(8):
            df[f'PHOTO{i+1}'] = df[f'PHOTO{i+1}'].apply(lambda x: '' if tool.isnull(x) else str(x).split('.')[0]).fillna('').astype(str)

        df['ISFROM_LOGO'] = df.apply(lambda x :dp.get_logo_path(x),axis=1)
        status_bar.display(float(1))
        
        df.DESCRIPTIF = df.DESCRIPTIF.apply(lambda x: dp.correct_descriptif(str(x)))

        if not reset:
            #status_bar = tool.ProgressBar(status, len_df, '......fragmentation des groupement')
            df['SR'] = df.apply(lambda x : False if (re.search(r"[oO]u en|Existe aussi en|\b[Oo]u\b", str(x['DESCRIPTIF'])) or x['PVC MAXI'] is None) else True, axis = 1)
  
        status_bar = tool.ProgressBar(status, len_df, '......ajustement RDM')
        df['RONDE DES MARQUES'] = df['RONDE DES MARQUES'].fillna('')
        if not reset:
            df = df.apply(lambda x: adjust_rdm(x,status_bar), axis=1)
            df['BONUS EN %'] = df['BONUS EN %'].apply(lambda x: f"{int(round(x * 100))}%" if pd.notnull(x) and x != "" else "")
            df['BONUS'] = df['BONUS'].apply(lambda x: f"{round(x, 2):.2f}".replace('.', ',') if pd.notnull(x) and x != "" else "")
   
        status_bar.display(float(1))

        ####AFFICHE
        if not reset:
            df['PRODUIT DE UNE'] = df['PRODUIT DE UNE'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
            df['PRODUIT EN DER'] = df['PRODUIT EN DER'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
            df['MISE EN AVANT'] = df['MISE EN AVANT'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)



 

    #CATEGORIES ET MENTIONS SPECIFIQUES#################################################################################################
        status_bar = tool.ProgressBar(status, len_df, '......corrections des categories')
        categories = pd.read_excel(CONFIG_FILE, sheet_name="CATEGORIES", header=0)
        match_categories = pd.read_excel(CONFIG_FILE, sheet_name="MATCH_CATEGORIE", header=0)
        match_mentions = pd.read_excel(CONFIG_FILE, sheet_name="MATCH_MENTION", header=0)
        mentions = pd.read_excel(CONFIG_FILE, sheet_name="MENTIONS", header=0)
        #intitules_rdm = pd.read_excel(CONFIG_FILE, sheet_name="INTITULE RDM", header=0)
        #int_rdm = dict(zip(mentions.MENTION, mentions.NOTE ))
        match_cat = {lab.lower():cat for lab, cat in zip(match_categories.INTITULE, match_categories.CATEGORIE)}
        match_men = {lab.lower():men for lab, men in zip(match_mentions.INTITULE, match_mentions.MENTION)}
        categories_avec_mention = categories[pd.notna(categories.MENTION)]
        cat_men = dict(zip(categories_avec_mention.CATEGORIE, categories_avec_mention.MENTION ))
        men_etoile = dict(zip(mentions.MENTION, mentions.NOTE ))
     
        df['CATEGORIE'] = df.apply(lambda x : dp.correct_categorie(x,categories.CATEGORIE.to_list(), match_cat, status_bar), axis = 1)
        df['MENTION SPECIFIQUE'] = df.apply(lambda x: dp.correct_mention(x,mentions.MENTION.to_list(),cat_men, match_men), axis=1)
        
    #MARQUES#################################################################################################
        status_bar = tool.ProgressBar(status, len_df, '......corrections des marques')
        marques = pd.read_excel(CONFIG_FILE, sheet_name="MARQUES", header=0)
        for n_init, n_final in zip(marques.Nom, marques.Correction):
            df.MARQUE = df.MARQUE.fillna('').astype('str').apply(lambda x: re.sub(str(n_init), str(n_final), str(x)).upper())
            status_bar.increment()
            status_bar.display()


        df['INTITULE'] = df['INTITULE'].apply(lambda x: dp.clean_intitule(x)).fillna('').astype(str)
        df = df.apply(lambda x: adjust_intitule(x, men_etoile, {}, status_bar), axis=1)


    #PICTO#################################################################################################
        status_bar = tool.ProgressBar(status, len_df, '......corrections des pictos')
        df['PICTO'] = df.apply(lambda x: dp.set_picto(x, None), axis=1)
        df['PICTO'] = df['PICTO'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
        df['ORIGINE'] = df.apply(lambda x: '' if x['PICTO']=='SURGELÉS' else x['ORIGINE'], axis=1)
        df['ORIGINE'] = df['ORIGINE'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)

        status_bar.display(float(1))

    #LOT VIRTUEL################################################
        df['LOT VIRTUEL'] = df['LOT VIRTUEL'].apply(lambda x: '' if tool.isnull(x) else re.sub(r'\s+', ' ', re.sub(r'Lot virtuel : ', '', str(x).strip())))
        df['LOT VIRTUEL'] = df['LOT VIRTUEL'].apply(lambda x: set_lot_virtuel(x)) #.apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
        ####################### Nettoyage PRIX AU KG DU LOT VIRTUEL

        df['PRIX AU KG'] = df['PRIX AU KG'].fillna('').apply(lambda x: correctpxkl(x)).apply(lambda x: dp.capitalize_lines(x))
        df['PRIX AU KG'] = df.apply(lambda x:  x['PRIX AU KG'].splitlines()[0] if x['LOT VIRTUEL'] != "" else x['PRIX AU KG'], axis=1)

        status_bar = tool.ProgressBar(status, len_df, '......corrections PRIX AU KG DU LOT VIRTUEL')
        df['PRIX AU KG DU LOT VIRTUEL'] = df.apply(lambda x: correct_pxkg_lotvirtuel(x, status_bar), axis=1)
        status_bar.display(float(1))


    #pour codifrance verifier les prix au kl et le prix net

        ####### transformer les colonnes booléènnes (celle qui utilise X pour Vrai)

        df['ORIGINE'] = df.apply(lambda x : dp.correct_origine(x), axis=1)              


#################################A TRAITER LORS DU DCF
        df['MARKET_WP'] = None
        df['EXPRESS_WP'] = None    
        df['SUPER_WP'] = None
        df['SUPER_Page'] = None
        df['SUPER_Rang'] = None
        df['SUPER_Case'] = None
        df['EXPRESS_Page'] = None
        df['EXPRESS_Rang'] = None
        df['EXPRESS_Case'] = None
        df['MARKET_Page'] = None
        df['MARKET_Rang'] = None
        df['MARKET_Case'] = None
        df['REGIO_Page'] = None
        df['REGIO_Rang'] = None
        df['REGIO_Case'] = None

        status.update(expanded=False)

    return df[output_col]



def apply_sr_process(df):
    #selectionner les conditions de degroupage, SR, et Catalogue:
    isgroup = ~df['RONDE DES MARQUES'] & (df['PHOT02']!='')               
    return df[isgroup]


           ######DISSOCIATION
            #for row in df.iterrows():
            #    nb_prod = productnumbers(row)
            #    if isrow2dissociate(row):
            #        pass
            #    else:
            #        pass
            #    pass
            #df = df.apply(lambda x: dissociategroup(x,status_bar), axis=1)






# Découpe la chaîne en utilisant la regex regex_saveur et aussi les virgules
def split_by_saveur_and_comma(text):
    """
    Découpe une chaîne de saveurs/packagings selon les connecteurs ('ou', 'existe aussi en', etc.) et les virgules,
    puis nettoie chaque élément pour ne garder que les saveurs pertinentes.
    """
    # Découpe d'abord selon les connecteurs de saveurs
    parts = re.split(regex_saveur, text)
    result = []
    for part in parts:
        cleaned = re.sub(regex_saveur, '', part, flags=re.IGNORECASE).strip()
        if not cleaned:
            continue
        # Découpe par virgule, nettoie chaque sous-partie
        for p in cleaned.split(','):
            p_clean = p.strip()
            # Ignore les lignes commençant par Le/La/L' et contenant une taille/unité
            if re.match(regex_le_la, p_clean) and (re.search(regex_contenu, p_clean) or re.search(regex_unitaire, p_clean)):
                continue
            # Si ce n'est pas un packaging, retire la taille/unité éventuelle
            if not re.match(regex_le_la, p_clean):
                p_clean = re.sub(regex_contenu, '', p_clean).strip()
                # Coupe à la première occurrence d'un nombre unitaire
                p_clean = re.split(regex_unitaire, p_clean, maxsplit=1)[0].strip()
            if p_clean:
                result.append(p_clean)
    return result



def parse_descriptif_lines_into_dict(row):
    """
    Parse chaque ligne du champ 'DESCRIPTIF' pour extraire les saveurs, packaging, taille et unité.
    Retourne une liste de dictionnaires structurés.
    """

    results = []
    lines = str(row['DESCRIPTIF']).split('\n')

    for line in lines:
        # Recherche de la taille/unité via regex
        match_c = re.search(regex_contenu, line)
        match_u = re.search(regex_unitaire, line)
        saveurs = split_by_saveur_and_comma(line)

        if match_c or match_u:
            match = match_c if match_c else match_u
            packaging = line[:match.start()].strip()
            size = ''.join(filter(str.isdigit, match.group(0)))
            # Récupère l'unité (lettres) si regex_contenu, sinon tente après le match unitaire
            unit = (
                ''.join(filter(str.isalpha, match.group(0)))
                if match_c else
                (line[match_u.end():].strip().split()[0] if match_u and line[match_u.end():].strip() else None)
            )
            # Retirer packaging, size et unit de la ligne pour misc (version condensée)
            misc = line
            for val in (packaging, size, unit):
                if val:
                    misc = misc.replace(val, '', 1)
            misc = misc.strip()
            results.append({
                'saveurs': saveurs,
                'packaging': packaging if packaging else None,
                'size': size if size else None,
                'unit': unit if unit else None,
                'misc': misc if misc else None
            })
        else:
            if saveurs[0]== line.strip if line.strip() else None:
                # Cas où il n'y a que des saveurs sans taille/unité
                results.append({
                    'saveurs': None,
                    'packaging': None,
                    'size': None,
                    'unit': None,
                    'misc': line.strip() if line.strip() else None
                    })
            # Cas sans taille/unité détectée
            else:
                results.append({
                    'saveurs': saveurs,
                    'packaging': None,
                    'size': None,
                    'unit': None,
                    'misc': None
                })

    return results

def merge_descriptif_dict(d_dict):
    """
    Fusionne une liste de dictionnaires descriptifs en regroupant les saveurs par contenant (size).
    - d_dict: liste de dictionnaires avec les clés 'saveurs', 'packaging', 'size', 'unit'
    Retourne une liste de dictionnaires fusionnés.
    """
    assert d_dict, "DESCRIPTION should not be empty"

    # Vérifier que tous les dictionnaires ont les mêmes unités
    # Met à jour d_dict en place si des unités différentes sont trouvées
    units = [item['unit'] for item in d_dict if item['unit'] is not None]
    if units and any(u != units[-1] for u in units):
        last_unit = units[-1]
        for item in d_dict:
            if item['unit'] is not None and item['unit'] != last_unit:
                # Concaténer packaging, size et unit pour misc
                misc_parts = []
                if item.get('packaging'):
                    misc_parts.append(str(item['packaging']))
                if item.get('size'):
                    misc_parts.append(str(item['size']))
                if item.get('unit'):
                    misc_parts.append(str(item['unit']))
                item['misc'] = " ".join(misc_parts)
                item['packaging'] = None
                item['size'] = None
                item['unit'] = None

    # Définir 'packaging' comme la première valeur non nulle trouvée dans d_dict
    first_packaging = next((item['packaging'] for item in d_dict if item.get('packaging')), None)
    for item in d_dict:
        if not item.get('packaging') and first_packaging:
            item['packaging'] = first_packaging
    # Extraire tous les 'size' non None, en gardant l'ordre et l'unicité
    seen = set()
    contenants = [item['size'] for item in d_dict if item['size'] is not None and not (item['size'] in seen or seen.add(item['size']))]

    result = []
    idx = 0
    while idx < len(d_dict):
        # Pour chaque contenant, regrouper les éléments jusqu'au dernier de ce contenant
        for c in contenants:
            indices_c = [i for i in range(idx, len(d_dict)) if d_dict[i]['size'] == c]
            if not indices_c:
                continue
            last_idx = indices_c[-1]
            # Inclure aussi les éléments sans 'size' avant le dernier de ce contenant
            sub_d_dict = [d_dict[i] for i in range(idx, last_idx + 1) if d_dict[i]['size'] is None or d_dict[i]['size'] == c]
            # Fusionner les saveurs en gardant l'ordre et l'unicité
            saveurs = list(dict.fromkeys(s for item in sub_d_dict for s in item['saveurs']))
            packaging = next((d['packaging'] for d in sub_d_dict if d['packaging']), None)
            unit = next((d['unit'] for d in sub_d_dict if d['size'] == c and d['unit']), None)
            misc = next((d['misc'] for d in sub_d_dict if d['misc']), None)
            result.append({
                'saveurs': saveurs,
                'packaging': packaging,
                'size': c,
                'unit': unit,
                'misc': misc
            })
            idx = last_idx + 1
        break  # On sort après avoir traité tous les contenants

    return result

def apply_sr_process(df):
    df['desc_dict'] = df.apply(lambda row: merge_descriptif_dict(parse_descriptif_lines_into_dict(row)), axis=1)
    df['len'] = df['desc_dict'].apply(lambda desc: sum(len(d.get('saveurs', [])) for d in desc))
    df['CLE'] = df['CLE'].astype(int) * 100
    df['PRIX AU KG'] = df['PRIX AU KG'].astype('object')

    units_t = {'g': 1000, 'kg': 1, 'mg': 1_000_000, 'ml': 1000, 'cl': 100, 'l': 1, 'default': 1}

    isgroup = (~df['RONDE DES MARQUES']) & (
        (df['PHOTO2'] != '') | (df['DESCRIPTIF_2'] != '') | (df['len'] > 1)
    )

    new_rows = []
    regex_euro = r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?(?=\s?€)"
    
    for idx in df[isgroup].index:
        row = df.loc[idx]
        cle = row['CLE']
        desc_dict = row['desc_dict']
        px_net, px_max = row['PVC NET'], row['PVC MAXI']

        df.at[idx, 'SR'] = ''
        df.at[idx, 'CATALOG'] = 'X'

        for i, d in enumerate(desc_dict):
            colname = f"DESCRIPTIF{'' if i == 0 else f'_{i + 1}'}"
            colpkg = f"PRIX AU KG{'' if i == 0 else f'_{i + 1}'}"
            colpkglv = f"PRIX AU KG DU LOT VIRTUEL{'' if i == 0 else f'_{i + 1}'}"

            # Texte descriptif combiné
            value_desc = '\n'.join(filter(None, [
                d.get('misc', ''),
                ', '.join(d.get('saveurs', [])),
                ' '.join(filter(None, [d.get('packaging'), d.get('size'), d.get('unit')]))
            ]))
            df.at[idx, colname] = value_desc

            # Conditionnement
            match_cond = re.search(r"\b(\d+)\b", str(d.get('packaging', '')))
            conditionnement = int(match_cond.group(1)) if match_cond else 1
            size = float(d.get('size', '1').replace(',', '.'))
            unit_factor = units_t.get(d.get('unit'), 1)

            if i > 0:
                prix_kg_str = row['PRIX AU KG']
                matches = re.findall(regex_euro, prix_kg_str)
                p1 = px_net * unit_factor / (conditionnement * size)
                p2 = px_max * unit_factor / (conditionnement * size)

                if matches:
                    prix_kg_str = re.sub(matches[0], f"{p1:.2f}".replace(".", ","), prix_kg_str)
                if len(matches) > 1:
                    prix_kg_str = re.sub(matches[1], f"{p2:.2f}".replace(".", ","), prix_kg_str)
                df.at[idx, colpkg] = prix_kg_str
            else:
                df.at[idx, colpkg] = row['PRIX AU KG']

            prix_lv_str = row['PRIX AU KG DU LOT VIRTUEL']
            if i > 0:
                matches_lv = re.findall(regex_euro, prix_lv_str)
                if len(matches_lv) > 2:
                    prix_lv_str = re.sub(matches_lv[2], f"{p1:.2f}".replace(".", ","), prix_lv_str)
            df.at[idx, colpkglv] = prix_lv_str

            # Création des lignes SR
            for j, sav in enumerate(d.get('saveurs', []), start=1):
                new_row = row.copy()
                new_row['CLE'] = cle + j
                new_row['DESCRIPTIF'] = '\n'.join(filter(None, [
                    d.get('misc', ''), sav,
                    ' '.join(filter(None, [d.get('packaging'), d.get('size'), d.get('unit')]))
                ]))
                new_row['SR'] = 'X'
                new_row['CATALOG'] = ''
                new_row['PRIX AU KG'] = df.at[idx, colpkg]
                new_rows.append(new_row)

    # Ajouter toutes les lignes SR en une fois
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    return df.sort_values("CLE", ascending=True).reset_index(drop=True)
