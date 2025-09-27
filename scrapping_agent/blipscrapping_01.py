import requests
from bs4 import BeautifulSoup
from collections import Counter
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import re

# Liste de mots vides courants à exclure dans l'analyse
STOP_WORDS = {
    "de", "la", "le", "les", "et", "des", "en", "un", "une", "du", "pour", "sur",
    "avec", "par", "au", "aux", "ce", "ces", "dans", "qui", "que", "se", "plus",
    "ne", "pas", "ou", "mais", "comme", "a", "il", "elle", "nous", "vous", "ils",
    "elles", "son", "sa", "ses", "être", "avoir", "faire", "tout", "sans", "sont"
}

# Étape 1 : Scraper les titres d'articles tech
def scraper_titres(url="https://techcrunch.com/"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    titres = []

    # Exemple : récupérer les titres dans les balises <a> avec une classe spécifique
    for a in soup.find_all('a', class_='post-block__title__link'):
        titre = a.get_text(strip=True)
        if titre:
            titres.append(titre)
    return titres

# Étape 2 : Analyser la fréquence des mots dans les titres
def analyser_frequence_mots(titres):
    mots = []
    for titre in titres:
        # Nettoyer le texte, garder uniquement les mots
        mots_titre = re.findall(r'\b\w+\b', titre.lower())
        # Exclure les mots vides
        mots.extend([mot for mot in mots_titre if mot not in STOP_WORDS and len(mot) > 2])
    compteur = Counter(mots)
    return compteur.most_common(10)  # Top 10 mots

# Étape 3 : Créer un graphique des mots fréquents
def creer_graphique(mots_freq):
    mots, freq = zip(*mots_freq)
    plt.figure(figsize=(8,4))
    plt.barh(mots, freq, color='teal')
    plt.xlabel('Fréquence')
    plt.title('Top 10 des mots clés dans les titres tech')
    plt.gca().invert_yaxis()  # Inverser pour avoir le plus fréquent en haut
    plt.tight_layout()
    tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    plt.savefig(tmpfile.name)
    plt.close()
    return tmpfile.name

# Étape 4 : Générer le PDF avec résumé et graphique
def generer_pdf(mots_freq, titres, fichier_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Rapport d'analyse des tendances tech par scraping", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    intro = (
        f"Ce rapport présente une analyse des titres des articles récents extraits de TechCrunch.\n"
        f"Nombre d'articles analysés : {len(titres)}.\n"
        "Voici les mots clés les plus fréquents dans ces titres :"
    )
    pdf.multi_cell(0, 10, intro)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Top 10 des mots clés :", ln=True)
    pdf.set_font("Arial", '', 12)
    for mot, freq in mots_freq:
        pdf.cell(0, 8, f"- {mot} : {freq} occurrences", ln=True)

    # Ajouter le graphique
    chemin_image = creer_graphique(mots_freq)
    pdf.ln(10)
    pdf.image(chemin_image, x=30, w=150)

    pdf.output(fichier_pdf)

if __name__ == "__main__":
    titres = scraper_titres()
    if not titres:
        print("Erreur : aucun titre récupéré, vérifiez l'URL ou la structure du site.")
    else:
        mots_freq = analyser_frequence_mots(titres)
        nom_fichier = "rapport_tendances_tech_scraping.pdf"
        generer_pdf(mots_freq, titres, nom_fichier)
        print(f"PDF généré avec succès : {nom_fichier}")
