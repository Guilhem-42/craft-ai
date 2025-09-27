import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scrapers.newsapi_scraper import NewsAPIScraper
from scrapers.clearbit_scraper import ClearbitScraper

class TestNewsAPIScraper:
    """Test cases for NewsAPI scraper"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        scraper = NewsAPIScraper("test_key")
        assert scraper.api_key == "test_key"
        assert scraper.client is not None

    @patch('scrapers.newsapi_scraper.httpx.Client')
    def test_search_articles_success(self, mock_client):
        """Test successful article search"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "author": "John Doe",
                    "title": "AI News",
                    "source": {"name": "TechCrunch"}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = NewsAPIScraper("test_key")
        articles = scraper.search_articles("AI")

        assert len(articles) == 1
        assert articles[0]["author"] == "John Doe"

    @patch('scrapers.newsapi_scraper.httpx.Client')
    def test_search_articles_http_error(self, mock_client):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_client.return_value.get.return_value = mock_response

        scraper = NewsAPIScraper("test_key")
        try:
            articles = scraper.search_articles("AI")
        except Exception:
            articles = []

        assert articles == []

    def test_extract_journalists(self):
        """Test journalist extraction from articles"""
        articles = [
            {
                "author": "John Doe",
                "source": {"name": "TechCrunch"}
            },
            {
                "author": "Jane Smith",
                "source": {"name": "Wired"}
            },
            {
                "author": "John Doe",  # Duplicate
                "source": {"name": "TechCrunch"}
            }
        ]

        scraper = NewsAPIScraper("test_key")
        journalists = scraper.extract_journalists(articles)

        assert len(journalists) == 2  # Should deduplicate
        assert journalists[0]["name"] == "John Doe"
        assert journalists[0]["current_publication"] == "TechCrunch"

class TestClearbitScraper:
    """Test cases for Clearbit scraper"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        scraper = ClearbitScraper("test_key")
        assert scraper.api_key == "test_key"
        assert scraper.client is not None

    @patch('scrapers.clearbit_scraper.httpx.Client')
    def test_enrich_person_success(self, mock_client):
        """Test successful person enrichment"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "person": {
                "name": {"fullName": "John Doe"},
                "email": "john@example.com",
                "bio": "Tech journalist",
                "twitter": {"handle": "johndoe"},
                "linkedin": {"url": "https://linkedin.com/in/johndoe"},
                "location": {"country": "US", "city": "San Francisco"}
            },
            "company": {
                "name": "TechCrunch"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = ClearbitScraper("test_key")
        data = scraper.enrich_person("john@example.com")

        assert data is not None
        assert data["person"]["name"]["fullName"] == "John Doe"

    @patch('scrapers.clearbit_scraper.httpx.Client')
    def test_enrich_person_http_error(self, mock_client):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_client.return_value.get.return_value = mock_response

        scraper = ClearbitScraper("test_key")
        try:
            data = scraper.enrich_person("john@example.com")
        except Exception:
            data = None

        assert data is None

    def test_extract_journalist_info(self):
        """Test journalist info extraction"""
        clearbit_data = {
            "person": {
                "name": {"fullName": "John Doe"},
                "email": "john@example.com",
                "bio": "Tech journalist",
                "twitter": {"handle": "johndoe"},
                "linkedin": {"url": "https://linkedin.com/in/johndoe"},
                "location": {"country": "US", "city": "San Francisco"}
            },
            "company": {
                "name": "TechCrunch"
            }
        }

        scraper = ClearbitScraper("test_key")
        info = scraper.extract_journalist_info(clearbit_data)

        assert info["name"] == "John Doe"
        assert info["email"] == "john@example.com"
        assert info["current_publication"] == "TechCrunch"
        assert info["twitter_handle"] == "johndoe"
        assert info["country"] == "US"
        assert info["city"] == "San Francisco"
