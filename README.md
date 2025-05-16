# AA_FRA_MP

# Detail du process Cofifrance

1. définition des colonnes de sortie
2. si nouvelle saisie:
    2.1 ajuster le tableau d'entrée:
        - elimination de colonnes superflue
        - renommage des colonnes
        - inserer les colonnes manquantes 

3. transfo et process
    3.1: reglage CODE OP, DATE OP, SELECTION FRANCAP, SELECTION CODIFRANCE
    3.2 identifier colonnes bolléennes
    3.3 Ne pas modifier:
        - AFFICHE, PVS MAXI
        - Mettre CATALOG à True
    
    3.4 Revision des GENCOD: (nombre entier transforme en str)
    3.5 fragmentation des photos
        - Fragmentation de GENCOD dans PHOTO_2 à 6

    3.5 Correction des dDESCRIPTIF
    3.6: identification et fragmentation des groupements:
        - reglage de SR en fonction d'une ligne groupé ou non
        - Fragmentation de DESCRIPTIF dans DESCRITIF_2 à 6
        - Fragmentation de PRIX AU KL dans PRIX AU KL_2 à 6
    
    3.8: correction  CATEGORIE   
        3.8: correction  MENTIONS SPECIFIQUE   
        3.8: correction  MARQUE   
                3.8: identifier les PICTO 
                'PRIX AU KG'
                'LOT VIRTUEL'
                'PRIX AU KG DU LOT VIRTUEL'




