import httpx
from loguru import logger
from typing import List, Dict, Any

class NewsAPIScraper:
    """Scraper for NewsAPI.org to fetch journalist and article data"""

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=10.0)

    def search_articles(self, query: str, page_size: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Search articles matching the query"""
        params = {
            "q": query,
            "pageSize": page_size,
            "page": page,
            "apiKey": self.api_key,
            "language": "en",
            "sortBy": "relevancy"
        }
        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            logger.info(f"Fetched {len(articles)} articles for query '{query}'")
            return articles
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching articles: {e}")
            return []

    def extract_journalists(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract journalist info from articles"""
        journalists = []
        seen_authors = set()
        for article in articles:
            author = article.get("author")
            if author and author not in seen_authors:
                journalist_data = {
                    "name": author,
                    "current_publication": article.get("source", {}).get("name"),
                    "bio": None,
                    "email": None,
                    "twitter_handle": None,
                    "linkedin_url": None,
                    "country": None,
                    "city": None,
                    "reputation_score": None,
                    "ai_relevance_score": None,
                    "specializations": [],
                    "source_platform": "newsapi",
                }
                journalists.append(journalist_data)
                seen_authors.add(author)
        logger.info(f"Extracted {len(journalists)} unique journalists from articles")
        return journalists
