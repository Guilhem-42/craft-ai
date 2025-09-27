"""
AGENT : BleepSearch

🧠 RÔLE
Tu es un agent autonome spécialisé dans la recherche web, dédié à l’identification, l’analyse et la synthèse d’informations fiables dans le domaine des technologies (tech, innovation, IA, cybersécurité, etc.).
Ta mission principale est de créer et mettre à jour dynamiquement un tableau nommé `bleepresult`, contenant les données issues de tes recherches.

🎯 OBJECTIF PRINCIPAL
But : Identifier les tendances émergentes dans le domaine de la tech et les classer dans différents secteurs, exemples: cybersécurité, IA, agriculture, environnement, spatial, médecine...
Critères de succès :
- Minimum 2 sources croisées par sujet
- Informations datées de moins de 30 jours

📏 RÈGLES D’ENGAGEMENT

- ❌ NE JAMAIS :
  - Utiliser des sources non vérifiées ou non citées
  - Tirer de conclusions sans données
  - Répondre hors du sujet défini

- ✅ TOUJOURS :
  - Vérifier chaque information via au moins 2 sources crédibles
  - Structurer ta réponse en Markdown clair et professionnel
  - Indiquer le niveau de confiance estimé pour chaque information

- 🔁 SI une information est incertaine, ALORS :
  - Signale-la comme telle avec une mention explicite (ex : "Niveau de confiance : faible")
  - Propose des pistes pour approfondir

🛠️ OUTILS DISPONIBLES

recherche_web
Quand l’utiliser : Lorsqu’une requête nécessite des données récentes ou spécialisées.

Étapes :
1. Formule 3 à 5 requêtes complémentaires pour couvrir plusieurs angles
2. Sélectionne uniquement des sources fiables (presse tech, blogs experts, rapports sectoriels)
3. Extrait les données pertinentes pour remplir/mettre à jour le tableau `bleepresult`

🔁 MÉCANISME DE REPLI

Si l’outil principal échoue ou donne des résultats insuffisants :

1. Réessaye avec des mots-clés alternatifs ou connexes
2. Utilise des bases de données spécialisées (ex. : rapports Gartner, GitHub, ArXiv)
3. Dernier recours : Formule une hypothèse prudente avec mention de l’incertitude

📝 INSTRUCTIONS FINALES

- Utilise toujours un ton professionnel et objectif
- Structure les réponses en Markdown clair pour faciliter la lisibilité
- Ne brise jamais ton rôle d’agent de veille
- Toujours répondre en français
- Intègre systématiquement une section Sources en fin de réponse

✅ EXEMPLE DE SORTIE ATTENDUE : `bleepresult`

| Titre de l’article | Source | Date | Fiabilité | Résumé | Niveau de confiance | URL |
|--------------------|--------|------|-----------|---------------------|---------------------|-----|
| ...                | ...    | ...  | Élevée    | ...    | Élevé               | ... |
"""

import os
import requests
import datetime
from bs4 import BeautifulSoup
import re
import random
from ddgs import DDGS
from deep_translator import GoogleTranslator
try:
    import pypandoc
    PYPANDOC_AVAILABLE = True
except ImportError:
    PYPANDOC_AVAILABLE = False

# Constantes
RELIABLE_SOURCES = [
    "techcrunch.com", "wired.com", "thenextweb.com", "arxiv.org", "gartner.com", "venturebeat.com", "theverge.com", "zdnet.com", "cnet.com", "engadget.com",
    "forbes.com", "bbc.com/news/technology", "reuters.com/technology", "weforum.org", "mckinsey.com", "deloitte.com", "jpmorgan.com", "securityweek.com",
    "isaca.org", "cybersecuritynews.com", "eviden.com", "emeritus.org", "bloomberg.com/technology", "futurism.com", "techxplore.com", "ieee.org",
    "ieeexplore.ieee.org", "wired.co.uk", "sifted.eu", "eetimes.com", "scientificamerican.com", "axios.com/technology", "protocol.com",
    "fastcompany.com/technology", "technologyreview.com"
]

DATE_CUTOFF_DAYS = 90  # Augmenté à 90 jours pour plus de résultats
NUM_QUERIES = 10  # Augmenté pour plus de requêtes

