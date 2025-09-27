"""
LinkedIn scraper for finding AI/Programming journalists
"""
import time
import re
from typing import List, Dict, Any, Optional
from loguru import logger
import requests
from bs4 import BeautifulSoup

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import AI_KEYWORDS, SCRAPING_DELAY, LINKEDIN_USERNAME, LINKEDIN_PASSWORD

class LinkedInScraper:
    """Scraper for finding journalists on LinkedIn who cover AI/Programming topics"""
    
    def __init__(self):
        """Initialize LinkedIn scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logged_in = False
        
        # Note: LinkedIn scraping requires careful handling due to their terms of service
        # This implementation provides a framework but should be used responsibly
        logger.warning("LinkedIn scraping should be used carefully and in compliance with LinkedIn's terms of service")
    
    def search_ai_journalists(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for AI/Programming journalists on LinkedIn"""
        journalists = []
        
        if not self._login():
            logger.error("Could not log in to LinkedIn. Skipping LinkedIn scraping.")
            return journalists
        
        # Search queries for finding AI journalists
        search_queries = [
            "AI journalist",
            "artificial intelligence reporter",
            "technology writer AI",
            "machine learning journalist",
            "programming correspondent",
            "tech reporter artificial intelligence"
        ]
        
        for query in search_queries:
            try:
                logger.info(f"Searching LinkedIn for: {query}")
                results = self._search_people(query, max_results // len(search_queries))
                
                for profile_data in results:
                    if self._is_relevant_journalist(profile_data):
                        journalists.append(profile_data)
                
                time.sleep(SCRAPING_DELAY * 2)  # Longer delay for LinkedIn
                
            except Exception as e:
                logger.error(f"Error searching LinkedIn with query '{query}': {e}")
                continue
        
        return self._deduplicate_journalists(journalists)
    
    def _login(self) -> bool:
        """Login to LinkedIn (placeholder - requires proper implementation)"""
        # Note: This is a placeholder. Actual LinkedIn login requires handling
        # CSRF tokens, captchas, and other security measures.
        # Consider using official LinkedIn API or tools like linkedin-api library
        
        if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
            logger.warning("LinkedIn credentials not provided. Using public search only.")
            return False
        
        try:
            # This is a simplified example - real implementation would be more complex
            login_url = "https://www.linkedin.com/login"
            response = self.session.get(login_url)
            
            if response.status_code == 200:
                # In a real implementation, you would:
                # 1. Parse the login form
                # 2. Extract CSRF tokens
                # 3. Submit credentials
                # 4. Handle 2FA if required
                # 5. Verify successful login
                
                logger.info("LinkedIn login simulation (not actually implemented)")
                self.logged_in = False  # Set to False since this is just a placeholder
                return False
            
        except Exception as e:
            logger.error(f"LinkedIn login error: {e}")
            return False
        
        return False
    
    def _search_people(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search for people on LinkedIn"""
        profiles = []
        
        try:
            # LinkedIn search URL (public search)
            search_url = f"https://www.linkedin.com/pub/dir/?first=&last=&search=Search&keyword={query.replace(' ', '+')}"
            
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                profiles = self._parse_search_results(response.text)
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
        
        return profiles[:max_results]
    
    def _parse_search_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse LinkedIn search results"""
        profiles = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Note: LinkedIn's HTML structure changes frequently
        # This is a simplified example of what profile parsing might look like
        
        profile_elements = soup.select('.search-result__info, .profile-card, [data-control-name="search_srp_result"]')
        
        for element in profile_elements:
            try:
                profile_data = self._extract_profile_data(element)
                if profile_data:
                    profiles.append(profile_data)
            except Exception as e:
                logger.warning(f"Error parsing profile element: {e}")
                continue
        
        return profiles
    
    def _extract_profile_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract profile data from HTML element"""
        try:
            # Extract name
            name_selectors = ['.name', '.actor-name', '.search-result__result-text h3', 'h3']
            name = None
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            if not name:
                return None
            
            # Extract headline/title
            headline_selectors = ['.headline', '.subline', '.search-result__result-text p', 'p']
            headline = ""
            for selector in headline_selectors:
                headline_elem = element.select_one(selector)
                if headline_elem:
                    headline = headline_elem.get_text().strip()
                    break
            
            # Extract location
            location_selectors = ['.location', '.subline-secondary', '.search-result__result-text .subline']
            location = ""
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    location = location_elem.get_text().strip()
                    break
            
            # Extract LinkedIn URL
            linkedin_url = None
            link_elem = element.select_one('a[href*="/in/"]')
            if link_elem:
                linkedin_url = link_elem.get('href')
                if linkedin_url and not linkedin_url.startswith('http'):
                    linkedin_url = f"https://www.linkedin.com{linkedin_url}"
            
            # Extract current company/publication
            company_selectors = ['.company', '.org', '.search-result__result-text .subline']
            current_publication = ""
            for selector in company_selectors:
                company_elem = element.select_one(selector)
                if company_elem:
                    current_publication = company_elem.get_text().strip()
                    break
            
            # Determine specializations from headline
            specializations = self._extract_specializations(headline)
            
            # Calculate AI relevance
            ai_relevance = self._calculate_ai_relevance(headline + " " + name)
            
            profile_data = {
                'name': name,
                'bio': headline,
                'job_title': headline,
                'current_publication': current_publication,
                'linkedin_url': linkedin_url,
                'country': self._extract_country_from_location(location),
                'city': self._extract_city_from_location(location),
                'specializations': specializations,
                'ai_relevance_score': ai_relevance,
                'programming_expertise': self._has_programming_expertise(headline),
                'source_platform': 'linkedin',
                'reputation_score': 0.6  # Default score for LinkedIn profiles
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error extracting profile data: {e}")
            return None
    
    def _is_relevant_journalist(self, profile_data: Dict[str, Any]) -> bool:
        """Check if profile is relevant for AI/Programming journalism"""
        headline = profile_data.get('bio', '').lower()
        job_title = profile_data.get('job_title', '').lower()
        
        # Check for journalist keywords
        journalist_keywords = [
            'journalist', 'reporter', 'writer', 'correspondent', 
            'editor', 'columnist', 'freelance', 'news', 'media'
        ]
        
        is_journalist = any(keyword in headline or keyword in job_title for keyword in journalist_keywords)
        
        # Check AI relevance
        ai_relevance = profile_data.get('ai_relevance_score', 0)
        programming_expertise = profile_data.get('programming_expertise', False)
        
        return is_journalist and (ai_relevance >= 0.3 or programming_expertise)
    
    def _extract_specializations(self, text: str) -> List[str]:
        """Extract specializations from headline/bio"""
        specializations = []
        text_lower = text.lower()
        
        specialization_keywords = {
            'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning'],
            'programming': ['programming', 'coding', 'software', 'developer'],
            'data science': ['data science', 'data analysis', 'analytics'],
            'cybersecurity': ['cybersecurity', 'security', 'privacy'],
            'blockchain': ['blockchain', 'cryptocurrency', 'crypto'],
            'robotics': ['robotics', 'automation', 'robots'],
            'cloud computing': ['cloud', 'aws', 'azure'],
            'technology': ['tech', 'technology', 'innovation']
        }
        
        for specialization, keywords in specialization_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                specializations.append(specialization)
        
        return specializations if specializations else ['technology']
    
    def _calculate_ai_relevance(self, text: str) -> float:
        """Calculate AI relevance score"""
        text_lower = text.lower()
        
        ai_keywords_weighted = {
            'artificial intelligence': 1.0,
            'machine learning': 1.0,
            'deep learning': 0.9,
            'ai': 0.8,
            'automation': 0.6,
            'robotics': 0.6,
            'data science': 0.5,
            'programming': 0.4,
            'technology': 0.3
        }
        
        relevance_score = 0.0
        for keyword, weight in ai_keywords_weighted.items():
            if keyword in text_lower:
                relevance_score += weight
        
        return min(relevance_score / 2.0, 1.0)
    
    def _has_programming_expertise(self, text: str) -> bool:
        """Check if text indicates programming expertise"""
        programming_keywords = [
            'programmer', 'developer', 'software engineer', 'coding',
            'python', 'javascript', 'programming', 'software development'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in programming_keywords)
    
    def _extract_country_from_location(self, location: str) -> Optional[str]:
        """Extract country from location string"""
        if not location:
            return None
        
        country_keywords = {
            'United States': ['usa', 'united states', 'america', 'us', 'new york', 'california', 'texas'],
            'United Kingdom': ['uk', 'united kingdom', 'britain', 'england', 'london'],
            'Canada': ['canada', 'toronto', 'vancouver', 'montreal'],
            'France': ['france', 'paris', 'lyon'],
            'Germany': ['germany', 'berlin', 'munich'],
            'Japan': ['japan', 'tokyo', 'osaka'],
            'Australia': ['australia', 'sydney', 'melbourne']
        }
        
        location_lower = location.lower()
        for country, keywords in country_keywords.items():
            if any(keyword in location_lower for keyword in keywords):
                return country
        
        return None
    
    def _extract_city_from_location(self, location: str) -> Optional[str]:
        """Extract city from location string"""
        if not location:
            return None
        
        # Common city extraction patterns
        parts = location.split(',')
        if parts:
            return parts[0].strip()
        
        return location.strip()
    
    def _deduplicate_journalists(self, journalists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate journalists based on name and LinkedIn URL"""
        seen = set()
        unique_journalists = []
        
        for journalist in journalists:
            # Create unique identifier
            identifier = (
                journalist.get('name', '').lower().strip(),
                journalist.get('linkedin_url', '')
            )
            
            if identifier not in seen and identifier[0]:  # Ensure name exists
                seen.add(identifier)
                unique_journalists.append(journalist)
        
        return unique_journalists
    
    def get_profile_details(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information from a LinkedIn profile URL"""
        try:
            response = self.session.get(linkedin_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract detailed profile information
                # Note: This would require parsing the full LinkedIn profile page
                # which has complex structure and anti-scraping measures
                
                profile_data = {
                    'linkedin_url': linkedin_url,
                    'source_platform': 'linkedin'
                }
                
                return profile_data
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile details: {e}")
        
        return None
    
    def search_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for journalists at a specific company/publication"""
        journalists = []
        
        try:
            # Search for people at specific company
            search_query = f"journalist {company_name}"
            results = self._search_people(search_query, 20)
            
            for profile in results:
                if company_name.lower() in profile.get('current_publication', '').lower():
                    journalists.append(profile)
            
        except Exception as e:
            logger.error(f"Error searching by company {company_name}: {e}")
        
        return journalists
