import pandas as pd
import requests
import logging
from typing import Optional, List, Dict
from fpdf import FPDF
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechJournalistAgent:
    def __init__(self, api_key: str = None):
        self.api_key = '5e7e6f52591e44ba982e69377cf5b8e0'
        self.endpoint = 'https://newsapi.org/v2/everything'
        self.serper_api_key = '3a416c48762aeffcf3a4f049e87f3899ecb9e3fa'
        self.serper_endpoint = 'https://google.serper.dev/search'
        self.categories = [
            "Intelligence Artificielle",
            "Chatbots",
            "Technologie",
            "Applications",
            "Réseaux Sociaux",
            "Tendances Émergentes"
        ]
        self.df: Optional[pd.DataFrame] = None
        self.followed_subjects: List[str] = []
        self.followed_journalists: List[str] = []
        self.themes = {
            "IA": ["intelligence artificielle", "ai", "machine learning", "deep learning"],
            "Chatbots": ["chatbot", "bot", "conversationnel"],
            "Tech": ["technologie", "innovation", "gadget"],
            "Apps": ["application", "app", "mobile"],
            "Social": ["réseaux sociaux", "social media", "facebook", "twitter"],
            "Trends": ["tendances", "émergentes", "futur"]
        }

    def search_tech_news(self, query: str, page_size: int = 10) -> List[Dict]:
        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': 'fr',
            'sortBy': 'publishedAt',
            'pageSize': page_size,
        }
        try:
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles for query '{query}'")
            return articles
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    def search_serper(self, query: str) -> List[Dict]:
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query
        }
        try:
            response = requests.post(self.serper_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            organic_results = data.get('organic', [])
            logger.info(f"Serper API returned {len(organic_results)} results for query '{query}'")
            return organic_results
        except Exception as e:
            logger.error(f"Error fetching Serper results: {e}")
            return []

    def scrape_link(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract main text content - this can be improved with more sophisticated extraction
            paragraphs = soup.find_all('p')
            text_content = ' '.join(p.get_text() for p in paragraphs)
            logger.info(f"Scraped content from {url} (length {len(text_content)})")
            return text_content
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""

    def classify_by_theme(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        themes = {}
        for article in articles:
            theme = article.get('source', {}).get('name', 'Autre')
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(article)
        return themes

    def select_top_articles(self, articles: List[Dict], count: int = 5) -> List[Dict]:
        # Simple selection by publishedAt date descending
        sorted_articles = sorted(articles, key=lambda x: x.get('publishedAt', ''), reverse=True)
        return sorted_articles[:count]

    def generate_pdf_review(self, articles: List[Dict], filename: str = "revue_de_presse.pdf") -> None:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Revue de Presse Tech", ln=True, align='C')
        pdf.ln(10)

        for article in articles:
            title = article.get('title', '').encode('latin-1', 'replace').decode('latin-1')
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 10, title)
            pdf.set_font("Arial", '', 10)
            author = article.get('author', 'Inconnu')
            if author:
                author = author.encode('latin-1', 'replace').decode('latin-1')
            date = article.get('publishedAt', '')[:10]
            source = article.get('source', {}).get('name', 'Inconnu')
            pdf.cell(0, 10, f"Par {author} - {date} - Source: {source}", ln=True)
            pdf.set_text_color(0, 0, 255)
            pdf.cell(0, 10, article.get('url', ''), ln=True, link=article.get('url', ''))
            pdf.set_text_color(0, 0, 0)
            # Add image if available
            image_url = article.get('urlToImage')
            if image_url:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image_path = "temp_image.jpg"
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        pdf.image(image_path, w=100)
                except Exception as e:
                    logger.warning(f"Impossible d'ajouter l'image: {e}")
            pdf.ln(10)

        pdf.output(filename)
        logger.info(f"PDF généré : {filename}")

    def add_follow_subject(self, subject: str) -> None:
        if subject not in self.followed_subjects:
            self.followed_subjects.append(subject)
            logger.info(f"Sujet suivi ajouté : {subject}")

    def add_follow_journalist(self, journalist: str) -> None:
        if journalist not in self.followed_journalists:
            self.followed_journalists.append(journalist)
            logger.info(f"Journaliste suivi ajouté : {journalist}")

    def get_followed_news(self) -> str:
        if not self.followed_subjects and not self.followed_journalists:
            return "<p>Vous ne suivez aucun sujet ou journaliste pour le moment.</p>"
        summary = "<h2>Nouvelles de vos suivis :</h2>\n"
        for subject in self.followed_subjects:
            articles = self.search_tech_news(subject, 3)
            if articles:
                summary += f"<h3>Sujet : {subject}</h3>\n<ul>\n"
                for article in articles:
                    url = article['url']
                    title = article['title']
                    date = article.get('publishedAt', '')[:10]
                    summary += f"<li><a href='{url}' target='_blank'>{title}</a> ({date})</li>\n"
                summary += "</ul>\n"
        for journalist in self.followed_journalists:
            # Note: NewsAPI doesn't filter by author easily, so this is simplified
            articles = self.search_tech_news(journalist, 3)
            if articles:
                summary += f"<h3>Journaliste : {journalist}</h3>\n<ul>\n"
                for article in articles:
                    url = article['url']
                    title = article['title']
                    date = article.get('publishedAt', '')[:10]
                    summary += f"<li><a href='{url}' target='_blank'>{title}</a> ({date})</li>\n"
                summary += "</ul>\n"
        return summary

    def generate_response(self, user_input: str) -> str:
        # Use Serper API to get search results
        results = self.search_serper(user_input)
        if not results:
            return "Désolé, je n'ai pas trouvé de résultats pertinents pour votre requête."

        # Limit to top 5 results
        top_results = results[:5]

        # Format response as bullet points with links
        response_html = "<h3>Résultats de recherche pour votre requête :</h3><ul>"
        for result in top_results:
            title = result.get('title', 'Titre non disponible')
            link = result.get('link', '')
            snippet = result.get('snippet', 'Description non disponible')

            if link:
                response_html += f"<li><strong><a href='{link}' target='_blank'>{title}</a></strong><br>{snippet}</li>"
            else:
                response_html += f"<li><strong>{title}</strong><br>{snippet}</li>"

        response_html += "</ul>"

        return response_html


# Exemple d’utilisation
if __name__ == "__main__":
    agent = TechJournalistAgent(api_key='5e7e6f52591e44ba982e69377cf5b8e0')
    print(agent.generate_response("info"))
