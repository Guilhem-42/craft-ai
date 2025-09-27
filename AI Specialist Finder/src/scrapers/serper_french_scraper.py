"""
Serper.dev scraper for finding French AI/Programming journalists
"""
import json
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import re

from src.serper_api_client import SerperAPIClient

class SerperFrenchScraper:
    """Scraper using Serper.dev API to find French journalists"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = SerperAPIClient(api_key)
        self.french_sites = [
            "actuia.com",
            "ialsmagazine.com",
            "larevueia.fr",
            "mesmedias.be",
            "rtbf.be",
            "trends.levif.be",
            "ictjournal.ch",
            "technology-innovators.com"
        ]

    def search_french_journalists(self) -> List[Dict[str, Any]]:
        """Search for French AI journalists using Serper API"""
        all_journalists = []

        # Search queries for French journalists
        search_queries = [
            "journaliste IA France",
            "journaliste intelligence artificielle France",
            "journaliste tech France",
            "rédacteur IA France",
            "spécialiste IA France",
            "journaliste IA Belgique",
            "journaliste tech Suisse",
            "journaliste IA francophone"
        ]

        for query in search_queries:
            logger.info(f"Searching with query: {query}")
            try:
                result = self.client.search(query)
                journalists = self._extract_journalists_from_serper_result(result, query)
                all_journalists.extend(journalists)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error searching with query '{query}': {e}")
                continue

        # Also search specific French sites
        for site in self.french_sites:
            try:
                query = f"site:{site} journaliste IA"
                logger.info(f"Searching site-specific: {query}")
                result = self.client.search(query)
                journalists = self._extract_journalists_from_serper_result(result, query)
                all_journalists.extend(journalists)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error searching site {site}: {e}")
                continue

        return self._deduplicate_journalists(all_journalists)

    def _extract_journalists_from_serper_result(self, result: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Extract journalist information from Serper API result"""
        journalists = []

        if 'organic' not in result:
            return journalists

        for item in result['organic']:
            try:
                title = item.get('title', '')
                link = item.get('link', '')
                snippet = item.get('snippet', '')

                # Check if this result is about a journalist
                if self._is_journalist_result(title, snippet, link):
                    journalist_data = self._parse_journalist_info(title, snippet, link, query)
                    if journalist_data:
                        journalists.append(journalist_data)

            except Exception as e:
                logger.warning(f"Error processing Serper result: {e}")
                continue

        return journalists

    def _is_journalist_result(self, title: str, snippet: str, link: str) -> bool:
        """Check if search result is about a journalist"""
        text_to_check = (title + " " + snippet).lower()

        journalist_keywords = [
            'journaliste', 'rédacteur', 'reporter', 'correspondant',
            'spécialiste', 'expert', 'auteur', 'écrivain',
            'journalist', 'writer', 'reporter', 'specialist'
        ]

        ai_keywords = [
            'ia', 'intelligence artificielle', 'ai', 'artificial intelligence',
            'machine learning', 'deep learning', 'tech', 'technologie'
        ]

        has_journalist = any(keyword in text_to_check for keyword in journalist_keywords)
        has_ai = any(keyword in text_to_check for keyword in ai_keywords)

        return has_journalist and has_ai

    def _parse_journalist_info(self, title: str, snippet: str, link: str, query: str) -> Optional[Dict[str, Any]]:
        """Parse journalist information from search result"""
        try:
            # Extract name from title or snippet
            name = self._extract_name(title + " " + snippet)

            if not name:
                return None

            # Determine country from query or link
            country = self._determine_country(query, link)

            # Extract publication from link
            publication = self._extract_publication(link)

            # Create journalist data
            journalist_data = {
                'name': name,
                'bio': snippet,
                'current_publication': publication,
                'country': country,
                'source_platform': 'serper_search',
                'specializations': ['intelligence artificielle', 'technologie'],
                'ai_relevance_score': 0.9,  # High relevance from targeted search
                'website_url': link  # Use website_url field instead of source_url
            }

            return journalist_data

        except Exception as e:
            logger.warning(f"Error parsing journalist info: {e}")
            return None

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract journalist name from text"""
        # Look for patterns like "Name - Title" or "Name, Title"
        patterns = [
            r'^([^,-]+?)(?:\s*[-,]\s*.+)?$',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Proper names
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                name = match.strip()
                if len(name.split()) >= 2 and len(name) < 50:  # Reasonable name length
                    return name

        return None

    def _determine_country(self, query: str, link: str) -> str:
        """Determine country from query or link"""
        query_lower = query.lower()
        link_lower = link.lower()

        if 'france' in query_lower or 'france' in link_lower:
            return 'France'
        elif 'belgique' in query_lower or 'belgique' in link_lower or 'be' in link_lower:
            return 'Belgique'
        elif 'suisse' in query_lower or 'suisse' in link_lower or 'ch' in link_lower:
            return 'Suisse'
        elif 'francophone' in query_lower:
            return 'Francophone'
        else:
            return 'France'  # Default to France for French queries

    def _extract_publication(self, link: str) -> str:
        """Extract publication name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(link).netloc.replace('www.', '')

            # Map known domains to publication names
            domain_map = {
                'actuia.com': 'ActuIA',
                'ialsmagazine.com': 'IALS Magazine',
                'larevueia.fr': 'La Revue IA',
                'mesmedias.be': 'Mes Médias',
                'rtbf.be': 'RTBF',
                'trends.levif.be': 'Trends-Tendances',
                'ictjournal.ch': 'ICTjournal',
                'technology-innovators.com': 'Technology Innovators'
            }

            return domain_map.get(domain, domain)
        except Exception:
            return 'Unknown'

    def _deduplicate_journalists(self, journalists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate journalists based on name"""
        seen_names = set()
        unique_journalists = []

        for journalist in journalists:
            name = journalist.get('name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_journalists.append(journalist)

        return unique_journalists
