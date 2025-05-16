import pandas as pd
import re, os
import numpy as np
import tool
import nlptools as nlpt
import dataprocess as dp
import codiprocess as cp
from unidecode import unidecode

from dotenv import load_dotenv

load_dotenv()
CONFIG_PATH = os.getenv('CONFIG_PATH')

def adjust_intitule(x, dict_etoile, dict_rdm, status_bar= None):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    intitule = x['INTITULE']
  
    if x['MENTION SPECIFIQUE'] in list(dict_etoile.keys()):
        intitule = intitule + dict_etoile.get(x['MENTION SPECIFIQUE'])

    x['INTITULE'] = intitule
    return x

def get_nat_index(gencod, df):
    # S'assurer que gencod est une chaîne de caractères avant d'utiliser startswith
    indexes = df[df['GENCOD'].apply(lambda x: gencod in str(x))].index
    return indexes

def set_nat(df_nat, col, x, status_bar):
    if status_bar is not None:
        status_bar.increment()
        status_bar.display()

    # Utiliser .loc avec des crochets [] au lieu de parenthèses
    indexes = get_nat_index(x['GENCOD'], df_nat)
    if not indexes.empty:
        return df_nat[col].loc[indexes].iloc[0]
    else:
        return x[col]  
    
def set_lot_virtuel(x, market):
    if x['NB UC DS LOT VIRTUEL'] == 3:
        return " 2+1(3) OFFERT"
    elif x['NB UC DS LOT VIRTUEL'] == 2:
        if market:
            reste = int(x['LOT VIRTUEL VALEUR']*100)%100
            return f"-{int(x['LOT VIRTUEL VALEUR'])}€.{'0'+str(reste) if reste <10 else reste}(4) SUR LE 2e".upper() #.replace('.',',')
        else:
            pourc = int(100*x['LOT VIRTUEL VALEUR']/x['PVC MAXI'])
            pourc = min([20, 25, 34, 50, 60, 68, 75, 80], key=lambda x: abs(x - pourc))
            return f"-{pourc}%(4) SUR LE 2e".upper()
    else:
        return ''
    
def set_pvcnet_lot_virtuel(x):
    if not tool.isnull(x['NB UC DS LOT VIRTUEL']) and int(x['NB UC DS LOT VIRTUEL']) in[2,3]:
        return float(f"{(x['PRIX LOT AVEC REMISE']/x['NB UC DS LOT VIRTUEL']):.2f}")
    else:
        return x['PVC NET']
    
    
def set_pxkg_lotvirtuel(x, status_bar):
    status_bar.increment()
    status_bar.display()
    if x['LOT VIRTUEL'] == '':
        return ''
    else:
        label = f"Les {int(x['NB UC DS LOT VIRTUEL'])} : {np.round(x['PRIX LOT AVEC REMISE'],2):.2f} €  \nAu lieu de {np.round(x['PRIX LOT INIT'],2):.2f} €  \nSoit le {'kg' if x['K/L']=='K' else 'litre' } : {np.round(x['PRIX AU KG OU L DU LOT VIRTUEL'],2):.2f} €  \nÉconomies : {np.round(x['LOT VIRTUEL VALEUR'],2):.2f} €"
        label = label.replace('.',',')
        return label

def get_market_tag(df, df_m, tag_l):
    # Boucle sur chaque tag
    for tag in tag_l:
        # Création de la colonne 'MARKET_<tag>' si elle n'existe pas
        market_col = f'MARKET_{tag}'
        if tag == 'PVC MAXI':
            market_col = 'MARKET_PVC_MAXI'
        if market_col not in df.columns:
            df[market_col] = None       
        # Mapper les valeurs de df_m[tag] basées sur la clé 'gencod'
        mapping = df_m.set_index('GENCOD')[tag]
        # Appliquer le mapping et remplir les valeurs manquantes avec None
        df[market_col] = df['GENCOD'].map(mapping).where(df['GENCOD'].notna(), '')
        df[market_col] = df[market_col].fillna('')
    
    return df