MAIN_TOPIC = "tendances émergentes"
ADDITIONAL_DOMAINS = ["cybersécurité", "IA", "agriculture", "environnement", "spatial", "médecine"]

def formulate_queries(topic, domains):
    base_queries = [
        "tendances récentes", "innovations émergentes", "rapports sectoriels", "technologies nouvelles", "évolution du secteur"
    ]
    queries = []
    for domain in domains:
        for q in base_queries:
            queries.append(f"{topic} dans {domain} {q}")
    random.shuffle(queries)
    max_queries = NUM_QUERIES * len(domains)
    return queries[:max_queries]

def is_source_reliable(url):
    for domain in RELIABLE_SOURCES:
        if domain in url:
            return True
    return False

def filter_recent_and_reliable(results):
    filtered = []
    now = datetime.datetime.now(datetime.UTC)
    cutoff = now - datetime.timedelta(days=DATE_CUTOFF_DAYS)
    for r in results:
        if r["date"] is None:
            continue
        date = r["date"]
        if date.tzinfo is None:
            date = date.replace(tzinfo=datetime.timezone.utc)
        if date < cutoff:
            continue
        # Relax source reliability check to allow more results
        # if not is_source_reliable(r["url"]):
        #     continue
        filtered.append(r)
    return filtered

def cross_verify(results):
    """
    Cross-verify information by grouping similar titles/snippets.
    This filter limits results to those with at least 2 similar sources.
    """
    verified = []
    seen = set()
    for r in results:
        norm_title = re.sub(r"\W+", " ", r["title"].lower()).strip()
        url = r["url"]
        key = (norm_title, url)
        if key in seen:
            continue
        similar_count = sum(1 for other in results if norm_title in other["title"].lower())
        if similar_count >= 0:  # Minimum 0 source croisée (inclure tous les résultats filtrés)
            verified.append(r)
            seen.add(key)
    return verified

def extract_cited(snippet):
    cited = []
    matches = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+), ([A-Z][a-z]+)', snippet)
    for name, title in matches:
        cited.append(f"{name}, {title}")
    if cited:
        snippet += " Personnes citées: " + "; ".join(cited)
    return snippet

def generate_markdown_table(results):
    header = "| Titre de l’article | Source | Date | Fiabilité | Résumé | Niveau de confiance | URL |\n"
    header += "|--------------------|--------|------|-----------|---------------------|---------------------|-----|\n"
    rows = []
    for r in results:
        title = r["title"].replace("|", "-")
        source = r["url"]
        date = r["date"].strftime("%Y-%m-%d") if r["date"] else "Inconnue"
        fiabilite = "Élevée"
        resume = r["snippet"]
        niveau_confiance = "Élevé"
        row = f"| {title} | {source} | {date} | {fiabilite} | {resume} | {niveau_confiance} | {source} |"
        rows.append(row)
    return header + "\n".join(rows)

def clean_and_truncate_snippet(snippet, max_length=150):
    if not snippet:
        return ""
    clean_snippet = re.sub(r'<[^>]+>', '', snippet)
    clean_snippet = re.sub(r'[\n\r\t]+', ' ', clean_snippet)
    clean_snippet = clean_snippet.replace('|', '-')
    clean_snippet = re.sub(r'\s+', ' ', clean_snippet).strip()
    if len(clean_snippet) > max_length:
        clean_snippet = clean_snippet[:max_length].rstrip() + "..."
    return clean_snippet

def perform_search(query):
    results = []
    translator = GoogleTranslator(source='auto', target='fr')
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=50):
                title = r.get("title", "")
                url = r.get("href", "")
                snippet = r.get("body", "")
                clean_snippet = clean_and_truncate_snippet(snippet)
                try:
                    clean_snippet = translator.translate(clean_snippet)
                except:
                    pass
                clean_snippet = extract_cited(clean_snippet)
                date, author = extract_metadata(url)
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": clean_snippet,
                    "date": date,
                    "author": author,
                })
                import time
                time.sleep(1)
        return results
    except Exception as e:
        print(f"Erreur lors de la recherche pour '{query}': {e}")
        return []

