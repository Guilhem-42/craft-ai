import httpx
from loguru import logger
from typing import Dict, Any, Optional

class ClearbitScraper:
    """Scraper for Clearbit API to enrich journalist data"""

    BASE_URL = "https://person.clearbit.com/v2/combined/find"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=10.0)

    def enrich_person(self, email: str) -> Optional[Dict[str, Any]]:
        """Enrich person data using email"""
        params = {
            "email": email
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            response = self.client.get(self.BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully enriched data for email: {email}")
            return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while enriching person data: {e}")
            return None

    def extract_journalist_info(self, clearbit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract journalist-relevant info from Clearbit data"""
        person = clearbit_data.get("person", {})
        company = clearbit_data.get("company", {})

        journalist_info = {
            "name": person.get("name", {}).get("fullName"),
            "email": person.get("email"),
            "current_publication": company.get("name"),
            "bio": person.get("bio"),
            "twitter_handle": person.get("twitter", {}).get("handle"),
            "linkedin_url": person.get("linkedin", {}).get("url"),
            "country": person.get("location", {}).get("country"),
            "city": person.get("location", {}).get("city"),
            "source_platform": "clearbit"
        }
        return journalist_info
