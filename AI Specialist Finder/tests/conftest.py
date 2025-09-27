import sys
import os
import pytest
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add src directory to Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after path setup
from database.database_manager import DatabaseManager
from database.models import Journalist
from main import JournalistFinderAgent

@pytest.fixture
def temp_db_manager():
    """Create a temporary database manager for testing"""
    # Create temporary database file
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, 'test.db')
    temp_db_url = f'sqlite:///{temp_db_path}'
    
    # Create database manager with temporary database
    db_manager = DatabaseManager(temp_db_url)
    db_manager.create_tables()
    
    yield db_manager
    
    # Cleanup
    db_manager.close()
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def integration_agent():
    """Create a mocked JournalistFinderAgent for integration testing"""
    with patch('main.JournalistFinderAgent') as mock_agent_class:
        # Create mock agent instance
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Mock all scrapers
        mock_agent.newspaper_scraper = Mock()
        mock_agent.newsapi_scraper = Mock()
        mock_agent.twitter_scraper = Mock()
        mock_agent.linkedin_scraper = Mock()
        mock_agent.linkedin_api_scraper = Mock()
        mock_agent.google_scholar_scraper = Mock()
        mock_agent.researchgate_scraper = Mock()
        mock_agent.clearbit_scraper = Mock()
        
        # Mock database manager
        mock_agent.db_manager = Mock()
        
        # Mock analysis components
        mock_agent.reputation_analyzer = Mock()
        mock_agent.relevance_scorer = Mock()
        
        yield mock_agent
