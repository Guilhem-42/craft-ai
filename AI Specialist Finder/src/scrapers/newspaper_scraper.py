"""
Newspaper scraper for finding AI/Programming journalists
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from loguru import logger
import json

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import NEWS_SOURCES, AI_KEYWORDS, SCRAPING_DELAY, MAX_RETRIES, TIMEOUT

class NewspaperScraper:
    """Scraper for extracting journalist information from news websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all configured news sources"""
        all_journalists = []
        
        for source in NEWS_SOURCES:
            logger.info(f"Scraping {source}...")
            try:
                journalists = self.scrape_source(source)
                all_journalists.extend(journalists)
                time.sleep(SCRAPING_DELAY)
            except Exception as e:
                logger.error(f"Error scraping {source}: {e}")
                continue
        
        logger.info(f"Total journalists found: {len(all_journalists)}")
        return all_journalists
    
    def scrape_source(self, domain: str) -> List[Dict[str, Any]]:
        """Scrape a specific news source"""
        journalists = []
        
        # Try different common paths for author pages
        author_paths = [
            '/authors',
            '/writers',
            '/staff',
            '/team',
            '/contributors',
            '/about/staff'
        ]
        
        base_url = f"https://{domain}"
        
        for path in author_paths:
            try:
                url = urljoin(base_url, path)
                response = self._make_request(url)
                
                if response and response.status_code == 200:
                    page_journalists = self._extract_journalists_from_page(response.text, base_url)
                    journalists.extend(page_journalists)
                    
                    if page_journalists:
                        logger.info(f"Found {len(page_journalists)} journalists on {url}")
                        break  # Found authors page, no need to try other paths
                        
            except Exception as e:
                logger.warning(f"Could not scrape {url}: {e}")
                continue
        
        # Also try to find journalists from recent AI/tech articles
        tech_journalists = self._scrape_from_articles(base_url)
        journalists.extend(tech_journalists)
        
        return self._deduplicate_journalists(journalists)
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retries"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=TIMEOUT)
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        return None
    
    def _extract_journalists_from_page(self, html: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract journalist information from HTML page"""
        soup = BeautifulSoup(html, 'html.parser')
        journalists = []
        
        # Common selectors for author information
        author_selectors = [
            '.author-card',
            '.staff-member',
            '.writer-profile',
            '.contributor',
            '.team-member',
            '[class*="author"]',
            '[class*="staff"]',
            '[class*="writer"]'
        ]
        
        for selector in author_selectors:
            author_elements = soup.select(selector)
            
            for element in author_elements:
                journalist_data = self._extract_journalist_data(element, base_url)
                if journalist_data and self._is_tech_journalist(journalist_data):
                    journalists.append(journalist_data)
        
        return journalists
    
    def _extract_journalist_data(self, element, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract journalist data from HTML element"""
        try:
            # Extract name
            name_selectors = ['h1', 'h2', 'h3', '.name', '.author-name', '[class*="name"]']
            name = None
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            if not name:
                return None
            
            # Extract bio/description
            bio_selectors = ['.bio', '.description', '.about', 'p']
            bio = ""
            for selector in bio_selectors:
                bio_elem = element.select_one(selector)
                if bio_elem:
                    bio = bio_elem.get_text().strip()
                    break
            
            # Extract email
            email = None
            email_links = element.select('a[href^="mailto:"]')
            if email_links:
                email = email_links[0]['href'].replace('mailto:', '')
            
            # Extract social media links
            twitter_handle = None
            linkedin_url = None
            
            social_links = element.select('a[href*="twitter.com"], a[href*="linkedin.com"]')
            for link in social_links:
                href = link.get('href', '')
                if 'twitter.com' in href:
                    twitter_handle = self._extract_twitter_handle(href)
                elif 'linkedin.com' in href:
                    linkedin_url = href
            
            # Extract job title
            title_selectors = ['.title', '.position', '.job-title', '[class*="title"]']
            job_title = ""
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    job_title = title_elem.get_text().strip()
                    break
            
            # Determine publication from base URL
            publication = urlparse(base_url).netloc.replace('www.', '')
            
            journalist_data = {
                'name': name,
                'bio': bio,
                'email': email,
                'twitter_handle': twitter_handle,
                'linkedin_url': linkedin_url,
                'job_title': job_title,
                'current_publication': publication,
                'source_platform': 'news_site',
                'specializations': self._extract_specializations(bio + " " + job_title)
            }
            
            return journalist_data
            
        except Exception as e:
            logger.warning(f"Error extracting journalist data: {e}")
            return None
    
    def _scrape_from_articles(self, base_url: str) -> List[Dict[str, Any]]:
        """Find journalists by scraping recent AI/tech articles"""
        journalists = []
        
        # Search for AI-related articles
        search_paths = [
            '/search?q=artificial+intelligence',
            '/tag/ai',
            '/category/technology',
            '/tech',
            '/artificial-intelligence'
        ]
        
        for path in search_paths:
            try:
                url = urljoin(base_url, path)
                response = self._make_request(url)
                
                if response and response.status_code == 200:
                    article_journalists = self._extract_journalists_from_articles(response.text, base_url)
                    journalists.extend(article_journalists)
                    
            except Exception as e:
                logger.warning(f"Error scraping articles from {url}: {e}")
                continue
        
        return journalists
    
    def _extract_journalists_from_articles(self, html: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract journalist information from article listings"""
        soup = BeautifulSoup(html, 'html.parser')
        journalists = []
        
        # Find article elements
        article_selectors = ['article', '.article', '.post', '[class*="article"]']
        
        for selector in article_selectors:
            articles = soup.select(selector)
            
            for article in articles:
                # Look for author information in articles
                author_selectors = ['.author', '.byline', '[class*="author"]', '[rel="author"]']
                
                for auth_selector in author_selectors:
                    author_elem = article.select_one(auth_selector)
                    if author_elem:
                        author_name = author_elem.get_text().strip()
                        
                        # Check if this is an AI/tech related article
                        article_text = article.get_text().lower()
                        if any(keyword.lower() in article_text for keyword in AI_KEYWORDS):
                            
                            journalist_data = {
                                'name': author_name,
                                'current_publication': urlparse(base_url).netloc.replace('www.', ''),
                                'source_platform': 'news_site',
                                'specializations': ['artificial intelligence', 'technology'],
                                'ai_relevance_score': 0.8  # High relevance since found in AI article
                            }
                            
                            journalists.append(journalist_data)
        
        return journalists
    
    def _is_tech_journalist(self, journalist_data: Dict[str, Any]) -> bool:
        """Check if journalist covers tech/AI topics"""
        text_to_check = " ".join([
            journalist_data.get('bio', ''),
            journalist_data.get('job_title', ''),
            " ".join(journalist_data.get('specializations', []))
        ]).lower()
        
        tech_keywords = AI_KEYWORDS + [
            'technology', 'tech', 'software', 'programming', 'coding',
            'developer', 'engineer', 'startup', 'innovation', 'digital'
        ]
        
        return any(keyword.lower() in text_to_check for keyword in tech_keywords)
    
    def _extract_specializations(self, text: str) -> List[str]:
        """Extract specializations from bio/title text"""
        specializations = []
        text_lower = text.lower()
        
        specialization_map = {
            'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning'],
            'programming': ['programming', 'coding', 'software development', 'developer'],
            'data science': ['data science', 'data analysis', 'analytics'],
            'cybersecurity': ['cybersecurity', 'security', 'privacy'],
            'blockchain': ['blockchain', 'cryptocurrency', 'crypto'],
            'robotics': ['robotics', 'automation', 'robots'],
            'cloud computing': ['cloud', 'aws', 'azure', 'google cloud']
        }
        
        for specialization, keywords in specialization_map.items():
            if any(keyword in text_lower for keyword in keywords):
                specializations.append(specialization)
        
        return specializations if specializations else ['technology']
    
    def _extract_twitter_handle(self, twitter_url: str) -> Optional[str]:
        """Extract Twitter handle from URL"""
        try:
            # Extract handle from URL like https://twitter.com/username
            match = re.search(r'twitter\.com/([^/?]+)', twitter_url)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None
    
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