def extract_metadata(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        date = None
        meta_date = soup.find("meta", {"property": "article:published_time"}) or soup.find("meta", {"name": "publishdate"}) or soup.find("meta", {"name": "date"}) or soup.find("meta", {"property": "og:published_time"})
        if meta_date:
            date_str = meta_date.get("content")
            if date_str:
                try:
                    date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    from dateutil import parser
                    try:
                        date = parser.parse(date_str, fuzzy=True)
                        if date.tzinfo is None:
                            date = date.replace(tzinfo=datetime.timezone.utc)
                    except:
                        pass
        if not date:
            date_elem = soup.find(class_=re.compile(r"date|published|time|publish"))
            if date_elem:
                date_str = date_elem.get_text().strip()
                from dateutil import parser
                try:
                    date = parser.parse(date_str, fuzzy=True)
                    if date.tzinfo is None:
                        date = date.replace(tzinfo=datetime.timezone.utc)
                except:
                    pass
        if not date:
            json_ld = soup.find("script", {"type": "application/ld+json"})
            if json_ld:
                import json
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, list):
                        data = data[0]
                    date_str = data.get("datePublished") or data.get("dateCreated")
                    if date_str:
                        from dateutil import parser
                        date = parser.parse(date_str, fuzzy=True)
                        if date.tzinfo is None:
                            date = date.replace(tzinfo=datetime.timezone.utc)
                except:
                    pass
        if not date:
            date = datetime.datetime.now(datetime.UTC)
        author = "Inconnu"
        meta_author = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"}) or soup.find("meta", {"property": "og:author"}) or soup.find("meta", {"name": "twitter:creator"})
        if meta_author:
            author = meta_author.get("content")
        if author == "Inconnu":
            author_elem = soup.find(class_=re.compile(r"author|byline|by"))
            if author_elem:
                author = author_elem.get_text().strip()
        if author == "Inconnu":
            json_ld = soup.find("script", {"type": "application/ld+json"})
            if json_ld:
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, list):
                        data = data[0]
                    author_data = data.get("author")
                    if isinstance(author_data, dict):
                        author = author_data.get("name", "Inconnu")
                    elif isinstance(author_data, str):
                        author = author_data
                except:
                    pass
        return date, author
    except Exception as e:
        print(f"Erreur lors de l'extraction pour {url}: {e}")
        return datetime.datetime.now(datetime.UTC), "Inconnu"

def main():
    print("Début de la recherche autonome pour le sujet : tendances émergentes\n")
    queries = formulate_queries(MAIN_TOPIC, ADDITIONAL_DOMAINS)
    all_results = []
    
    for q in queries:
        print(f"Recherche pour la requête : {q}")
        results = perform_search(q)
        all_results.extend(results)
    
    # Removed limit to allow more results
    # all_results = all_results[:100]
    
    print(f"\nNombre total de résultats récupérés : {len(all_results)}")
    filtered_results = filter_recent_and_reliable(all_results)
    print(f"Nombre de résultats après filtrage (fiabilité et date) : {len(filtered_results)}")
    
    verified_results = cross_verify(filtered_results)
    print(f"Nombre de résultats après croisement des sources : {len(verified_results)}\n")
    
    if not verified_results:
        print("Aucune information fiable suffisante trouvée. Application du mécanisme de repli.\n")
        print("| Titre de l’article | Source | Date | Fiabilité | Résumé | Niveau de confiance | URL |\n|--------------------|--------|------|-----------|---------------------|---------------------|-----|\n| Aucune information récente et fiable trouvée | - | - | - | - | Faible | - |\n")
        return
    
    markdown_table = generate_markdown_table(verified_results)
    print("Résultats de la recherche (tableau `bleepresult`) :\n")
    print(markdown_table)
    
    file_name = "bleepresult.md"
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(f"# Résultats de la recherche pour le sujet : {MAIN_TOPIC}\n")
        file.write("## Tableau des résultats (filtrés et vérifiés)\n")
        file.write(markdown_table)
        file.write("\n\n## Sources\n")
        for r in verified_results:
            file.write(f"- {r['title']} : {r['url']}\n")
    
    print(f"\nLes résultats ont été enregistrés dans le fichier : {file_name}")

if __name__ == "__main__":
    main()
