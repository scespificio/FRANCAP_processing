import pandas as pd
import io, os
import pickle
import dataprocess as dp 
import codiprocess as cp 
import seguprocess as sp 


class Operation:
   
    def __init__(self):
        self.main_df = None
        self.code_op, self.date_op = None, None
        self.st = None
      
    def detach_session(self):
        self.st = None

    #def get_new_list_from_customer(self, liste_nat, liste_codi, liste_segu):
#
    #    self.df_nat = pd.read_excel(liste_nat, sheet_name=0, header=0)
    #    natsheets = pd.ExcelFile(liste_nat).sheet_names
    #
#
    #    if   'A' in natsheets:
    #        self.df_nat = pd.read_excel(liste_nat, sheet_name='A', header=0)
    #    elif 'FINALE'in natsheets:
    #        self.df_nat = pd.read_excel(liste_nat, sheet_name='FINALE', header=0)
#
    #            # Garder uniquement les lignes où 'colonne_a_filtrer' n'est ni NaN ni une chaîne vide
    #    self.df_nat = self.df_nat[self.df_nat['GENCOD'].notna() & (self.df_nat['GENCOD'] != '')]
#
    #    #self.df_segu = self.df_segu[self.df_segu['GENCOD'].notna() & (self.df_segu['GENCOD'] != '')]
    #    #self.main_df = dp.apply_base_process(self.st, self.df_nat, 'NAT')
    #    self.code_op, self.date_op = self.df_nat['CODE OP'][0], self.df_nat['DATE OP'][0]


class Segurel(Operation):
    def __init__(self):
        # Appelle le constructeur de la classe parent
        super().__init__()
        self.main_df_m = None
        self.df_segu, self.df_segu_m = None, None
        self.df_non, self.df_prod_seg = None, None

    def get_new_list_from_customer(self, liste_segu):
        segusheets = pd.ExcelFile(liste_segu).sheet_names

        assert(all(sheet in [s.strip() for s in segusheets] for sheet in ['EP','COCCINELLE agence','CMK agence'])),\
              f" La feuilles 'EP','COCCINELLE agence' ou 'CMK agence' est manquante dans le fichier SEGUREL: {segusheets}"
 
        for sheet in segusheets:
            if sheet.strip() == 'COCCINELLE agence':
                cocci = sheet
            elif sheet.strip() == 'CMK agence':
                cmk = sheet
            elif sheet.strip() == 'EP':
                ep = sheet

        
    ##########################COCCINELLE
        i=0
        header_cond = True
        while (header_cond):
            self.df_segu = pd.read_excel(liste_segu, sheet_name=cocci, header=i)
            header_cond = 'pageligne' not in [str(col).strip() for col in list(self.df_segu.columns)]
            i +=1
        
        self.df_segu = self.df_segu.dropna(subset=['pageligne'])
        #self.df_segu = self.df_segu.rename(columns = { col : col.strip() for col in list(self.df_segu.columns)})
        rename_dict = {}
        col2remove = {}
        col2add = {}
        self.df_segu = dp.clean(self.df_segu, rename_dict, col2remove, col2add)

    ##########################MARKET
        i=0
        header_cond = True
        while (header_cond):
            self.df_segu_m = pd.read_excel(liste_segu, sheet_name=cmk, header=i)
            header_cond = 'pageligne' not in [str(col).strip() for col in list(self.df_segu_m.columns)]
            i +=1
        #
        self.df_segu_m = self.df_segu_m.dropna(subset=['pageligne'])
        #self.df_segu_m = self.df_segu_m.rename(columns = { col : col.strip() for col in list(self.df_segu_m.columns)})
        self.df_segu_m = dp.clean(self.df_segu_m, rename_dict, col2remove, col2add)
           

