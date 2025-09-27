"""
LinkedIn API scraper for finding AI/Programming journalists using official LinkedIn API
"""
import requests
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import urllib.parse

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import (
    LINKEDIN_CLIENT_ID, 
    LINKEDIN_CLIENT_SECRET, 
    LINKEDIN_REDIRECT_URI,
    SCRAPING_DELAY
)

class LinkedInAPIScraper:
    """Official LinkedIn API scraper for finding journalists"""
    
    def __init__(self):
        """Initialize LinkedIn API scraper"""
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.redirect_uri = LINKEDIN_REDIRECT_URI
        self.access_token = None
        self.base_url = "https://api.linkedin.com/v2"
        
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn API credentials not found. LinkedIn API scraping will be disabled.")
    
    def get_authorization_url(self) -> str:
        """Get LinkedIn OAuth authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'r_liteprofile r_emailaddress'
        }
        
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            
            data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                logger.info("Successfully obtained LinkedIn access token")
                return True
            else:
                logger.error(f"Failed to get access token: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False
    
    def search_ai_journalists(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for AI journalists using LinkedIn API"""
        if not self.access_token:
            logger.error("No access token available. Cannot search LinkedIn API.")
            return []
        
        journalists = []
        
        # Note: LinkedIn's People Search API has restrictions and may require special permissions
        # This is a framework for when those permissions are available
        
        search_queries = [
            "AI journalist",
            "artificial intelligence reporter", 
            "technology writer",
            "machine learning journalist",
            "programming correspondent"
        ]
        
        for query in search_queries:
            try:
                logger.info(f"Searching LinkedIn API for: {query}")
                results = self._search_people_api(query, max_results // len(search_queries))
                journalists.extend(results)
                time.sleep(SCRAPING_DELAY)
                
            except Exception as e:
                logger.error(f"Error searching LinkedIn API with query '{query}': {e}")
                continue
        
        return self._deduplicate_journalists(journalists)
    
    def _search_people_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search people using LinkedIn API"""
        profiles = []
        
        try:
            # Note: LinkedIn's People Search API requires special permissions
            # This is a placeholder for the actual API call structure
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # LinkedIn API endpoint for people search (requires special permissions)
            # search_url = f"{self.base_url}/people-search"
            
            # For now, we'll use the profile API to get current user info as a test
            profile_url = f"{self.base_url}/people/~"
            
            response = requests.get(profile_url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info(f"LinkedIn API connection successful: {profile_data}")
                
                # Convert to our format
                journalist_data = self._convert_api_profile(profile_data)
                if journalist_data:
                    profiles.append(journalist_data)
            else:
                logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error calling LinkedIn API: {e}")
        
        return profiles
    
    def _convert_api_profile(self, api_profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert LinkedIn API profile to our format"""
        try:
            # Extract basic information from LinkedIn API response
            first_name = api_profile.get('localizedFirstName', '')
            last_name = api_profile.get('localizedLastName', '')
            name = f"{first_name} {last_name}".strip()
            
            if not name:
                return None
            
            # Get profile picture
            profile_picture = None
            if 'profilePicture' in api_profile:
                display_image = api_profile['profilePicture'].get('displayImage')
                if display_image:
                    profile_picture = display_image
            
            # Create journalist profile
            journalist_data = {
                'name': name,
                'bio': f"LinkedIn professional: {name}",
                'job_title': "Professional",  # Would need additional API calls to get position
                'current_publication': "LinkedIn",
                'linkedin_url': f"https://www.linkedin.com/in/{api_profile.get('id', '')}",
                'profile_picture': profile_picture,
                'specializations': ['technology'],  # Default, would need more data
                'ai_relevance_score': 0.5,  # Default, would need headline/summary
                'programming_expertise': False,  # Would need more profile data
                'source_platform': 'linkedin_api',
                'reputation_score': 0.7,  # Higher score for API-verified profiles
                'linkedin_id': api_profile.get('id')
            }
            
            return journalist_data
            
        except Exception as e:
            logger.error(f"Error converting API profile: {e}")
            return None
    
    def get_profile_details(self, linkedin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile information using LinkedIn API"""
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get basic profile
            profile_url = f"{self.base_url}/people/id={linkedin_id}"
            response = requests.get(profile_url, headers=headers)
            
            if response.status_code == 200:
                return self._convert_api_profile(response.json())
            else:
                logger.error(f"Error getting profile details: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting profile details: {e}")
            return None
    
    def get_current_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user's profile (for testing)"""
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            profile_url = f"{self.base_url}/people/~"
            response = requests.get(profile_url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                return self._convert_api_profile(profile_data)
            else:
                logger.error(f"Error getting current user profile: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting current user profile: {e}")
            return None
    
    def _deduplicate_journalists(self, journalists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate journalists"""
        seen = set()
        unique_journalists = []
        
        for journalist in journalists:
            identifier = (
                journalist.get('name', '').lower().strip(),
                journalist.get('linkedin_id', '')
            )
            
            if identifier not in seen and identifier[0]:
                seen.add(identifier)
                unique_journalists.append(journalist)
        
        return unique_journalists
    
    def is_configured(self) -> bool:
        """Check if LinkedIn API is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def setup_instructions(self) -> str:
        """Return setup instructions for LinkedIn API"""
        return """
LinkedIn API Setup Instructions:

1. Go to LinkedIn Developer Portal: https://developer.linkedin.com/
2. Create a new app or use your existing app
3. Add your Client ID and Client Secret to the .env file:
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   
4. Set up OAuth redirect URI in your LinkedIn app settings:
   LINKEDIN_REDIRECT_URI=http://localhost:8080/callback
   
5. Request appropriate permissions for your app:
   - r_liteprofile (basic profile info)
   - r_emailaddress (email address)
   
Note: LinkedIn's People Search API requires special permissions that may not be 
available for all applications. Contact LinkedIn for enterprise access if needed.
"""