def set_px_kg(x): 
    if x['K/L'] in ['K','L']:
        unit = 'kg' if x['K/L']=='K' else 'litre'
        if x['K/L']=='L' and int(x['POIDS/VOLUME'])==1:
            return ''
        if tool.isnull(x['RI EN %']) and tool.isnull(x['RI EN €']):
            return f"Soit le {unit} : {x['PRIX AU KG OU L']:.2f} €".replace('.', ',')
        else:
            return f"Soit le {unit} : {x['PRIX NET AU KG OU L']:.2f} € \nAu lieu de {x['PRIX AU KG OU L']:.2f} €".replace('.', ',')
    else:
        return ''

def apply_segu_process(self, df, reset=False, market = False):
  
    load_dotenv()
    CONFIG_FILE = os.getenv('CONFIG_FILE')

    columns = df.columns
    len_df = len(df)
    output_col = dp.output_col('SEGU_M' if market else 'SEGU')

    if not reset:
        df.drop(['theme', 'radio', 'réseaux sociaux/digital'], axis=1, inplace=True)
        rename_dict = {'PVC COCCINELLE': 'PVC MAXI','PVC COCCIMARKET': 'PVC MAXI', 'prix net':'PVC NET','affiche':'AFFICHE','une':'PRODUIT DE UNE',               ###### dans liste client
                        'der': 'PRODUIT EN DER', 'mise en avant':'MISE EN AVANT', 'Picto': 'PICTO', 'Catégorie': 'CATEGORIE',
                        'SUPER':'FORMAT GV', 'EXPRESS':'FORMAT MV', 'CMK': 'FORMAT MVK', 'origine' : 'ORIGINE',
                        'bonus':'BONUS', 'RI valeur':'RI EN €', 'RI %':'RI EN %', 'bonus %': 'BONUS EN %',
                        'libellé remise': 'LOT VIRTUEL'}
        df = df.rename(rename_dict, axis=1)
        rename_dict = {col : unidecode(col.upper()) for col in df.columns}
        rename_dict['pageligne']='pageligne'
        rename_dict['RI EN €']='RI EN €'
        df = df.rename(rename_dict, axis=1)
        df = df.copy()
        columns = df.columns

        df[[col for col in output_col if col not in columns]] = None # ajouter les colonnes manquantes
       
    with self.st.status('Traitement de la liste COCCIMARKET' if market else 'Traitement de la liste COCCINELLE', expanded=True) as status:
        
        df['CODE OP'] = self.code_op
        df['DATE OP'] = tool.set_month_in_french(tool.get_d_label(tool.extract_dates(self.date_op)))
        if not reset: 
            df['SELECTION SEGUREL'] = df['pageligne'].apply(lambda x: 'X' if x in self.df_prod_seg['pageligne'].to_list() else '')
            df['SELECTION FRANCAP'] = df['pageligne'].apply(lambda x: 'X' if x not in self.df_prod_seg['pageligne'].to_list() else '')       
            df['SR'] = 'X'    # Mettre tout les produits en stop rayon par default
            df['CATALOG'] = 'X'

        ####### transformer les colonnes booléènnes (celle qui utilise X pour Vrai)
        col_bool = dp.col_bool('SEGU_M' if market else 'SEGU')
        for col in col_bool:
            df[col] = df[col].apply(lambda x : True if str(x).strip() in ['X', 'x'] else False)    

        df = dp.verifGencod(status, df, len_df) #Verification et formattage des GENCOD

        if not market:
            status_bar = tool.ProgressBar(status, len_df, '......répartitions des PHOTOS')
            df = df.apply(lambda x: dp.dissociatephoto(x,status_bar), axis=1)
            for i in range(8):
                df[f'PHOTO{i+1}'] = df[f'PHOTO{i+1}'].apply(lambda x: '' if tool.isnull(x) else str(x).split('.')[0]).fillna('').astype(str)

            df['ISFROM_LOGO'] = df.apply(lambda x :dp.get_logo_path(x),axis=1)
            #df = df.copy()
            status_bar.display(float(1))

        categories = pd.read_excel(CONFIG_FILE, sheet_name="CATEGORIES", header=0)
        match_categories = pd.read_excel(CONFIG_FILE, sheet_name="MATCH_CATEGORIE", header=0)
        match_mentions = pd.read_excel(CONFIG_FILE, sheet_name="MATCH_MENTION", header=0)
        mentions = pd.read_excel(CONFIG_FILE, sheet_name="MENTIONS", header=0)
        match_cat = {lab.lower():cat for lab, cat in zip(match_categories.INTITULE, match_categories.CATEGORIE)}
        match_men = {lab.lower():men for lab, men in zip(match_mentions.INTITULE, match_mentions.MENTION)}
        categories_avec_mention = categories[pd.notna(categories.MENTION)]
        cat_men = dict(zip(categories_avec_mention.CATEGORIE, categories_avec_mention.MENTION ))
        men_etoile = dict(zip(mentions.MENTION, mentions.NOTE ))

        status_bar = tool.ProgressBar(status, len_df, '......ajustement des decriptifs des produits francap')
        df['DESCRIPTIF'] = df.apply(lambda x: dp.correct_descriptif(str(x['DESCRIPTIF'])), axis =1)
        status_bar.display(float(1))        
        
        status_bar = tool.ProgressBar(status, len_df, '......assignation des categories des produits francap')
        df['CATEGORIE'] = df.apply(lambda x: dp.correct_categorie(x,categories.CATEGORIE.to_list(), match_cat, status_bar), axis =1)
        status_bar.display(float(1))
        status_bar = tool.ProgressBar(status, len_df, '......assignation des mention spécifiques des produits francap')
        df['MENTION SPECIFIQUE'] = df.apply(lambda x: dp.correct_mention(x,mentions.MENTION.to_list(),cat_men, match_men), axis=1)
        status_bar.display(float(1))
        
        status_bar = tool.ProgressBar(status, len_df, '......assignation des intitulés des produits francap')
        df['INTITULE'] = df.apply(lambda x: dp.clean_intitule(x['INTITULE']), axis =1)
        df = df.apply(lambda x: x if x['SELECTION FRANCAP'] else adjust_intitule(x, men_etoile, {}, status_bar), axis=1)
        status_bar.display(float(1))
        status_bar = tool.ProgressBar(status, len_df, '......assignation des pictos des produits francap')
        df['PICTO'] = df['PICTO'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
        df['ORIGINE'] = df.apply(lambda x: '' if x['PICTO']=='SURGELÉS' else x['ORIGINE'], axis=1)
        df['ORIGINE'] = df['ORIGINE'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
        status_bar.display(float(1))
        df['ORIGINE'] = df.apply(lambda x: dp.correct_origine(x), axis =1)
        status_bar.display(float(1))
        
        status_bar = tool.ProgressBar(status, len_df, '......corrections des marques')
        marques = pd.read_excel(CONFIG_FILE, sheet_name="MARQUES", header=0)
        for n_init, n_final in zip(marques.Nom, marques.Correction):
            df.MARQUE = df.MARQUE.fillna('').astype('str').apply(lambda x: re.sub(str(n_init), str(n_final), str(x)).upper())
            status_bar.increment()
            status_bar.display()

    #LOT VIRTUEL################################################
        df['LOT VIRTUEL'] = df.apply(lambda x: set_lot_virtuel(x, market), axis=1)

        ####################### Nettoyage PRIX AU KG DU LOT VIRTUEL
        status_bar = tool.ProgressBar(status, len_df, '......réglages des PRIX AU KG DU LOT VIRTUEL')
        df['PRIX AU KG DU LOT VIRTUEL'] = df.apply(lambda x: set_pxkg_lotvirtuel(x, status_bar), axis=1)
        status_bar.display(float(1))

        df['PRIX AU KG'] = df.apply(lambda x: set_px_kg(x),axis=1)
    ####AFFICHE
        if not reset:
            df['PVC MAXI'] = df['PVC MAXI'].apply(lambda x: None if x is None or x in ['',' '] else float(x)) ### PVC MAXI
            df['PVC NET'] = df['PVC NET'].apply(lambda x: None if x is None or x in ['',' '] else float(x)) ### PVC MAXI
            df['PVC NET'] = df.apply(lambda x: set_pvcnet_lot_virtuel(x), axis=1)
            #df['BONUS'] = df.apply(lambda x: x.BONUS if pd.isna(x['BONUS EN %']) or x['BONUS E%'] == '' or x['BONUS %'] is None else x['BONUS %'], axis=1)

            df['PRODUIT DE UNE'] = df['PRODUIT DE UNE'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
            df['PRODUIT EN DER'] = df['PRODUIT EN DER'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)
            df['MISE EN AVANT'] = df['MISE EN AVANT'].apply(lambda x: '' if tool.isnull(x) else x).fillna('').astype(str)


        #df_g = df.groupby(['CATEGORIE', 'MARQUE', 'PVC MAXI']) \
        # .apply(lambda x: list(x.index)) \
        # .reset_index(name='LISTE_INDEX')
        #df_g = df_g[df_g['LISTE_INDEX'].apply(len)>1]
        #df_g['maxindex']=df_g['LISTE_INDEX'].apply(max)
        #df_g = df_g.sort_values(by='maxindex', ascending=False)

        if not market:
            tag = ['DESCRIPTIF', 'PRIX AU KG', 'PVC MAXI', 'BONUS','BONUS EN %', 
                   'RI EN €', 'RI EN %', 'PVC NET', 'LOT VIRTUEL', 'PRIX AU KG DU LOT VIRTUEL','SR',
                   'DESCRIPTIF_2','PRIX AU KG_2', 'PRIX AU KG DU LOT VIRTUEL_2',
                   'DESCRIPTIF_3','PRIX AU KG_3', 'PRIX AU KG DU LOT VIRTUEL_3',
                   'DESCRIPTIF_4','PRIX AU KG_4', 'PRIX AU KG DU LOT VIRTUEL_4']
            df = get_market_tag(df, self.main_df_m, tag)
            df = df.rename({'MARKET_SR': 'SR_SEGU_MARKET'})
            df['FORMAT MVK'] = df['GENCOD'].apply(lambda x: x in self.main_df_m['GENCOD'].values)

        #    j=0
        #    for _, row in df_g.iterrows():
        #        print(row)
        #        row_to_duplicate = df.iloc[row.LISTE_INDEX[0]+j]
        #        row_to_duplicate.SR = False
        #        for i, index in enumerate(row.LISTE_INDEX):
        #            df.loc[index,'CATALOG'] = False
        #            #row_to_duplicate[f"PHOTO{i+1}"]=df.loc[index,'PHOTO1']
        #            row_to_duplicate[f"DESCRIPTIF_{i+1}"]=df.loc[index]['DESCRIPTIF']
        #            row_to_duplicate[f"PRIX AU KG_{i+1}"]=df.loc[index]['PRIX AU KG']
        #            row_to_duplicate[f"PRIX AU KG DU LOT VIRTUEL_{i+1}"]=df.loc[index]['PRIX AU KG DU LOT VIRTUEL']

        #        row_df = pd.DataFrame([row_to_duplicate])    
        #        df_upper = df.iloc[:row.maxindex+1+j]
        #        df_lower = df.iloc[row.maxindex+1+j:]
        #        df = pd.concat([df_upper, row_df, df_lower]).reset_index(drop=True)
        #        j +=1

        status.update(expanded=False)

    return df[output_col]