#    ##########################PROD SEGUREL
        i=0
        not_header_cond = True
        while (not_header_cond):
            df = pd.read_excel(liste_segu, sheet_name=ep, header=i).dropna(axis=1, how='all')
            not_header_cond = 'pageligne' not in [str(col).strip() for col in list(df.columns)]
            i +=1
        self.df_prod_seg = df.dropna(subset=['pageligne']).reset_index(drop=True)
        #self.df_prod_seg = pd.concat([df[df.columns[:3]], df[df.columns[3:]].\
        #                            rename(columns={ df.columns[i+3] : df.columns[i] for i in range(3)}).\
        #                            dropna(axis=0, how='all')], axis=0).reset_index(drop=True)


    def init_main(self, st=None, reference = None):
        self.st = st
        if reference is None:
            self.main_df = self.df_segu
            self.main_df_m = self.df_segu_m
        else:
            self.main_df = reference.main_df
            self.main_df_m = reference.main_df_m

    def set_main(self, st=None):
        if st is not None:
            self.st = st
        
        self.main_df_m = sp.apply_segu_process(self, self.df_segu_m, market=True).reset_index(drop=True)
        self.main_df = sp.apply_segu_process(self, self.df_segu, market =False).reset_index(drop=True)

        self.main_df.CLE = self.main_df.index + 1

    def reset_main(self, st=None):
        if st is not None:
            self.st = st
        
        self.main_df = self.main_df[self.main_df['GENCOD'].notna() & (self.main_df['GENCOD'] != '')]



    def save(self, filepath):
        try:
            self.detach_session()
            with open(filepath, 'wb') as file:
                pickle.dump(self, file)
                return 'ok'
        except Exception as e:
                return e
        
    def prepare_to_excel(self):
        print(self.main_df.columns)
        df = self.main_df[dp.output_col('SEGU')]
        #df_m = self.main_df_m[dp.output_col('SEGU')]  
        col_bool = dp.col_bool('SEGU')
        for col in col_bool:
            df[col] = self.main_df[col].apply(lambda x : 'X' if x else '')
            #df_m[col] = self.main_df_m[col].apply(lambda x : 'X' if x else '')

        return df

    def set_worksheet(self, worksheet, workbook, df):
        # Définir le format pour l'en-tête (gras + background bleu ciel)
        internal_f = workbook.add_format({ 'bg_color': '#E9DACE', 'font_color': '#E9DACE',  'text_wrap': True, 'valign': 'top'})  ##### Variable interne  couleur specifique à Codi
        format1 = workbook.add_format({'text_wrap': True, 'valign': 'top'}) #colonne neutre sans transfo
        useless_f = workbook.add_format({'font_color':'#000000' , 'bg_color': '#000000'}) # colonne inutile à supprimer
        bool_f = workbook.add_format({'align': 'center', 'valign': 'top'}) #gris
        final_bool_f = workbook.add_format({'align': 'center', 'font_color': '#3470C9', 'bold': True, 'valign': 'top'})
        toverify_bool_f = workbook.add_format({'align': 'center', 'font_color': '#3470C9', 'bold': False, 'valign': 'top'})
        toverify_f = workbook.add_format({'font_color': '#3470C9', 'bold': False, 'valign': 'top'})  #bleu
        toverify_wf = workbook.add_format({'font_color': '#3470C9', 'bold': False, 'text_wrap': True, 'valign': 'top'})  #bleu
        final_f = workbook.add_format({'font_color': '#3470C9', 'bold': True, 'valign': 'top'})  #bleu
        final_wf = workbook.add_format({'font_color': '#3470C9', 'bold': True, 'text_wrap': True, 'valign': 'top'})  #bleu
        format_w = workbook.add_format({'text_wrap': True, 'valign': 'top'}) # affiche le retour chariot
        # Définir le format pour l'en-tête (gras + background bleu ciel)
        header_f = workbook.add_format({'text_wrap': True,  
                                        'bold': True,       # Texte en gras
                                        'valign': 'top'     # Aligné en haut de la cellule
                                    })
        # Appliquer le format à la première ligne (les en-têtes)
        worksheet.set_row(0, 40, header_f)
        for col, value in enumerate(dp.output_col('SEGU')):  # On part de 1 pour ignorer les en-têtes
            worksheet.write(0, col, value, header_f)
        worksheet.freeze_panes(1, 0)
        for row_num, value in enumerate(df[dp.output_col('SEGU')[0]].values, 1):  # On part de 1 pour ignorer les en-têtes
            worksheet.write(row_num, 0, value, internal_f)
        worksheet.set_column('B:B', 5, toverify_f)  ##### CLE
        worksheet.set_column('C:C', 10, final_f)  ##### CODE OP
        worksheet.set_column('D:D', 20, final_wf)  ##### DATE OP
        worksheet.set_column('E:E', 10, internal_f)  #####  MENTION SPECIFIQUE
        worksheet.set_column('F:F', 20, toverify_wf)  ##### CATEGORIE
        worksheet.set_column('G:G', 20, toverify_wf)  ##### INTITULE
        worksheet.set_column('H:H', 20, final_f)  ##### GENCOD
        worksheet.set_column('I:I', 20, toverify_f)  ##### MARQUE
        worksheet.set_column('J:J', 20, format1)  ##### ORIGINE
        worksheet.set_column('K:K', 20, internal_f)  ##### MECAPROMO
        worksheet.set_column('L:L', 10, bool_f)  ##### RONDE DES MARQUES
        worksheet.set_column('M:M', 40, format1)  ##### DESCRIPTIF     
        worksheet.set_column('N:N', 20, toverify_f)  ##### PRIX AU KG
        worksheet.set_column('O:O', 20, toverify_f)  ##### PVC MAXI
        worksheet.set_column('P:P', 10, toverify_f)  ##### BONUS
        worksheet.set_column('Q:Q', 10, format1)  ##### BONUS
        worksheet.set_column('R:R', 10, format1)  ##### RI EN €
        worksheet.set_column('S:S', 10, format1)  ##### RI EN %
        worksheet.set_column('T:T', 10, format1)  ##### PVC NET
        worksheet.set_column('U:U', 20, toverify_wf)  ##### LOT VIRTUEL
        worksheet.set_column('V:V', 20, toverify_wf)  ##### PRIX AU KG DU LOT VIRTUEL
        worksheet.set_column('W:W', 40, format1)  ##### MARKET DESCRIPTIF     
        worksheet.set_column('X:X', 20, toverify_f)  ##### MARKET PRIX AU KG
        worksheet.set_column('Y:Y', 20, toverify_f)  ##### MARKET PRIX AU KG
        worksheet.set_column('Z:Z', 10, toverify_f)  ##### MARKET PVC MAXI
        worksheet.set_column('AA:AA', 10, format1)  ##### MARKET BONUS
        worksheet.set_column('AB:AB', 10, format1)  ##### MARKET RI EN €
        worksheet.set_column('AC:AC', 10, format1)  ##### MARKET RI EN %
        worksheet.set_column('AD:AD', 10, format1)  ##### MARKET PVC NET
        worksheet.set_column('AE:AE', 20, toverify_wf)  ##### MARKET LOT VIRTUEL
        worksheet.set_column('AF:AF', 20, toverify_wf)  ##### MARKET PRIX AU KG DU LOT VIRTUEL
        worksheet.set_column('AG:AG', 10, final_bool_f)  ##### FORMAT GV
        worksheet.set_column('AH:AH', 10, final_bool_f)  ##### FORMAT MV
        worksheet.set_column('AI:AI', 10, final_bool_f)  ##### FORMAT MVK
        worksheet.set_column('AJ:AJ', 10, bool_f)  ##### FORMAT PV
        worksheet.set_column('AK:AK', 10, useless_f)   ##### VIDE_2                 ##### PRODUIT DE UNE
        worksheet.set_column('AL:AL', 10, format1)  ##### PRODUIT EN DER
        worksheet.set_column('AM:AM', 10, format1)  ##### MISE EN AVANT
        worksheet.set_column('AN:AN', 10, bool_f) #### SR SEGU MARKET
        worksheet.set_column('AO:AO', 20, final_f)  ##### PICTO
        worksheet.set_column('AP:AP', 5, final_bool_f)  ##### SR
        worksheet.set_column('AQ:AQ', 10, final_bool_f)  ##### AFFICHE
        worksheet.set_column('AR:AR', 10, useless_f)  ##### INFO COMPLEMENTAIRES 
        worksheet.set_column('AS:AS', 10, toverify_bool_f) ##### SELECTION FRANCAP
        worksheet.set_column('AT:AT', 10, toverify_bool_f)  ##### SELECTION CODIFRANCE
        worksheet.set_column('AU:AU', 20, final_f)  ##### INFO COMPLEMENTAIRES
        worksheet.set_column('AV:AV', 20, final_f)  ##### PHOTO1
        worksheet.set_column('AW:AW', 20, final_f)  ##### PHOTO2
        worksheet.set_column('AX:AX', 20, final_f)  ##### PHOTO3
        worksheet.set_column('AY:AY', 20, final_f)  ##### PHOTO4
        worksheet.set_column('AZ:AZ', 20, final_f)  ##### PHOTO5
        worksheet.set_column('BA:BA', 20, final_f)  ##### PHOTO6
        worksheet.set_column('BB:BB', 20, final_f)  ##### PHOTO7
        worksheet.set_column('BC:BC', 20, final_f)  ##### PHOTO8
        worksheet.set_column('BD:BD', 20, format1)  ##### DESCRIPTIF_2
        worksheet.set_column('DE:DE', 20, format1)  ##### PRIX AU KG_2
        worksheet.set_column('DF:DF', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_2
        worksheet.set_column('DG:DG', 20, format1)  ##### DESCRIPTIF_3
        worksheet.set_column('DH:DH', 20, format1)  ##### PRIX AU KG_3
        worksheet.set_column('BI:BI', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_3
        worksheet.set_column('BJ:BJ', 20, format1)  ##### DESCRIPTIF_4
        worksheet.set_column('BK:BK', 20, format1)  ##### PRIX AU KG_4
        worksheet.set_column('BL:BL', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_4
        worksheet.set_column('BM:BM', 20, format1)  ##### DESCRIPTIF_5
        worksheet.set_column('BN:BN', 20, format1)  ##### PRIX AU KG_5
        worksheet.set_column('BO:BO', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_5
        worksheet.set_column('BP:BP', 20, format1)  ##### DESCRIPTIF_6
        worksheet.set_column('BQ:BQ', 20, format1)  ##### PRIX AU KG_6
        worksheet.set_column('BR:BR', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_6
        worksheet.set_column('BS:BS', 15, format1)  ##### SUPER_Page
        worksheet.set_column('BT:BT', 15, format1)  ##### SUPER_Rang
        worksheet.set_column('BU:BU', 15, format1)  ##### SUPER_Case
        worksheet.set_column('BV:BV', 15, format1)  ##### EXPRESS_Page
        worksheet.set_column('BW:BW', 15, format1)  ##### EXPRESS_Rang
        worksheet.set_column('BX:BX', 15, format1)  ##### EXPRESS_Case
        worksheet.set_column('BY:BY', 15, format1)  ##### MARKET_Page
        worksheet.set_column('BZ:BZ', 15, format1)  ##### MARKET_Rang
        worksheet.set_column('CA:CA', 15, format1)  ##### MARKET_Case
        worksheet.set_column('CB:CB', 15, format1)  ##### REGIO_Page
        worksheet.set_column('CC:CC', 15, format1)  ##### REGIO_Rang
        worksheet.set_column('CD:CD', 15, format1)  ##### REGIO_Case
        worksheet.set_column('CE:CE', 15, format1)  ##### SUPER_WP
        worksheet.set_column('CF:CF', 15, format1)  ##### EXPRESS_WP
        worksheet.set_column('CG:CG', 15, format1)  ##### MARKET_WP
        return worksheet

    def set_excel_file(self, output):
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_output = self.prepare_to_excel()
            df_output.to_excel(writer, sheet_name='COCCINELLE', index=False)
            #df_output_m.to_excel(writer, sheet_name='COCCIMARKET', index=False)            

            # Obtenir l'objet workbook et worksheet
            workbook  = writer.book
            worksheet = writer.sheets['COCCINELLE']
            #worksheet_m = writer.sheets['COCCIMARKET']
            
            worksheet = self.set_worksheet(worksheet, workbook, df_output)
            #worksheet_m = self.set_worksheet(worksheet_m, workbook, df_output_m)

            output.seek(0)
            with open('formatted_output.xlsx', 'wb') as f:
                f.write(output.getvalue())

        return output

class Codifrance(Operation):
    def __init__(self):
        # Appelle le constructeur de la classe parent
        super().__init__()
        self.df_nat = None

    def get_new_list_from_customer(self, liste_codi):
        
        codisheets = pd.ExcelFile(liste_codi).sheet_names
        for sheet in codisheets:
            if 'FINALE' in codisheets:
                self.main_df = pd.read_excel(liste_codi, sheet_name='FINALE', header=0)
                self.main_df = self.main_df.dropna(subset=['GENCOD'])
            elif 'Finale' in codisheets:
                self.main_df = pd.read_excel(liste_codi, sheet_name='Finale', header=0)
                self.main_df = self.main_df.dropna(subset=['GENCOD'])
            elif 'Francap' in codisheets:
                self.df_nat = pd.read_excel(liste_codi, sheet_name='Francap', header=0)

        self.code_op = self.main_df['CODE OP'][0]
        self.date_op = self.main_df['DATE OP'][0]



    def set_main(self, st=None):
        if st is not None:
            self.st = st

        self.main_df = cp.apply_codi_process(self, self.main_df, 'NAT')
        rename_dict = {'TEST' : 'LALALERE',
                    'PRIX AU KG OU L AVEC ET SANS RI' : 'PRIX AU KG/L',
                     'FORMAT SUPER' : 'FORMAT GV',
                     'FORMAT EXPRESS' : 'FORMAT MV', 
                     'FORMAT COCCIMKT' : 'FORMAT MVK',
                     'FORMAT REGIONAL pv' : 'FORMAT PV'}
        
        col2remove = ['CODE', 'INFO COMPLEMENTAIRES']
        col2add = {}
        #self.df_codi = dp.clean(self.df_codi, rename_dict, col2remove, col2add)
        #self.df_codi = cp.apply_codi_process(self.st, self.df_codi, self.code_op,self.date_op, 'CODI')
        #self.main_df = cp.fusion_codifrance(self.df_codi, self.main_df).reset_index(drop=True)
        self.main_df.CLE = self.main_df.index + 1
        


    def prepare_to_excel(self):
        df = self.main_df[dp.output_col('CODI')]
        
        col_bool = dp.col_bool('CODI')
        for col in col_bool:
            df[col] = self.main_df[col].apply(lambda x : 'X' if x else '')
        return df

    def set_excel_file(self, output):
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_output = self.prepare_to_excel()
            df_output.to_excel(writer, startrow=0, sheet_name='CODI', index=False)

            # Obtenir l'objet workbook et worksheet
            workbook  = writer.book
            worksheet = writer.sheets['CODI']

            internal_f = workbook.add_format({ 'bg_color': '#E9DACE', 'font_color':'#E9DACE',  'text_wrap': True, 'valign': 'top'})  ##### Variable interne  couleur specifique à Codi
            format1 = workbook.add_format({'text_wrap': True, 'valign': 'top'}) #colonne neutre sans transfo
            useless_f = workbook.add_format({'font_color':'#000000' , 'bg_color': '#000000'}) # colonne inutile à supprimer
            bool_f = workbook.add_format({'align': 'center', 'valign': 'top'}) #gris
            final_bool_f = workbook.add_format({'align': 'center', 'font_color': '#3470C9', 'bold': True, 'valign': 'top'})
            toverify_bool_f = workbook.add_format({'align': 'center', 'font_color': '#3470C9', 'bold': False, 'valign': 'top'})
            toverify_f = workbook.add_format({'font_color': '#3470C9', 'bold': False, 'valign': 'top'})  #bleu
            toverify_wf = workbook.add_format({'font_color': '#3470C9', 'bold': False, 'text_wrap': True, 'valign': 'top'})  #bleu
            final_f = workbook.add_format({'font_color': '#3470C9', 'bold': True, 'valign': 'top'})  #bleu
            final_wf = workbook.add_format({'font_color': '#3470C9', 'bold': True, 'text_wrap': True, 'valign': 'top'})  #bleu
            format_w = workbook.add_format({'text_wrap': True, 'valign': 'top'}) # affiche le retour chariot

            # Définir le format pour l'en-tête (gras + background bleu ciel)
            header_f = workbook.add_format({'text_wrap': True,  
                                            'bold': True,       # Texte en gras
                                            'valign': 'top'     # Aligné en haut de la cellule
                                        })
            # Appliquer le format à la première ligne (les en-têtes)
            worksheet.set_row(0, 40, header_f)
            for col, value in enumerate(dp.output_col('CODI')):  # On part de 1 pour ignorer les en-têtes
                worksheet.write(0, col, value, header_f)

            worksheet.freeze_panes(1, 0)

            for row_num, value in enumerate(df_output[dp.output_col('CODI')[0]].values, 1):  # On part de 1 pour ignorer les en-têtes
                worksheet.write(row_num, 0, value, internal_f)

            worksheet.set_column('B:B', 5, toverify_f)  ##### CLE
            worksheet.set_column('C:C', 10, final_f)  ##### CODE OP
            worksheet.set_column('D:D', 20, final_wf)  ##### DATE OP
            worksheet.set_column('E:E', 10, toverify_f)  ##### MENTION SPECIFIQUE
            worksheet.set_column('F:F', 20, toverify_wf)  ##### CATEGORIE
            worksheet.set_column('G:G', 20, toverify_wf)  ##### INTITULE
            worksheet.set_column('H:H', 20, final_f)  ##### GENCOD
            worksheet.set_column('I:I', 20, toverify_f)  ##### MARQUE
            worksheet.set_column('J:J', 20, toverify_f)  ##### ORIGINE
            worksheet.set_column('K:K', 40, internal_f)  ##### MECAPROMO
            worksheet.set_column('L:L', 20, toverify_wf)  ##### RONDE DES MARQUES
            worksheet.set_column('M:M', 20, toverify_wf)  ##### DESCRIPTIFinternal_f)  ##### MECAPROMO
            worksheet.set_column('N:N', 20, format1)  ##### PRIX AU KG
            worksheet.set_column('O:O', 10, toverify_f)  ##### PVC MAXI
            worksheet.set_column('P:P', 10, format1)  ##### BONUS
            worksheet.set_column('Q:Q', 10, format1)  ##### BONUS
            worksheet.set_column('R:R', 10, format1)  ##### RI EN €
            worksheet.set_column('S:S', 10, format1)  ##### RI EN %
            worksheet.set_column('T:T', 10, format1)  ##### PVC NET
            worksheet.set_column('U:U', 20, format1)  ##### LOT VIRTUEL
            worksheet.set_column('V:V', 10, toverify_wf)  ##### PRIX AU KG DU LOT VIRTUEL
            worksheet.set_column('W:W', 10, useless_f)   
            worksheet.set_column('X:X', 10, useless_f) 
            worksheet.set_column('Y:Y', 10, useless_f)  
            worksheet.set_column('Z:Z', 10, toverify_bool_f)  
            worksheet.set_column('AA:AA', 10, toverify_bool_f)  
            worksheet.set_column('AB:AB', 10, toverify_bool_f)  
            worksheet.set_column('AC:AC', 10, toverify_bool_f) 
            worksheet.set_column('AD:AD', 20, useless_f)  
            worksheet.set_column('AE:AE', 10, toverify_bool_f) 
            worksheet.set_column('AF:AF', 10, toverify_bool_f) 
            worksheet.set_column('AG:AG', 10, final_bool_f)  ##### AFFICHE
            worksheet.set_column('AH:AH', 10, toverify_bool_f) ##### SELECTION FRANCAP

 
            worksheet.set_column('AI:AI', 10, toverify_f)  ##### SELECTION CODIFRANCE
            worksheet.set_column('AJ:AJ', 20, toverify_f)  ##### INFO COMPLEMENTAIRES
            worksheet.set_column('AK:AK', 20, final_f)  ##### PHOTO1
            worksheet.set_column('AL:AL', 20, useless_f)  
            worksheet.set_column('AM:AM', 20, final_f)  ##### PHOTO3
            worksheet.set_column('AN:AN', 20, final_f)  ##### PHOTO4
            worksheet.set_column('AO:AO', 20, final_f)  ##### PHOTO5
            worksheet.set_column('AP:AP', 20, final_f)  ##### PHOTO6
            worksheet.set_column('AQ:AQ', 20, final_f)  ##### PHOTO7
            worksheet.set_column('AR:AR', 20, final_f)  ##### PHOTO8
            worksheet.set_column('AS:AS', 20, toverify_wf)  ##### DESCRIPTIF_2
            worksheet.set_column('AT:AT', 20, format1)  ##### PRIX AU KG_2
            worksheet.set_column('AU:AU', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_2
            worksheet.set_column('AV:AV', 20, toverify_wf)  ##### DESCRIPTIF_3
            worksheet.set_column('AW:AW', 20, format1)  ##### PRIX AU KG_3
            worksheet.set_column('AX:AX', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_3
            worksheet.set_column('AY:AY', 20, toverify_wf)  ##### DESCRIPTIF_4
            worksheet.set_column('AZ:AZ', 20, format1)  ##### PRIX AU KG_4
            worksheet.set_column('BA:BA', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_4
            worksheet.set_column('BB:BB', 20, toverify_wf)  ##### DESCRIPTIF_5
            worksheet.set_column('BC:BC', 20, format1)  ##### PRIX AU KG_5
            worksheet.set_column('BD:BD', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_5
            worksheet.set_column('BE:BE', 20, toverify_wf)  ##### DESCRIPTIF_6
            worksheet.set_column('BF:BF', 20, format1)  ##### PRIX AU KG_6
            worksheet.set_column('BG:BG', 20, format1)  ##### PRIX AU KG DU LOT VIRTUEL_6
            worksheet.set_column('BH:BH', 15, format1)  ##### SUPER_Page
            worksheet.set_column('BI:BI', 15, format1)  ##### SUPER_Rang
            worksheet.set_column('BJ:BJ', 15, format1)  ##### SUPER_Case
            worksheet.set_column('BK:BK', 15, format1)  ##### EXPRESS_Page
            worksheet.set_column('BL:BL', 15, format1)  ##### EXPRESS_Rang
            worksheet.set_column('BM:BM', 15, format1)  ##### EXPRESS_Case
            worksheet.set_column('BN:BN', 15, format1)  ##### MARKET_Page
            worksheet.set_column('BO:BO', 15, format1)  ##### MARKET_Rang
            worksheet.set_column('BP:BP', 15, format1)  ##### MARKET_Case
            worksheet.set_column('BQ:BQ', 15, format1)  ##### REGIO_Page
            worksheet.set_column('BR:BR', 15, format1)  ##### REGIO_Rang
            worksheet.set_column('BS:BS', 15, format1)  ##### REGIO_Case
            worksheet.set_column('BT:BT', 15, format1)  ##### SUPER_WP
            worksheet.set_column('BU:BU', 15, format1)  ##### EXPRESS_WP
            worksheet.set_column('BV:BV', 15, format1)  ##### MARKET_WP

            output.seek(0)
            with open('formatted_output.xlsx', 'wb') as f:
                f.write(output.getvalue())
        return output
    
    def save(self, filepath):
        try:
            self.detach_session()
            with open(filepath, 'wb') as file:
                pickle.dump(self, file)
                return 'ok'
        except Exception as e:
                return e
        