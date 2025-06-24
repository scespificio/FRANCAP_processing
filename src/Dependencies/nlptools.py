from spellchecker import SpellChecker
import pandas as pd
from dotenv import load_dotenv
import os


SPELL = SpellChecker(language='fr')
SPELL.word_frequency.add("€")
SPELL.word_frequency.add("BSA")
SPELL.word_frequency.add("BOF")
SPELL.word_frequency.add("animalerie")

word2add = ["€", "BSA", "BOF", "animalerie", "UE", "Asie", "Amérique", "Amériques", "2ème", "Monbéliard"]

load_dotenv(dotenv_path='../.env')


# main.py
from dotenv import load_dotenv
import os

load_dotenv()  # Charge le fichier .env (placé dans le même dossier ou chemin spécifié)

print("CUSTOMER =", os.getenv("CUSTOMER"))
print("CONFIG_FILE =", os.getenv("CONFIG_FILE"))

CONFIG_PATH = os.getenv('CONFIG_PATH')
DEPARTEMENTS = pd.read_csv(CONFIG_PATH + '/' + 'departements_francais.csv').nom.to_list()
PAYS = pd.read_csv(CONFIG_PATH + '/' + 'liste_pays_fr.csv').nom.to_list()

for word in word2add:
    SPELL.word_frequency.add(word)

for dep in DEPARTEMENTS:
    SPELL.word_frequency.add(dep)

for pays in PAYS:
    SPELL.word_frequency.add(pays)



def correct_orth(text):
    # Découper le texte en lignes pour conserver les sauts de ligne
    lines = text.splitlines()
    corrected_lines = []

    try:
    # Parcourir chaque ligne pour la corriger
        for line in lines:
            words = line.split()  # Découper la ligne en mots
            # Appliquer la correction sur chaque mot
            corrected_words = [SPELL.correction(word.lower()).capitalize() if word[0].isupper() else SPELL.correction(word) for word in words]
            # Remplacer uniquement si une correction existe, sinon conserver le mot original
            corrected_final = [word if cword is None else cword for cword, word in zip(corrected_words, words)]
            corrected_lines.append(" ".join(corrected_final))  # Réassembler les mots corrigés en ligne
    except Exception as e:
        raise TypeError(f"IL Y A UNE ERREUR DANS LE FICHIER : Veuillez corriger {text}")

    # Réassembler toutes les lignes en conservant les sauts de ligne
    return "\n".join(corrected_lines)   