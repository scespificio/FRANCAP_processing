
import pandas as pd
import re, os
import numpy as np
import tool
import nlptools as nlpt
import dataprocess as dp 

from dotenv import load_dotenv
from spellchecker import SpellChecker
pd.options.mode.copy_on_write = True

load_dotenv()
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
        #self.df_nat = dp.verifGencod(status, self.df_nat, len(self.df_nat))
        #liste_nat = self.df_nat.GENCOD.tolist()
        #df = df.apply(lambda x: set_selection(x,liste_nat), axis=1)


        status_bar = tool.ProgressBar(status, len_df, '......répartitions des PHOTOS')
        df = df.apply(lambda x: dp.dissociatephoto(x,status_bar), axis=1)
        for i in range(8):
            df[f'PHOTO{i+1}'] = df[f'PHOTO{i+1}'].apply(lambda x: '' if tool.isnull(x) else str(x).split('.')[0]).fillna('').astype(str)

        df['ISFROM_LOGO'] = df.apply(lambda x :dp.get_logo_path(x),axis=1)
        status_bar.display(float(1))
        
        df.DESCRIPTIF = df.DESCRIPTIF.apply(lambda x: dp.correct_descriptif(str(x)))
  
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

        if not reset:
            #status_bar = tool.ProgressBar(status, len_df, '......fragmentation des groupement')
            df['SR'] = df.apply(lambda x : False if (re.search(r"[oO]u en|Existe aussi en|\b[Oo]u\b", str(x['DESCRIPTIF'])) or x['PVC MAXI'] is None) else True, axis = 1)

            ######DISSOCIATION
            #for row in df.iterrows():
            #    nb_prod = productnumbers(row)
            #    if isrow2dissociate(row):
            #        pass
            #    else:
            #        pass
            #    pass
            #df = df.apply(lambda x: dissociategroup(x,status_bar), axis=1)

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
