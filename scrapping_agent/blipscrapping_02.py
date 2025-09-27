#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from weasyprint import HTML, CSS

# Liste de mots vides courants à exclure dans l'analyse
STOP_WORDS = {
    "de", "la", "le", "les", "et", "des", "en", "un", "une", "du", "pour", "sur",
    "avec", "par", "au", "aux", "ce", "ces", "dans", "qui", "que", "se", "plus",
    "ne", "pas", "ou", "mais", "comme", "a", "il", "elle", "nous", "vous", "ils",
    "elles", "son", "sa", "ses", "être", "avoir", "faire", "tout", "sans", "sont"
}

def scraper_titres(url="https://techcrunch.com/"):
    """Scrape les titres d'articles récents sur TechCrunch."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erreur HTTP {response.status_code} lors du scraping")
    soup = BeautifulSoup(response.text, 'html.parser')
    titres = []
    for a in soup.find_all('a', class_='post-block__title__link'):
        titre = a.get_text(strip=True)
        if titre:
            titres.append(titre)
    return titres

def analyser_frequence_mots(titres):
    """Analyse la fréquence des mots dans les titres, excluant les stop words."""
    mots = []
    for titre in titres:
        mots_titre = re.findall(r'\b\w+\b', titre.lower())
        mots.extend([mot for mot in mots_titre if mot not in STOP_WORDS and len(mot) > 2])
    compteur = Counter(mots)
    return compteur.most_common(10)

def generer_html(mots_freq, titres):
    """Génère un contenu HTML stylé pour le rapport PDF."""
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rapport Tendances Tech</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ text-align: center; color: #2c3e50; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #2980b9; padding-bottom: 5px; }}
            ul {{ list-style-type: square; padding-left: 20px; }}
            table {{ border-collapse: collapse; width: 50%; margin: 20px auto; }}
            th, td {{ border: 1px solid #2980b9; padding: 8px; text-align: center; }}
            th {{ background-color: #2980b9; color: white; }}
            .footer {{ font-size: 0.8em; text-align: center; margin-top: 40px; color: #999; }}
        </style>
    </head>
    <body>
        <h1>Rapport d'analyse des tendances tech par scraping</h1>
        <p>Ce rapport présente une analyse des titres des articles récents extraits de TechCrunch.</p>
        <p><strong>Nombre d'articles analysés :</strong> {len(titres)}</p>

        <h2>Top 10 des mots clés</h2>
        <table>
            <thead>
                <tr><th>Mot clé</th><th>Occurrences</th></tr>
            </thead>
            <tbody>
    """
    for mot, freq in mots_freq:
        html += f"<tr><td>{mot}</td><td>{freq}</td></tr>"
    html += """
            </tbody>
        </table>

        <h2>Liste des titres analysés</h2>
        <ul>
    """
    for titre in titres:
        html += f"<li>{titre}</li>"
    html += """
        </ul>

        <div class="footer">
            Généré automatiquement avec WeasyPrint - blipscrapping_02.py
        </div>
    </body>
    </html>
    """
    return html

def generer_pdf(html_content, fichier_pdf):
    """Génère un PDF à partir du contenu HTML avec WeasyPrint."""
    HTML(string=html_content).write_pdf(fichier_pdf)
    print(f"PDF généré avec succès : {fichier_pdf}")

if __name__ == "__main__":
    try:
        titres = scraper_titres()
        if not titres:
            print("Aucun titre récupéré, vérifiez l'URL ou la structure du site.")
        else:
            mots_freq = analyser_frequence_mots(titres)
            html = generer_html(mots_freq, titres)
            generer_pdf(html, "rapport_tendances_tech_weasyprint.pdf")
    except Exception as e:
        print(f"Erreur : {e}")
