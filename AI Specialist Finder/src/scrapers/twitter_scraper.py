"""
Twitter scraper for finding AI/Programming journalists
"""
import tweepy
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import re

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    AI_KEYWORDS, SCRAPING_DELAY
)

class TwitterScraper:
    """Scraper for finding journalists on Twitter who cover AI/Programming topics"""
    
    def __init__(self):
        """Initialize Twitter API client"""
        self.client = None
        self.api = None
        self._setup_twitter_api()
    
    def _setup_twitter_api(self):
        """Setup Twitter API authentication"""
        try:
            if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
                logger.warning("Twitter API credentials not found. Twitter scraping will be disabled.")
                return
            
            # Setup API v1.1 for user search
            auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Setup API v2 for enhanced features
            self.client = tweepy.Client(
                bearer_token=None,  # We'll use OAuth 1.0a
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            logger.info("Twitter API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.client = None
            self.api = None
    
    def search_ai_journalists(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for journalists who tweet about AI/Programming"""
        if not self.api:
            logger.warning("Twitter API not available")
            return []
        
        journalists = []
        
        # Search queries for finding AI journalists
        search_queries = [
            "journalist AI artificial intelligence bio:journalist",
            "tech reporter machine learning bio:reporter",
            "technology writer programming bio:writer",
            "AI correspondent neural networks bio:correspondent",
            "tech journalist automation bio:journalist",
            "software journalist coding bio:journalist"
        ]
        
        for query in search_queries:
            try:
                logger.info(f"Searching Twitter with query: {query}")
                users = self._search_users_by_query(query, max_results // len(search_queries))
                
                for user in users:
                    journalist_data = self._extract_journalist_data(user)
                    if journalist_data and self._is_relevant_journalist(journalist_data):
                        journalists.append(journalist_data)
                
                time.sleep(SCRAPING_DELAY)
                
            except Exception as e:
                logger.error(f"Error searching with query '{query}': {e}")
                continue
        
        # Also search by AI-related hashtags
        hashtag_journalists = self._search_by_hashtags()
        journalists.extend(hashtag_journalists)
        
        return self._deduplicate_journalists(journalists)
    
    def _search_users_by_query(self, query: str, max_results: int) -> List[Any]:
        """Search users by query string"""
        users = []
        
        try:
            # Use Twitter API v1.1 for user search
            searched_users = tweepy.Cursor(
                self.api.search_users,
                q=query,
                count=20
            ).items(max_results)
            
            for user in searched_users:
                users.append(user)
                
        except Exception as e:
            logger.error(f"Error in user search: {e}")
        
        return users
    
    def _search_by_hashtags(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for journalists using AI-related hashtags"""
        journalists = []
        
        if not self.api:
            return journalists
        
        # AI-related hashtags
        hashtags = [
            "#AI", "#MachineLearning", "#ArtificialIntelligence", 
            "#DeepLearning", "#TechNews", "#Programming",
            "#SoftwareDevelopment", "#DataScience", "#Automation"
        ]
        
        for hashtag in hashtags[:3]:  # Limit to avoid rate limits
            try:
                # Search recent tweets with hashtag
                tweets = tweepy.Cursor(
                    self.api.search_tweets,
                    q=f"{hashtag} journalist OR reporter OR writer",
                    result_type="recent",
                    lang="en"
                ).items(20)
                
                for tweet in tweets:
                    user = tweet.user
                    if self._is_likely_journalist(user):
                        journalist_data = self._extract_journalist_data(user)
                        if journalist_data:
                            journalists.append(journalist_data)
                
                time.sleep(SCRAPING_DELAY)
                
            except Exception as e:
                logger.error(f"Error searching hashtag {hashtag}: {e}")
                continue
        
        return journalists
    
    def _extract_journalist_data(self, user) -> Optional[Dict[str, Any]]:
        """Extract journalist data from Twitter user object"""
        try:
            # Extract basic information
            name = user.name
            username = user.screen_name
            bio = user.description or ""
            location = user.location or ""
            
            # Extract metrics
            followers_count = user.followers_count
            following_count = user.friends_count
            tweet_count = user.statuses_count
            
            # Calculate engagement rate (simplified)
            engagement_rate = min(following_count / max(followers_count, 1), 1.0) if followers_count > 0 else 0
            
            # Extract website/email from bio
            website = user.url
            email = self._extract_email_from_bio(bio)
            
            # Extract current publication from bio
            publication = self._extract_publication_from_bio(bio)
            
            # Determine specializations
            specializations = self._extract_specializations_from_bio(bio)
            
            # Calculate AI relevance score
            ai_relevance = self._calculate_ai_relevance(bio, name)
            
            journalist_data = {
                'name': name,
                'bio': bio,
                'email': email,
                'twitter_handle': username,
                'website_url': website,
                'current_publication': publication,
                'twitter_followers': followers_count,
                'country': self._extract_country_from_location(location),
                'city': self._extract_city_from_location(location),
                'reputation_score': self._calculate_reputation_score(user),
                'ai_relevance_score': ai_relevance,
                'specializations': specializations,
                'source_platform': 'twitter',
                'programming_expertise': self._has_programming_expertise(bio)
            }
            
            return journalist_data
            
        except Exception as e:
            logger.error(f"Error extracting journalist data: {e}")
            return None
    
    def _is_likely_journalist(self, user) -> bool:
        """Check if user is likely a journalist based on profile"""
        bio = (user.description or "").lower()
        name = (user.name or "").lower()
        
        journalist_keywords = [
            'journalist', 'reporter', 'writer', 'correspondent', 
            'editor', 'columnist', 'freelance', 'news', 'media',
            'tech writer', 'technology reporter', 'ai reporter'
        ]
        
        # Check bio and name for journalist keywords
        has_journalist_keywords = any(keyword in bio or keyword in name for keyword in journalist_keywords)
        
        # Check follower count (journalists usually have decent following)
        has_decent_following = user.followers_count >= 100
        
        # Check if verified (many journalists are verified)
        is_verified = user.verified
        
        # Check if has website (many journalists have personal websites)
        has_website = bool(user.url)
        
        return has_journalist_keywords and (has_decent_following or is_verified or has_website)
    
    def _is_relevant_journalist(self, journalist_data: Dict[str, Any]) -> bool:
        """Check if journalist is relevant for AI/Programming topics"""
        ai_relevance = journalist_data.get('ai_relevance_score', 0)
        programming_expertise = journalist_data.get('programming_expertise', False)
        
        return ai_relevance >= 0.3 or programming_expertise
    
    def _extract_email_from_bio(self, bio: str) -> Optional[str]:
        """Extract email from bio using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, bio)
        return matches[0] if matches else None
    
    def _extract_publication_from_bio(self, bio: str) -> Optional[str]:
        """Extract current publication from bio"""
        # Common patterns for publications in bios
        patterns = [
            r'@(\w+)',  # @publication
            r'(\w+)\s+(?:journalist|reporter|writer|correspondent)',
            r'(?:at|for)\s+(\w+)',
            r'(\w+)\s+(?:news|media|magazine|newspaper)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, bio, re.IGNORECASE)
            if matches:
                # Filter out common non-publication words
                excluded = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                publications = [match for match in matches if match.lower() not in excluded]
                if publications:
                    return publications[0]
        
        return None
    
    def _extract_specializations_from_bio(self, bio: str) -> List[str]:
        """Extract specializations from bio"""
        specializations = []
        bio_lower = bio.lower()
        
        specialization_keywords = {
            'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'programming': ['programming', 'coding', 'software', 'developer', 'development'],
            'data science': ['data science', 'data analysis', 'analytics', 'big data'],
            'cybersecurity': ['cybersecurity', 'security', 'privacy', 'cyber'],
            'blockchain': ['blockchain', 'cryptocurrency', 'crypto', 'bitcoin'],
            'robotics': ['robotics', 'automation', 'robots', 'iot'],
            'cloud computing': ['cloud', 'aws', 'azure', 'google cloud'],
            'technology': ['tech', 'technology', 'innovation', 'digital']
        }
        
        for specialization, keywords in specialization_keywords.items():
            if any(keyword in bio_lower for keyword in keywords):
                specializations.append(specialization)
        
        return specializations if specializations else ['technology']
    
    def _calculate_ai_relevance(self, bio: str, name: str) -> float:
        """Calculate AI relevance score based on bio and name"""
        text = (bio + " " + name).lower()
        
        ai_keywords_weighted = {
            'artificial intelligence': 1.0,
            'machine learning': 1.0,
            'deep learning': 0.9,
            'neural networks': 0.9,
            'ai': 0.8,
            'ml': 0.7,
            'automation': 0.6,
            'robotics': 0.6,
            'data science': 0.5,
            'programming': 0.4,
            'technology': 0.3
        }
        
        relevance_score = 0.0
        for keyword, weight in ai_keywords_weighted.items():
            if keyword in text:
                relevance_score += weight
        
        # Normalize to 0-1 range
        return min(relevance_score / 2.0, 1.0)
    
    def _has_programming_expertise(self, bio: str) -> bool:
        """Check if bio indicates programming expertise"""
        programming_keywords = [
            'programmer', 'developer', 'software engineer', 'coding',
            'python', 'javascript', 'java', 'c++', 'programming',
            'software development', 'full stack', 'backend', 'frontend'
        ]
        
        bio_lower = bio.lower()
        return any(keyword in bio_lower for keyword in programming_keywords)
    
    def _calculate_reputation_score(self, user) -> float:
        """Calculate reputation score based on Twitter metrics"""
        followers = user.followers_count
        following = user.friends_count
        tweets = user.statuses_count
        verified = user.verified
        
        # Base score from followers (logarithmic scale)
        import math
        follower_score = math.log10(max(followers, 1)) / 6.0  # Normalize to ~0-1
        
        # Engagement ratio (following/followers ratio, lower is better for journalists)
        engagement_ratio = following / max(followers, 1)
        engagement_score = max(0, 1 - engagement_ratio)
        
        # Activity score based on tweet count
        activity_score = min(tweets / 10000, 1.0)
        
        # Verification bonus
        verification_bonus = 0.2 if verified else 0.0
        
        # Combine scores
        reputation_score = (
            follower_score * 0.4 +
            engagement_score * 0.3 +
            activity_score * 0.2 +
            verification_bonus * 0.1
        )
        
        return min(reputation_score, 1.0)
    
    def _extract_country_from_location(self, location: str) -> Optional[str]:
        """Extract country from location string"""
        if not location:
            return None
        
        # Simple country extraction (can be enhanced with geopy)
        country_keywords = {
            'USA': ['usa', 'united states', 'america', 'us'],
            'UK': ['uk', 'united kingdom', 'britain', 'england', 'london'],
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
        
        # Extract first part of location (usually city)
        parts = location.split(',')
        if parts:
            return parts[0].strip()
        
        return location.strip()
    
    def _deduplicate_journalists(self, journalists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate journalists based on Twitter handle"""
        seen_handles = set()
        unique_journalists = []
        
        for journalist in journalists:
            handle = journalist.get('twitter_handle', '').lower()
            if handle and handle not in seen_handles:
                seen_handles.add(handle)
                unique_journalists.append(journalist)
        
        return unique_journalists
    
    def get_user_details(self, username: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific Twitter user"""
        if not self.api:
            return None
        
        try:
            user = self.api.get_user(screen_name=username)
            return self._extract_journalist_data(user)
        except Exception as e:
            logger.error(f"Error getting user details for {username}: {e}")
            return None
