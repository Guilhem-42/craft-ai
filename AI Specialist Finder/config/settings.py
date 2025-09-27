"""
Configuration settings for the Journalist Finder AI Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = "sqlite:///data/journalists.db"

# API Keys (to be set in .env file)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# LinkedIn API Configuration (OAuth 2.0)
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")

# Legacy LinkedIn credentials (for scraping - use with caution)
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# NewsAPI Configuration
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Clearbit Configuration
CLEARBIT_KEY = os.getenv("CLEARBIT_KEY")

# Scraping Configuration
SCRAPING_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Search Keywords for AI/Programming Journalists
AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural networks",
    "AI ethics",
    "automation",
    "robotics",
    "data science",
    "programming",
    "software development",
    "tech innovation",
    "digital transformation"
]

# Target News Sources
NEWS_SOURCES = [
    "techcrunch.com",
    "wired.com",
    "arstechnica.com",
    "theverge.com",
    "venturebeat.com",
    "zdnet.com",
    "engadget.com",
    "mashable.com",
    "recode.net",
    "axios.com",
    "epsiloon.com",
    # France
    "actuia.com",
    "ialsmagazine.com",
    "larevueia.fr",
    # Belgique
    "mesmedias.be",
    "rtbf.be",
    "trends.levif.be",
    # Suisse
    "ictjournal.ch",
    "technology-innovators.com"
]

# Reputation Scoring Weights
REPUTATION_WEIGHTS = {
    "article_count": 0.3,
    "social_followers": 0.2,
    "engagement_rate": 0.2,
    "publication_quality": 0.2,
    "expertise_relevance": 0.1
}

# Geographic Regions of Interest
TARGET_REGIONS = [
    "United States",
    "United Kingdom",
    "Canada",
    "France",
    "Germany",
    "Japan",
    "South Korea",
    "Singapore",
    "Australia",
    "Netherlands"
]

# Quality Thresholds for Filtering
DEFAULT_MIN_REPUTATION = 0.15  # Lowered from 0.5 to capture more journalists
DEFAULT_MIN_AI_RELEVANCE = 0.02  # Lowered from 0.5 to capture more journalists

# Alternative threshold sets for different use cases
QUALITY_THRESHOLDS = {
    'strict': {
        'min_reputation': 0.5,
        'min_ai_relevance': 0.5
    },
    'moderate': {
        'min_reputation': 0.25,
        'min_ai_relevance': 0.15
    },
    'inclusive': {
        'min_reputation': 0.15,
        'min_ai_relevance': 0.02
    },
    'all': {
        'min_reputation': 0.0,
        'min_ai_relevance': 0.0
    }
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/journalist_finder.log"
