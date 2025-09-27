import requests
import psycopg2
from psycopg2.extras import execute_values
import os
import logging

# Configuration - replace with your actual credentials or use environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key_here')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'newsdb')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'
QUERY = 'informatique OR technologie OR informatique'  # Search query for tech news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_news():
    params = {
        'q': QUERY,
        'apiKey': NEWS_API_KEY,
        'language': 'fr',
        'sortBy': 'publishedAt',
        'pageSize': 100,
    }
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    response.raise_for_status()
    data = response.json()
    articles = data.get('articles', [])
    logger.info(f"Fetched {len(articles)} articles from NewsAPI")
    return articles

def connect_db():
    conn = psycopg2.connect(
        host=POSTGRES_blackbox,
        port=POSTGRES_PORT,
        dbname=blackboxsenor,
        user=senor,
        password=mysecretpassword
    )
    return conn

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title TEXT,
                description TEXT,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                source_name TEXT
            );
        """)
        conn.commit()
    logger.info("Ensured articles table exists")

def save_articles(conn, articles):
    with conn.cursor() as cur:
        records = []
        for article in articles:
            records.append((
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('publishedAt'),
                article.get('source', {}).get('name')
            ))
        sql = """
            INSERT INTO articles (title, description, url, published_at, source_name)
            VALUES %s
            ON CONFLICT (url) DO NOTHING;
        """
        execute_values(cur, sql, records)
        conn.commit()
    logger.info(f"Saved {len(records)} articles to database")

def main():
    try:
        articles = fetch_news()
        conn = connect_db()
        create_table(conn)
        save_articles(conn, articles)
        conn.close()
        logger.info("News fetching and saving completed successfully")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

if __name__ == '__main__':
    main()
