"""
Main application for the Journalist Finder AI Agent
"""
import asyncio
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.scrapers.newspaper_scraper import NewspaperScraper
from src.scrapers.twitter_scraper import TwitterScraper
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.linkedin_api_scraper import LinkedInAPIScraper
from src.scrapers.newsapi_scraper import NewsAPIScraper
from src.scrapers.clearbit_scraper import ClearbitScraper
from src.scrapers.google_scholar_scraper import GoogleScholarScraper
from src.scrapers.researchgate_scraper import ResearchGateScraper
from src.scrapers.serper_french_scraper import SerperFrenchScraper
from src.analysis.reputation_analyzer import ReputationAnalyzer
from src.analysis.relevance_scorer import RelevanceScorer
from config.settings import LOG_LEVEL, LOG_FILE, NEWSAPI_KEY, CLEARBIT_KEY, DEFAULT_MIN_REPUTATION, DEFAULT_MIN_AI_RELEVANCE

class JournalistFinderAgent:
    """Main AI agent for finding and analyzing journalists"""
    
    def __init__(self):
        """Initialize the journalist finder agent"""
        self._setup_logging()
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.newspaper_scraper = NewspaperScraper()
        self.twitter_scraper = TwitterScraper()
        self.linkedin_scraper = LinkedInScraper()
        self.linkedin_api_scraper = LinkedInAPIScraper()
        self.newsapi_scraper = NewsAPIScraper(NEWSAPI_KEY) if NEWSAPI_KEY else None
        self.clearbit_scraper = ClearbitScraper(CLEARBIT_KEY) if CLEARBIT_KEY else None
        self.google_scholar_scraper = GoogleScholarScraper()
        self.researchgate_scraper = ResearchGateScraper()
        self.serper_french_scraper = SerperFrenchScraper("2fb50306700da371c6a4d46b28d6045830fa7781")
        self.reputation_analyzer = ReputationAnalyzer()
        self.relevance_scorer = RelevanceScorer()
        
        logger.info("Journalist Finder AI Agent initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            
            # Configure loguru
            logger.remove()  # Remove default handler
            logger.add(
                sys.stderr,
                level=LOG_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            )
            logger.add(
                LOG_FILE,
                level=LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="10 MB"
            )
            
        except Exception as e:
            print(f"Warning: Could not setup logging: {e}")
    
    async def run_full_search(self, max_results_per_platform: int = 100) -> Dict[str, Any]:
        """Run comprehensive search across all platforms"""
        logger.info("Starting comprehensive journalist search...")
        
        start_time = time.time()
        results = {
            'total_found': 0,
            'by_platform': {},
            'top_journalists': [],
            'statistics': {},
            'execution_time': 0
        }
        
        try:
            # Search newspapers
            logger.info("Searching newspaper websites...")
            newspaper_journalists = self.newspaper_scraper.scrape_all_sources()
            results['by_platform']['newspapers'] = len(newspaper_journalists)
            
            # Process and store newspaper journalists
            for journalist_data in newspaper_journalists:
                self._process_and_store_journalist(journalist_data)
            
            # Search Twitter
            logger.info("Searching Twitter...")
            twitter_journalists = self.twitter_scraper.search_ai_journalists(max_results_per_platform)
            results['by_platform']['twitter'] = len(twitter_journalists)
            
            # Process and store Twitter journalists
            for journalist_data in twitter_journalists:
                self._process_and_store_journalist(journalist_data)
            
            # Search LinkedIn (try API first, fallback to scraping)
            logger.info("Searching LinkedIn...")
            linkedin_journalists = []
            
            # Try LinkedIn API first if configured
            if self.linkedin_api_scraper.is_configured():
                logger.info("Using LinkedIn API...")
                try:
                    api_journalists = self.linkedin_api_scraper.search_ai_journalists(max_results_per_platform)
                    linkedin_journalists.extend(api_journalists)
                    logger.info(f"LinkedIn API found {len(api_journalists)} journalists")
                except Exception as e:
                    logger.warning(f"LinkedIn API failed, falling back to scraping: {e}")
            
            # Fallback to traditional scraping if API not available or failed
            if not linkedin_journalists:
                logger.info("Using LinkedIn scraping...")
                scraping_journalists = self.linkedin_scraper.search_ai_journalists(max_results_per_platform)
                linkedin_journalists.extend(scraping_journalists)
            
            results['by_platform']['linkedin'] = len(linkedin_journalists)

            # Process and store LinkedIn journalists
            for journalist_data in linkedin_journalists:
                self._process_and_store_journalist(journalist_data)

            # Search NewsAPI
            if self.newsapi_scraper:
                logger.info("Searching NewsAPI...")
                newsapi_articles = self.newsapi_scraper.search_articles("artificial intelligence OR machine learning OR AI", page_size=max_results_per_platform)
                newsapi_journalists = self.newsapi_scraper.extract_journalists(newsapi_articles)
                results['by_platform']['newsapi'] = len(newsapi_journalists)

                # Process and store NewsAPI journalists
                for journalist_data in newsapi_journalists:
                    self._process_and_store_journalist(journalist_data)
            else:
                logger.warning("NewsAPI key not configured, skipping NewsAPI search")
                results['by_platform']['newsapi'] = 0

            # Search Google Scholar
            logger.info("Searching Google Scholar...")
            google_scholar_researchers = self.google_scholar_scraper.search_ai_researchers(max_results_per_platform)
            results['by_platform']['google_scholar'] = len(google_scholar_researchers)

            for researcher_data in google_scholar_researchers:
                self._process_and_store_journalist(researcher_data)

            # Search ResearchGate
            logger.info("Searching ResearchGate...")
            researchgate_researchers = self.researchgate_scraper.search_ai_researchers(max_results_per_platform)
            results['by_platform']['researchgate'] = len(researchgate_researchers)

            for researcher_data in researchgate_researchers:
                self._process_and_store_journalist(researcher_data)

            # Search French journalists using Serper API
            logger.info("Searching French journalists with Serper API...")
            french_journalists = self.serper_french_scraper.search_french_journalists()
            results['by_platform']['serper_french'] = len(french_journalists)

            for journalist_data in french_journalists:
                self._process_and_store_journalist(journalist_data)
            
            # Calculate totals and get top journalists
            results['total_found'] = sum(results['by_platform'].values())
            results['top_journalists'] = self.get_top_journalists(limit=20)
            results['statistics'] = self.db_manager.get_statistics()
            
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            
            logger.info(f"Search completed in {execution_time:.2f} seconds")
            logger.info(f"Total journalists found: {results['total_found']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in full search: {e}")
            results['error'] = str(e)
            return results
    
    def _process_and_store_journalist(self, journalist_data: Dict[str, Any]) -> Optional[int]:
        """Process journalist data and store in database"""
        try:
            # Ensure minimum required fields
            if not journalist_data.get('name'):
                logger.warning("Skipping journalist without name")
                return None
            
            # Calculate reputation score (with fallback)
            try:
                journalist_data['reputation_score'] = self.reputation_analyzer.calculate_reputation_score(journalist_data)
            except Exception as e:
                logger.debug(f"Could not calculate reputation for {journalist_data.get('name')}: {e}")
                journalist_data['reputation_score'] = 0.1  # Default low score
            
            # Calculate AI relevance score (with fallback)
            try:
                journalist_data['ai_relevance_score'] = self.relevance_scorer.calculate_ai_relevance_score(journalist_data)
            except Exception as e:
                logger.debug(f"Could not calculate AI relevance for {journalist_data.get('name')}: {e}")
                journalist_data['ai_relevance_score'] = 0.05  # Default low score
            
            # Store in database
            journalist = self.db_manager.add_journalist(journalist_data)
            
            if journalist:
                logger.debug(f"Processed and stored journalist: {journalist.name}")
                return journalist.id
            
        except Exception as e:
            logger.error(f"Error processing journalist {journalist_data.get('name', 'Unknown')}: {e}")
        
        return None
    
    def search_by_criteria(self, 
                          specialization: Optional[str] = None,
                          min_reputation: float = None,
                          min_ai_relevance: float = None,
                          country: Optional[str] = None,
                          platform: Optional[str] = None,
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Search journalists by specific criteria"""
        # Use default values if None provided
        if min_reputation is None:
            min_reputation = DEFAULT_MIN_REPUTATION
        if min_ai_relevance is None:
            min_ai_relevance = DEFAULT_MIN_AI_RELEVANCE
            
        logger.info(f"Searching journalists with criteria: specialization={specialization}, "
                   f"min_reputation={min_reputation}, min_ai_relevance={min_ai_relevance}")
        
        try:
            # Get journalists from database
            journalists = self.db_manager.search_journalists(
                specialization=specialization,
                min_reputation=min_reputation,
                country=country,
                platform=platform,
                limit=limit * 2  # Get more to filter by AI relevance
            )
            
            # Convert to dict format for analysis
            journalist_dicts = []
            for journalist in journalists:
                journalist_dict = {
                    'id': journalist.id,
                    'name': journalist.name,
                    'email': journalist.email,
                    'bio': journalist.bio,
                    'job_title': journalist.job_title,
                    'current_publication': journalist.current_publication,
                    'twitter_handle': journalist.twitter_handle,
                    'linkedin_url': journalist.linkedin_url,
                    'country': journalist.country,
                    'city': journalist.city,
                    'reputation_score': journalist.reputation_score,
                    'ai_relevance_score': journalist.ai_relevance_score,
                    'specializations': journalist.specializations,
                    'source_platform': journalist.source_platform,
                    'twitter_followers': journalist.twitter_followers,
                    'programming_expertise': journalist.programming_expertise
                }
                journalist_dicts.append(journalist_dict)
            
            # Filter by AI relevance
            relevant_journalists = self.relevance_scorer.find_relevant_journalists(
                journalist_dicts,
                min_relevance=min_ai_relevance,
                specialization_filter=specialization
            )
            
            # Limit results
            return relevant_journalists[:limit]
            
        except Exception as e:
            logger.error(f"Error searching by criteria: {e}")
            return []
    
    def get_top_journalists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top journalists by reputation score"""
        try:
            journalists = self.db_manager.get_top_journalists(limit)
            
            # Convert to dict format
            top_journalists = []
            for journalist in journalists:
                journalist_dict = {
                    'id': journalist.id,
                    'name': journalist.name,
                    'email': journalist.email,
                    'current_publication': journalist.current_publication,
                    'reputation_score': journalist.reputation_score,
                    'ai_relevance_score': journalist.ai_relevance_score,
                    'twitter_handle': journalist.twitter_handle,
                    'linkedin_url': journalist.linkedin_url,
                    'country': journalist.country,
                    'specializations': journalist.specializations,
                    'source_platform': journalist.source_platform
                }
                top_journalists.append(journalist_dict)
            
            return top_journalists
            
        except Exception as e:
            logger.error(f"Error getting top journalists: {e}")
            return []
    
    def analyze_journalist(self, journalist_id: int) -> Dict[str, Any]:
        """Get detailed analysis of a specific journalist"""
        try:
            journalist = self.db_manager.get_journalist_by_id(journalist_id)
            
            if not journalist:
                return {'error': 'Journalist not found'}
            
            # Convert to dict for analysis
            journalist_dict = {
                'name': journalist.name,
                'bio': journalist.bio,
                'job_title': journalist.job_title,
                'current_publication': journalist.current_publication,
                'reputation_score': journalist.reputation_score,
                'ai_relevance_score': journalist.ai_relevance_score,
                'specializations': journalist.specializations,
                'twitter_followers': journalist.twitter_followers,
                'article_count': journalist.article_count,
                'programming_expertise': journalist.programming_expertise,
                'is_verified': journalist.is_verified
            }
            
            # Generate detailed analysis
            reputation_analysis = self.reputation_analyzer.analyze_journalist_portfolio(journalist_dict)
            relevance_report = self.relevance_scorer.generate_relevance_report(journalist_dict)
            
            analysis = {
                'journalist_info': journalist_dict,
                'reputation_analysis': reputation_analysis,
                'relevance_report': relevance_report,
                'contact_info': {
                    'email': journalist.email,
                    'twitter': journalist.twitter_handle,
                    'linkedin': journalist.linkedin_url,
                    'website': journalist.website_url
                },
                'location': {
                    'country': journalist.country,
                    'city': journalist.city,
                    'timezone': journalist.timezone
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing journalist {journalist_id}: {e}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the database"""
        try:
            base_stats = self.db_manager.get_statistics()
            
            # Add additional analysis
            top_journalists = self.get_top_journalists(5)
            
            enhanced_stats = {
                **base_stats,
                'top_journalists_preview': [
                    {
                        'name': j['name'],
                        'publication': j['current_publication'],
                        'reputation_score': j['reputation_score'],
                        'ai_relevance_score': j['ai_relevance_score']
                    }
                    for j in top_journalists
                ],
                'platform_distribution': self._get_platform_distribution(),
                'specialization_distribution': self._get_specialization_distribution()
            }
            
            return enhanced_stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}
    
    def _get_platform_distribution(self) -> Dict[str, int]:
        """Get distribution of journalists by platform"""
        try:
            # This would require a custom query - simplified version
            return {
                'twitter': len(self.db_manager.search_journalists(platform='twitter', limit=1000)),
                'linkedin': len(self.db_manager.search_journalists(platform='linkedin', limit=1000)),
                'news_site': len(self.db_manager.search_journalists(platform='news_site', limit=1000)),
                'newsapi': len(self.db_manager.search_journalists(platform='newsapi', limit=1000))
            }
        except:
            return {}
    
    def _get_specialization_distribution(self) -> Dict[str, int]:
        """Get distribution of journalists by specialization"""
        # This would require parsing specializations from the database
        # Simplified version
        return {
            'artificial_intelligence': 0,
            'programming': 0,
            'data_science': 0,
            'cybersecurity': 0,
            'technology': 0
        }

    def enrich_journalist_with_clearbit(self, journalist_id: int) -> Dict[str, Any]:
        """Enrich journalist data using Clearbit API"""
        try:
            journalist = self.db_manager.get_journalist_by_id(journalist_id)

            if not journalist or not journalist.email:
                return {'error': 'Journalist not found or no email available'}

            if not self.clearbit_scraper:
                return {'error': 'Clearbit API key not configured'}

            # Enrich data using Clearbit
            clearbit_data = self.clearbit_scraper.enrich_person(journalist.email)

            if clearbit_data:
                enriched_info = self.clearbit_scraper.extract_journalist_info(clearbit_data)

                # Update journalist in database
                update_data = {
                    'name': enriched_info.get('name') or journalist.name,
                    'current_publication': enriched_info.get('current_publication') or journalist.current_publication,
                    'bio': enriched_info.get('bio') or journalist.bio,
                    'twitter_handle': enriched_info.get('twitter_handle') or journalist.twitter_handle,
                    'linkedin_url': enriched_info.get('linkedin_url') or journalist.linkedin_url,
                    'country': enriched_info.get('country') or journalist.country,
                    'city': enriched_info.get('city') or journalist.city
                }

                self.db_manager.update_journalist(journalist_id, update_data)

                return {
                    'success': True,
                    'enriched_data': enriched_info,
                    'updated_fields': [k for k, v in update_data.items() if v != getattr(journalist, k, None)]
                }
            else:
                return {'error': 'No enrichment data found'}

        except Exception as e:
            logger.error(f"Error enriching journalist {journalist_id}: {e}")
            return {'error': str(e)}
    
    def export_journalists(self, 
                          criteria: Optional[Dict[str, Any]] = None,
                          format: str = 'json',
                          filename: Optional[str] = None) -> str:
        """Export journalists to file"""
        try:
            # Get journalists based on criteria
            if criteria:
                journalists = self.search_by_criteria(**criteria)
            else:
                journalists = self.get_top_journalists(limit=100)
            
            # Generate filename if not provided
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"journalists_export_{timestamp}.{format}"
            
            # Export based on format
            if format.lower() == 'json':
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(journalists, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'csv':
                import pandas as pd
                df = pd.DataFrame(journalists)
                df.to_csv(filename, index=False)
            
            elif format.lower() == 'md':
                # Export to markdown table
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write header
                    headers = ["ID", "Name", "Email", "Job Title", "Publication", "Reputation Score", "AI Relevance Score"]
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("|" + " --- |" * len(headers) + "\n")
                    # Write rows
                    for j in journalists:
                        row = [
                            str(j.get('id', '')),
                            str(j.get('name', '')).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').strip(),
                            str(j.get('email', '')).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').strip(),
                            str(j.get('job_title', '')).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').strip(),
                            str(j.get('current_publication', '')).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').strip(),
                            f"{j.get('reputation_score', 0):.2f}",
                            f"{j.get('ai_relevance_score', 0):.2f}"
                        ]
                        f.write("| " + " | ".join(row) + " |\n")
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(journalists)} journalists to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting journalists: {e}")
            raise

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Journalist Finder AI Agent')
    parser.add_argument('--search', action='store_true', help='Run full search')
    parser.add_argument('--specialization', type=str, help='Filter by specialization')
    parser.add_argument('--min-reputation', type=float, default=DEFAULT_MIN_REPUTATION, help=f'Minimum reputation score (default: {DEFAULT_MIN_REPUTATION})')
    parser.add_argument('--min-relevance', type=float, default=DEFAULT_MIN_AI_RELEVANCE, help=f'Minimum AI relevance score (default: {DEFAULT_MIN_AI_RELEVANCE})')
    parser.add_argument('--country', type=str, help='Filter by country')
    parser.add_argument('--limit', type=int, default=20, help='Maximum results')
    parser.add_argument('--export', type=str, choices=['json', 'csv', 'md'], help='Export format')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = JournalistFinderAgent()
    
    try:
        if args.search:
            # Run full search
            logger.info("Starting full search...")
            results = asyncio.run(agent.run_full_search())
            print(f"Search completed. Found {results['total_found']} journalists.")
            print(f"Execution time: {results['execution_time']:.2f} seconds")
            
        elif args.stats:
            # Show statistics
            stats = agent.get_statistics()
            print("\n=== Journalist Database Statistics ===")
            for key, value in stats.items():
                if key != 'top_journalists_preview':
                    print(f"{key}: {value}")
            
            if 'top_journalists_preview' in stats:
                print("\nTop Journalists:")
                for i, journalist in enumerate(stats['top_journalists_preview'], 1):
                    print(f"{i}. {journalist['name']} ({journalist['publication']}) - "
                          f"Reputation: {journalist['reputation_score']:.2f}, "
                          f"AI Relevance: {journalist['ai_relevance_score']:.2f}")
        
        else:
            # Search by criteria
            criteria = {
                'specialization': args.specialization,
                'min_reputation': args.min_reputation,
                'min_ai_relevance': args.min_relevance,
                'country': args.country,
                'limit': args.limit
            }
            
            # Remove None values
            criteria = {k: v for k, v in criteria.items() if v is not None}
            
            journalists = agent.search_by_criteria(**criteria)
            
            print(f"\nFound {len(journalists)} journalists matching criteria:")
            for i, journalist in enumerate(journalists, 1):
                print(f"{i}. {journalist['name']} ({journalist.get('current_publication', 'Unknown')})")
                print(f"   Reputation: {journalist['reputation_score']:.2f}, "
                      f"AI Relevance: {journalist['ai_relevance_score']:.2f}")
                if journalist.get('email'):
                    print(f"   Email: {journalist['email']}")
                print()
            
            # Export if requested
            if args.export:
                filename = agent.export_journalists(criteria, args.export)
                print(f"Results exported to: {filename}")
    
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
