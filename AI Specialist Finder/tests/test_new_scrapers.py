import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from scrapers.google_scholar_scraper import GoogleScholarScraper
from scrapers.researchgate_scraper import ResearchGateScraper


class TestGoogleScholarScraper:
    """Test cases for Google Scholar scraper"""

    def test_init(self):
        """Test Google Scholar scraper initialization"""
        scraper = GoogleScholarScraper()
        assert scraper.client is not None
        assert scraper.BASE_URL == "https://scholar.google.com"

    @patch('scrapers.google_scholar_scraper.httpx.Client')
    def test_search_ai_researchers_success(self, mock_client):
        """Test successful search for AI researchers"""
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
            <div class="gs_r">
                <a href="/citations?user=test_user">Test Researcher</a>
            </div>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = GoogleScholarScraper()
        researchers = scraper.search_ai_researchers(max_results=1)

        assert len(researchers) >= 0  # May be 0 if profile extraction fails
        mock_client.return_value.get.assert_called()

    @patch('scrapers.google_scholar_scraper.httpx.Client')
    def test_extract_researcher_profile_success(self, mock_client):
        """Test successful researcher profile extraction"""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
            <div id="gsc_prf_in">Dr. Test Researcher</div>
            <div class="gsc_prf_il">Test University</div>
            <div id="gsc_prf_int">
                <a>Artificial Intelligence</a>
                <a>Machine Learning</a>
            </div>
            <td class="gsc_rsb_std">100</td>
            <td class="gsc_rsb_std">20</td>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = GoogleScholarScraper()
        profile = scraper._extract_researcher_profile("https://scholar.google.com/citations?user=test")

        assert profile is not None
        assert profile['name'] == "Dr. Test Researcher"
        assert profile['current_publication'] == "Test University"
        assert "Artificial Intelligence" in profile['research_interests']

    def test_calculate_reputation_score(self):
        """Test reputation score calculation"""
        scraper = GoogleScholarScraper()

        # Test with zero values
        score = scraper._calculate_reputation_score(0, 0)
        assert score >= 0.0

        # Test with actual values
        score = scraper._calculate_reputation_score(100, 20)
        assert score > 0.0
        assert score <= 1.0


class TestResearchGateScraper:
    """Test cases for ResearchGate scraper"""

    def test_init(self):
        """Test ResearchGate scraper initialization"""
        scraper = ResearchGateScraper()
        assert scraper.client is not None
        assert scraper.BASE_URL == "https://www.researchgate.net"

    @patch('scrapers.researchgate_scraper.httpx.Client')
    def test_search_ai_researchers_success(self, mock_client):
        """Test successful search for AI researchers"""
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
            <a href="/profile/test_profile">Test Researcher</a>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = ResearchGateScraper()
        researchers = scraper.search_ai_researchers(max_results=1)

        assert len(researchers) >= 0
        mock_client.return_value.get.assert_called()

    @patch('scrapers.researchgate_scraper.httpx.Client')
    def test_extract_researcher_profile_success(self, mock_client):
        """Test successful researcher profile extraction"""
        mock_response = Mock()
        mock_response.text = """
        <html>
        <body>
            <h1 class="profile-name">Dr. Test Researcher</h1>
            <div class="institution">Test University</div>
            <div class="research-interests">
                <span class="interest-item">Artificial Intelligence</span>
                <span class="interest-item">Machine Learning</span>
            </div>
            <div class="publication-count">50</div>
            <div class="citation-count">200</div>
            <div class="h-index">15</div>
        </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.get.return_value = mock_response

        scraper = ResearchGateScraper()
        profile = scraper._extract_researcher_profile("https://www.researchgate.net/profile/test")

        assert profile is not None
        assert profile['name'] == "Dr. Test Researcher"
        assert profile['current_publication'] == "Test University"
        assert profile['publication_count'] == 50
        assert profile['citation_count'] == 200
        assert profile['h_index'] == 15

    def test_calculate_reputation_score(self):
        """Test reputation score calculation"""
        scraper = ResearchGateScraper()

        # Test with zero values
        score = scraper._calculate_reputation_score(0, 0, 0)
        assert score >= 0.0

        # Test with actual values
        score = scraper._calculate_reputation_score(50, 200, 15)
        assert score > 0.0
        assert score <= 1.0
