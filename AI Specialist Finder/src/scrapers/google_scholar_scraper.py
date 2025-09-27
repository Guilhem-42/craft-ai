"""
Google Scholar scraper for finding AI/Programming researchers and academics
"""
import httpx
import time
from typing import List, Dict, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
import re
import urllib.parse

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import SCRAPING_DELAY

class GoogleScholarScraper:
    """Scraper for finding researchers and academics on Google Scholar who work in AI/Programming"""

    BASE_URL = "https://scholar.google.com"

    def __init__(self):
        """Initialize Google Scholar scraper"""
        self.client = httpx.Client(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

    def search_ai_researchers(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for AI researchers on Google Scholar"""
        researchers = []

        # AI-related search queries
        search_queries = [
            "artificial intelligence researcher",
            "machine learning researcher",
            "computer vision researcher",
            "natural language processing researcher",
            "deep learning researcher",
            "AI ethics researcher",
            "robotics researcher",
            "data science researcher"
        ]

        for query in search_queries:
            try:
                logger.info(f"Searching Google Scholar for: {query}")
                query_researchers = self._search_query(query, max_results // len(search_queries))
                researchers.extend(query_researchers)
                time.sleep(SCRAPING_DELAY * 2)  # Longer delay for Google Scholar

            except Exception as e:
                logger.error(f"Error searching Google Scholar for '{query}': {e}")
                continue

        return self._deduplicate_researchers(researchers)

    def _search_query(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Google Scholar for a specific query"""
        researchers = []

        try:
            # Encode query for URL
            encoded_query = urllib.parse.quote(query)

            # Search URL
            search_url = f"{self.BASE_URL}/scholar?q={encoded_query}&hl=en&as_sdt=0&as_vis=1&oi=scholart"

            response = self.client.get(search_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find researcher profiles
            profile_links = soup.find_all('a', href=re.compile(r'/citations\?user='))

            for link in profile_links[:max_results]:
                profile_url = link.get('href')
                if profile_url:
                    full_profile_url = f"{self.BASE_URL}{profile_url}"
                    researcher_data = self._extract_researcher_profile(full_profile_url)
                    if researcher_data:
                        researchers.append(researcher_data)

                time.sleep(SCRAPING_DELAY)

        except Exception as e:
            logger.error(f"Error in Google Scholar search: {e}")

        return researchers

    def _extract_researcher_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """Extract researcher information from Google Scholar profile"""
        try:
            response = self.client.get(profile_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract basic information
            name_elem = soup.find('div', {'id': 'gsc_prf_in'})
            name = name_elem.text.strip() if name_elem else "Unknown"

            # Extract affiliation
            affiliation_elem = soup.find('div', {'class': 'gsc_prf_il'})
            affiliation = affiliation_elem.text.strip() if affiliation_elem else ""

            # Extract research interests
            interests_elem = soup.find('div', {'id': 'gsc_prf_int'})
            interests = []
            if interests_elem:
                interest_links = interests_elem.find_all('a')
                interests = [link.text.strip() for link in interest_links]

            # Extract citation metrics
            citation_elem = soup.find('td', {'class': 'gsc_rsb_std'})
            citation_count = 0
            if citation_elem:
                try:
                    citation_count = int(citation_elem.text.strip())
                except ValueError:
                    citation_count = 0

            # Extract h-index
            h_index_elem = soup.find_all('td', {'class': 'gsc_rsb_std'})
            h_index = 0
            if len(h_index_elem) >= 2:
                try:
                    h_index = int(h_index_elem[1].text.strip())
                except (ValueError, IndexError):
                    h_index = 0

            # Extract bio/research summary
            bio = self._extract_bio_from_interests(interests)

            # Extract email if available (rare in Google Scholar)
            email = None

            # Extract website if available
            website_elem = soup.find('div', {'id': 'gsc_prf_ivh'})
            website = None
            if website_elem:
                website_link = website_elem.find('a')
                if website_link:
                    website = website_link.get('href')

            # Determine specializations
            specializations = self._extract_specializations(interests)

            # Calculate reputation score based on citations and h-index
            reputation_score = self._calculate_reputation_score(citation_count, h_index)

            # Calculate AI relevance score
            ai_relevance_score = self._calculate_ai_relevance(interests, name)

            researcher_data = {
                'name': name,
                'bio': bio,
                'email': email,
                'current_publication': affiliation,
                'website_url': website,
                'country': self._extract_country_from_affiliation(affiliation),
                'city': self._extract_city_from_affiliation(affiliation),
                'reputation_score': reputation_score,
                'ai_relevance_score': ai_relevance_score,
                'specializations': specializations,
                'source_platform': 'google_scholar',
                'citation_count': citation_count,
                'h_index': h_index,
                'programming_expertise': self._has_programming_expertise(interests)
            }

            return researcher_data

        except Exception as e:
            logger.error(f"Error extracting researcher profile from {profile_url}: {e}")
            return None

    def _extract_bio_from_interests(self, interests: List[str]) -> str:
        """Create a bio-like description from research interests"""
        if not interests:
            return "AI/ML Researcher"

        bio_parts = ["Researcher specializing in"]
        bio_parts.extend(interests[:3])  # Limit to first 3 interests

        return " ".join(bio_parts)

    def _extract_specializations(self, interests: List[str]) -> List[str]:
        """Extract specializations from research interests"""
        specializations = []
        interests_text = " ".join(interests).lower()

        specialization_map = {
            'artificial intelligence': ['artificial intelligence', 'ai', 'machine learning', 'ml'],
            'computer vision': ['computer vision', 'image processing', 'cv'],
            'natural language processing': ['natural language processing', 'nlp', 'text mining'],
            'deep learning': ['deep learning', 'neural networks', 'cnn', 'rnn'],
            'robotics': ['robotics', 'robot', 'automation'],
            'data science': ['data science', 'big data', 'data mining'],
            'cybersecurity': ['cybersecurity', 'security', 'privacy'],
            'programming': ['programming', 'software engineering', 'algorithms'],
            'blockchain': ['blockchain', 'cryptocurrency', 'distributed systems']
        }

        for specialization, keywords in specialization_map.items():
            if any(keyword in interests_text for keyword in keywords):
                specializations.append(specialization)

        return specializations if specializations else ['artificial intelligence']

    def _calculate_reputation_score(self, citation_count: int, h_index: int) -> float:
        """Calculate reputation score based on academic metrics"""
        import math

        # Citation score (logarithmic scale)
        citation_score = min(math.log10(max(citation_count, 1)) / 4.0, 1.0)

        # H-index score (normalized)
        h_index_score = min(h_index / 50.0, 1.0)

        # Combine scores
        reputation_score = (citation_score * 0.6 + h_index_score * 0.4)

        return min(reputation_score, 1.0)

    def _calculate_ai_relevance(self, interests: List[str], name: str) -> float:
        """Calculate AI relevance score"""
        text = " ".join(interests).lower() + " " + name.lower()

        ai_keywords = {
            'artificial intelligence': 1.0,
            'machine learning': 1.0,
            'deep learning': 0.9,
            'neural networks': 0.9,
            'computer vision': 0.8,
            'natural language processing': 0.8,
            'robotics': 0.7,
            'data science': 0.6,
            'algorithms': 0.5,
            'programming': 0.4
        }

        relevance_score = 0.0
        for keyword, weight in ai_keywords.items():
            if keyword in text:
                relevance_score += weight

        return min(relevance_score / 2.0, 1.0)

    def _has_programming_expertise(self, interests: List[str]) -> bool:
        """Check if researcher has programming expertise"""
        interests_text = " ".join(interests).lower()

        programming_keywords = [
            'programming', 'algorithms', 'software', 'computer science',
            'python', 'java', 'c++', 'machine learning', 'data structures'
        ]

        return any(keyword in interests_text for keyword in programming_keywords)

    def _extract_country_from_affiliation(self, affiliation: str) -> Optional[str]:
        """Extract country from affiliation string"""
        if not affiliation:
            return None

        affiliation_lower = affiliation.lower()

        country_keywords = {
            'USA': ['usa', 'united states', 'america', 'california', 'new york', 'stanford', 'mit', 'harvard'],
            'UK': ['uk', 'united kingdom', 'britain', 'england', 'london', 'oxford', 'cambridge'],
            'Canada': ['canada', 'toronto', 'university of toronto', 'mcgill'],
            'France': ['france', 'paris', 'sorbonne', 'inria'],
            'Germany': ['germany', 'berlin', 'munich', 'max planck'],
            'Japan': ['japan', 'tokyo', 'kyoto university'],
            'Australia': ['australia', 'sydney', 'university of melbourne'],
            'China': ['china', 'beijing', 'tsinghua', 'peking'],
            'India': ['india', 'iit', 'indian institute']
        }

        for country, keywords in country_keywords.items():
            if any(keyword in affiliation_lower for keyword in keywords):
                return country

        return None

    def _extract_city_from_affiliation(self, affiliation: str) -> Optional[str]:
        """Extract city from affiliation string"""
        if not affiliation:
            return None

        # Common city patterns in academic affiliations
        city_patterns = [
            r',\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*[A-Z]{2}',
            r',\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$'
        ]

        for pattern in city_patterns:
            match = re.search(pattern, affiliation)
            if match:
                return match.group(1)

        return None

    def _deduplicate_researchers(self, researchers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate researchers based on name"""
        seen_names = set()
        unique_researchers = []

        for researcher in researchers:
            name = researcher.get('name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_researchers.append(researcher)

        return unique_researchers

    def get_researcher_details(self, scholar_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific researcher by Scholar ID"""
        profile_url = f"{self.BASE_URL}/citations?user={scholar_id}&hl=en"
        return self._extract_researcher_profile(profile_url)
