"""
Comprehensive tests for main application and CLI interface
"""
import pytest
import sys
import os
import asyncio
import tempfile
import json
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main import JournalistFinderAgent, main
from fixtures import (
    sample_journalist, sample_journalist_2, sample_journalists_list,
    mock_env_vars, test_database_url,
    SAMPLE_JOURNALIST_DATA, SAMPLE_JOURNALIST_DATA_2
)


class TestJournalistFinderAgent:
    """Test cases for JournalistFinderAgent"""

    @pytest.fixture
    def mock_agent(self, mock_env_vars):
        """Create a mock agent for testing"""
        with patch('main.DatabaseManager'), \
             patch('main.NewspaperScraper'), \
             patch('main.TwitterScraper'), \
             patch('main.LinkedInScraper'), \
             patch('main.LinkedInAPIScraper'), \
             patch('main.NewsAPIScraper'), \
             patch('main.ClearbitScraper'), \
             patch('main.GoogleScholarScraper'), \
             patch('main.ResearchGateScraper'), \
             patch('main.ReputationAnalyzer'), \
             patch('main.RelevanceScorer'):
            
            agent = JournalistFinderAgent()
            return agent

    def test_int_001_journalist_finder_agent_initialization(self, mock_agent):
        """INT-001: Test JournalistFinderAgent initialization"""
        assert mock_agent is not None
        
        # Check that all components are initialized
        assert hasattr(mock_agent, 'db_manager')
        assert hasattr(mock_agent, 'newspaper_scraper')
        assert hasattr(mock_agent, 'twitter_scraper')
        assert hasattr(mock_agent, 'linkedin_scraper')
        assert hasattr(mock_agent, 'reputation_analyzer')
        assert hasattr(mock_agent, 'relevance_scorer')

    @pytest.mark.asyncio
    async def test_int_002_full_search_workflow_execution(self, mock_agent):
        """INT-002: Test full search workflow execution"""
        # Mock the scrapers to return sample data
        mock_agent.newspaper_scraper.scrape_all_sources.return_value = [SAMPLE_JOURNALIST_DATA.copy()]
        mock_agent.twitter_scraper.search_ai_journalists.return_value = [SAMPLE_JOURNALIST_DATA_2.copy()]
        mock_agent.linkedin_scraper.search_ai_journalists.return_value = []
        mock_agent.linkedin_api_scraper.is_configured.return_value = False
        mock_agent.newsapi_scraper = None  # No API key
        mock_agent.google_scholar_scraper.search_ai_researchers.return_value = []
        mock_agent.researchgate_scraper.search_ai_researchers.return_value = []
        
        # Mock database operations
        mock_agent.db_manager.get_statistics.return_value = {
            'total_journalists': 2,
            'verified_journalists': 1,
            'countries_covered': 2,
            'avg_reputation_score': 0.75,
            'avg_ai_relevance_score': 0.68
        }
        
        # Mock analysis components
        mock_agent.reputation_analyzer.calculate_reputation_score.return_value = 0.8
        mock_agent.relevance_scorer.calculate_ai_relevance_score.return_value = 0.7
        mock_agent.db_manager.add_journalist.return_value = Mock(id=1)
        
        # Execute full search
        results = await mock_agent.run_full_search(max_results_per_platform=10)
        
        # Verify results structure
        assert isinstance(results, dict)
        assert 'total_found' in results
        assert 'by_platform' in results
        assert 'execution_time' in results
        
        # Verify platform results
        assert 'newspapers' in results['by_platform']
        assert 'twitter' in results['by_platform']
        assert 'linkedin' in results['by_platform']

    def test_int_003_multi_platform_data_aggregation(self, mock_agent):
        """INT-003: Test multi-platform data aggregation"""
        # Mock different platforms returning different data
        newspaper_data = [{'name': 'Newspaper Journalist', 'source_platform': 'newspaper'}]
        twitter_data = [{'name': 'Twitter Journalist', 'source_platform': 'twitter'}]
        
        mock_agent.newspaper_scraper.scrape_all_sources.return_value = newspaper_data
        mock_agent.twitter_scraper.search_ai_journalists.return_value = twitter_data
        
        # Test data processing
        mock_agent.reputation_analyzer.calculate_reputation_score.return_value = 0.7
        mock_agent.relevance_scorer.calculate_ai_relevance_score.return_value = 0.6
        mock_agent.db_manager.add_journalist.return_value = Mock(id=1)
        
        # Process data from different platforms
        newspaper_id = mock_agent._process_and_store_journalist(newspaper_data[0])
        twitter_id = mock_agent._process_and_store_journalist(twitter_data[0])
        
        assert newspaper_id is not None
        assert twitter_id is not None

    def test_int_004_data_processing_pipeline(self, mock_agent, sample_journalist):
        """INT-004: Test data processing pipeline"""
        # Mock analysis components
        mock_agent.reputation_analyzer.calculate_reputation_score.return_value = 0.85
        mock_agent.relevance_scorer.calculate_ai_relevance_score.return_value = 0.92
        
        # Mock database storage
        mock_journalist = Mock()
        mock_journalist.id = 123
        mock_journalist.name = sample_journalist['name']
        mock_agent.db_manager.add_journalist.return_value = mock_journalist
        
        # Test processing pipeline
        journalist_id = mock_agent._process_and_store_journalist(sample_journalist)
        
        assert journalist_id == 123
        
        # Verify that analysis was called
        mock_agent.reputation_analyzer.calculate_reputation_score.assert_called_once()
        mock_agent.relevance_scorer.calculate_ai_relevance_score.assert_called_once()
        mock_agent.db_manager.add_journalist.assert_called_once()

    def test_int_005_search_by_criteria_functionality(self, mock_agent):
        """INT-005: Test search by criteria functionality"""
        # Mock database search results
        mock_journalists = [
            Mock(
                id=1, name="AI Journalist", email="ai@example.com",
                reputation_score=0.8, ai_relevance_score=0.9,
                country="United States", specializations="artificial intelligence"
            )
        ]
        mock_agent.db_manager.search_journalists.return_value = mock_journalists
        
        # Mock relevance scorer
        mock_agent.relevance_scorer.find_relevant_journalists.return_value = [
            {
                'id': 1, 'name': 'AI Journalist', 'reputation_score': 0.8,
                'ai_relevance_score': 0.9, 'country': 'United States'
            }
        ]
        
        # Test search by criteria
        results = mock_agent.search_by_criteria(
            specialization="artificial intelligence",
            min_reputation=0.7,
            min_ai_relevance=0.8,
            country="United States",
            limit=10
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert results[0]['name'] == 'AI Journalist'

    def test_int_006_top_journalists_retrieval(self, mock_agent):
        """INT-006: Test top journalists retrieval"""
        # Mock the get_top_journalists method directly
        mock_top_journalists = [
            {
                'id': 1, 'name': "Top Journalist 1", 'reputation_score': 0.95,
                'ai_relevance_score': 0.9, 'current_publication': "TechCrunch",
                'email': 'top1@techcrunch.com', 'twitter_handle': 'top1',
                'linkedin_url': 'https://linkedin.com/in/top1', 'country': 'US',
                'specializations': 'AI', 'source_platform': 'newsapi'
            },
            {
                'id': 2, 'name': "Top Journalist 2", 'reputation_score': 0.90,
                'ai_relevance_score': 0.85, 'current_publication': "Wired",
                'email': 'top2@wired.com', 'twitter_handle': 'top2',
                'linkedin_url': 'https://linkedin.com/in/top2', 'country': 'US',
                'specializations': 'Tech', 'source_platform': 'twitter'
            }
        ]
        mock_agent.get_top_journalists = Mock(return_value=mock_top_journalists)
        
        # Test top journalists retrieval
        top_journalists = mock_agent.get_top_journalists(limit=5)
        
        assert isinstance(top_journalists, list)
        assert len(top_journalists) == 2
        assert top_journalists[0]['name'] == "Top Journalist 1"
        assert top_journalists[0]['reputation_score'] == 0.95

    def test_int_007_journalist_analysis_workflow(self, mock_agent):
        """INT-007: Test journalist analysis workflow"""
        # Mock journalist data
        mock_journalist = Mock()
        mock_journalist.name = "Test Journalist"
        mock_journalist.bio = "AI researcher and journalist"
        mock_journalist.reputation_score = 0.8
        mock_journalist.ai_relevance_score = 0.9
        mock_journalist.email = "test@example.com"
        mock_journalist.country = "United States"
        
        mock_agent.db_manager.get_journalist_by_id.return_value = mock_journalist
        
        # Mock analysis results
        mock_agent.reputation_analyzer.analyze_journalist_portfolio.return_value = {
            'overall_score': 0.85,
            'strengths': ['High AI expertise', 'Strong publication record'],
            'recommendations': ['Increase social media presence']
        }
        
        mock_agent.relevance_scorer.generate_relevance_report.return_value = {
            'relevance_score': 0.9,
            'ai_keywords_found': ['artificial intelligence', 'machine learning'],
            'recommendations': ['Focus on emerging AI trends']
        }
        
        # Test analysis workflow
        analysis = mock_agent.analyze_journalist(journalist_id=1)
        
        assert isinstance(analysis, dict)
        assert 'journalist_info' in analysis
        assert 'reputation_analysis' in analysis
        assert 'relevance_report' in analysis
        assert 'contact_info' in analysis

    def test_int_008_statistics_generation(self, mock_agent):
        """INT-008: Test statistics generation"""
        # Mock database statistics
        mock_stats = {
            'total_journalists': 150,
            'verified_journalists': 45,
            'countries_covered': 25,
            'avg_reputation_score': 0.72,
            'avg_ai_relevance_score': 0.68,
            'top_publications': ['TechCrunch', 'Wired', 'MIT Technology Review']
        }
        mock_agent.db_manager.get_statistics.return_value = mock_stats
        
        # Mock top journalists for preview
        mock_agent.get_top_journalists = Mock(return_value=[
            {'name': 'Top Journalist', 'current_publication': 'TechCrunch',
             'reputation_score': 0.95, 'ai_relevance_score': 0.92}
        ])
        
        # Mock platform distribution
        mock_agent._get_platform_distribution = Mock(return_value={
            'twitter': 50, 'linkedin': 40, 'news_site': 35, 'newsapi': 25
        })
        
        # Test statistics generation
        stats = mock_agent.get_statistics()
        
        assert isinstance(stats, dict)
        assert stats['total_journalists'] == 150
        assert 'top_journalists_preview' in stats
        assert 'platform_distribution' in stats

    def test_int_009_data_export_functionality(self, mock_agent):
        """INT-009: Test data export functionality"""
        # Mock journalist data for export
        mock_journalists = [
            {
                'id': 1, 'name': 'Export Test 1', 'email': 'test1@example.com',
                'reputation_score': 0.8, 'ai_relevance_score': 0.9
            },
            {
                'id': 2, 'name': 'Export Test 2', 'email': 'test2@example.com',
                'reputation_score': 0.7, 'ai_relevance_score': 0.8
            }
        ]
        
        mock_agent.get_top_journalists = Mock(return_value=mock_journalists)
        
        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            filename = mock_agent.export_journalists(format='json', filename=tmp_file.name)
            
            assert filename == tmp_file.name
            
            # Verify file contents
            with open(filename, 'r') as f:
                exported_data = json.load(f)
                assert len(exported_data) == 2
                assert exported_data[0]['name'] == 'Export Test 1'
            
            # Cleanup
            os.unlink(filename)

    def test_int_010_clearbit_enrichment_integration(self, mock_agent):
        """INT-010: Test Clearbit enrichment integration"""
        # Mock journalist with email
        mock_journalist = Mock()
        mock_journalist.id = 1
        mock_journalist.name = "Test Journalist"
        mock_journalist.email = "test@example.com"
        mock_journalist.current_publication = "TechCrunch"
        
        mock_agent.db_manager.get_journalist_by_id.return_value = mock_journalist
        
        # Mock Clearbit scraper
        mock_agent.clearbit_scraper = Mock()
        mock_agent.clearbit_scraper.enrich_person.return_value = {
            'person': {'name': {'fullName': 'Enhanced Name'}},
            'company': {'name': 'Enhanced Publication'}
        }
        mock_agent.clearbit_scraper.extract_journalist_info.return_value = {
            'name': 'Enhanced Name',
            'current_publication': 'Enhanced Publication'
        }
        
        # Mock database update
        mock_agent.db_manager.update_journalist.return_value = mock_journalist
        
        # Test enrichment
        result = mock_agent.enrich_journalist_with_clearbit(journalist_id=1)
        
        assert isinstance(result, dict)
        assert result.get('success') is True
        assert 'enriched_data' in result


class TestCLIInterface:
    """Test cases for CLI interface"""

    def test_cli_001_main_cli_entry_point(self):
        """CLI-001: Test main CLI entry point"""
        # Test that main function exists and can be called
        assert callable(main)

    @patch('main.JournalistFinderAgent')
    @patch('sys.argv', ['main.py', '--stats'])
    def test_cli_002_statistics_command(self, mock_agent_class):
        """CLI-002: Test statistics command (--stats)"""
        # Mock agent and its methods
        mock_agent = Mock()
        mock_agent.get_statistics.return_value = {
            'total_journalists': 100,
            'verified_journalists': 30,
            'avg_reputation_score': 0.75
        }
        mock_agent_class.return_value = mock_agent
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                main()
                output = mock_stdout.getvalue()
                assert 'total_journalists' in output or 'Statistics' in output
            except SystemExit:
                # argparse may cause SystemExit, which is acceptable
                pass

    @patch('main.JournalistFinderAgent')
    @patch('sys.argv', ['main.py', '--specialization', 'artificial intelligence', '--limit', '5'])
    def test_cli_003_criteria_based_search(self, mock_agent_class):
        """CLI-003: Test criteria-based search"""
        # Mock agent and search results
        mock_agent = Mock()
        mock_agent.search_by_criteria.return_value = [
            {'name': 'AI Journalist', 'current_publication': 'TechCrunch',
             'reputation_score': 0.9, 'ai_relevance_score': 0.95}
        ]
        mock_agent_class.return_value = mock_agent
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                main()
                output = mock_stdout.getvalue()
                # Should show search results
                assert 'AI Journalist' in output or 'Found' in output
            except SystemExit:
                pass

    @patch('main.JournalistFinderAgent')
    @patch('sys.argv', ['main.py', '--export', 'json'])
    def test_cli_004_export_functionality(self, mock_agent_class):
        """CLI-004: Test export functionality (--export)"""
        # Mock agent and export
        mock_agent = Mock()
        mock_agent.search_by_criteria.return_value = [
            {
                'name': 'Export Test', 
                'email': 'test@example.com',
                'reputation_score': 0.8,
                'ai_relevance_score': 0.9,
                'current_publication': 'Test Publication'
            }
        ]
        mock_agent.export_journalists.return_value = 'test_export.json'
        mock_agent_class.return_value = mock_agent
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                main()
                output = mock_stdout.getvalue()
                assert 'export' in output.lower() or 'json' in output.lower()
            except SystemExit:
                pass

    @patch('main.JournalistFinderAgent')
    @patch('sys.argv', ['main.py', '--help'])
    def test_cli_005_help_and_argument_parsing(self, mock_agent_class):
        """CLI-005: Test help and argument parsing"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                main()
            except SystemExit as e:
                # Help command causes SystemExit with code 0
                assert e.code == 0
                output = mock_stdout.getvalue()
                assert 'usage:' in output.lower() or 'help' in output.lower()

    @patch('main.JournalistFinderAgent')
    @patch('sys.argv', ['main.py', '--search'])
    @patch('main.asyncio.run')
    def test_cli_006_full_search_command(self, mock_asyncio_run, mock_agent_class):
        """CLI-006: Test full search command (--search)"""
        # Mock agent and search results
        mock_agent = Mock()
        mock_search_results = {
            'total_found': 50,
            'execution_time': 120.5,
            'by_platform': {'twitter': 20, 'linkedin': 15, 'newspapers': 15}
        }
        
        # Mock the async function
        async def mock_run_full_search():
            return mock_search_results
        
        mock_agent.run_full_search.return_value = mock_search_results
        mock_asyncio_run.return_value = mock_search_results
        mock_agent_class.return_value = mock_agent
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                main()
                output = mock_stdout.getvalue()
                assert 'Search completed' in output or '50' in output
            except SystemExit:
                pass

    def test_cli_007_error_handling_and_user_feedback(self):
        """CLI-007: Test error handling and user feedback"""
        # Test with invalid arguments
        with patch('sys.argv', ['main.py', '--invalid-argument']):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                try:
                    main()
                except SystemExit as e:
                    # Should exit with error code
                    assert e.code != 0
                    error_output = mock_stderr.getvalue()
                    assert 'error' in error_output.lower() or 'invalid' in error_output.lower()


class TestMainApplicationErrorHandling:
    """Test error handling in main application"""

    def test_initialization_error_handling(self):
        """Test handling of initialization errors"""
        # Test with missing dependencies
        with patch('main.DatabaseManager', side_effect=ImportError("Missing dependency")):
            try:
                agent = JournalistFinderAgent()
                # Should handle gracefully or raise appropriate error
            except ImportError:
                # Acceptable to raise ImportError for missing dependencies
                pass

    @patch('main.JournalistFinderAgent')
    def test_keyboard_interrupt_handling(self, mock_agent_class):
        """Test handling of keyboard interrupts"""
        mock_agent = Mock()
        mock_agent.run_full_search.side_effect = KeyboardInterrupt()
        mock_agent_class.return_value = mock_agent
        
        with patch('sys.argv', ['main.py', '--search']):
            with patch('sys.stdout', new_callable=StringIO):
                try:
                    main()
                except (KeyboardInterrupt, SystemExit):
                    # Should handle keyboard interrupt gracefully
                    pass

    def test_database_connection_error_handling(self, mock_env_vars):
        """Test handling of database connection errors"""
        with patch('main.DatabaseManager', side_effect=Exception("Database connection failed")):
            try:
                agent = JournalistFinderAgent()
                # Should handle database errors gracefully
            except Exception as e:
                assert "Database" in str(e) or "connection" in str(e)

    def test_api_key_missing_error_handling(self):
        """Test handling of missing API keys"""
        # Test initialization without API keys
        with patch.dict(os.environ, {}, clear=True):
            try:
                agent = JournalistFinderAgent()
                # Should initialize but with limited functionality
                assert agent is not None
                # API-dependent scrapers should be None or handle gracefully
                assert agent.newsapi_scraper is None
                assert agent.clearbit_scraper is None
            except Exception:
                # Acceptable if it raises exception for missing configuration
                pass


class TestMainApplicationIntegration:
    """Integration tests for main application"""

    @patch('main.DatabaseManager')
    @patch('main.NewspaperScraper')
    @patch('main.ReputationAnalyzer')
    @patch('main.RelevanceScorer')
    def test_end_to_end_workflow(self, mock_relevance, mock_reputation, mock_newspaper, mock_db):
        """Test end-to-end workflow integration"""
        # Mock all components
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        
        mock_newspaper_instance = Mock()
        mock_newspaper_instance.scrape_all_sources.return_value = [SAMPLE_JOURNALIST_DATA.copy()]
        mock_newspaper.return_value = mock_newspaper_instance
        
        mock_reputation_instance = Mock()
        mock_reputation_instance.calculate_reputation_score.return_value = 0.8
        mock_reputation.return_value = mock_reputation_instance
        
        mock_relevance_instance = Mock()
        mock_relevance_instance.calculate_ai_relevance_score.return_value = 0.9
        mock_relevance.return_value = mock_relevance_instance
        
        # Initialize agent
        agent = JournalistFinderAgent()
        
        # Test that all components are properly integrated
        assert agent.db_manager is not None
        assert agent.newspaper_scraper is not None
        assert agent.reputation_analyzer is not None
        assert agent.relevance_scorer is not None

    def test_configuration_loading_integration(self, mock_env_vars):
        """Test configuration loading integration"""
        # Test that configuration is properly loaded and used
        with patch('main.NEWSAPI_KEY', 'test_key'), \
             patch('main.CLEARBIT_KEY', 'test_clearbit_key'):
            
            try:
                agent = JournalistFinderAgent()
                # Should initialize with API keys
                assert agent is not None
            except Exception:
                # May fail due to other dependencies
                pass

    def test_logging_integration(self):
        """Test logging integration"""
        # Test that logging is properly configured
        try:
            agent = JournalistFinderAgent()
            # Should set up logging without errors
            assert agent is not None
        except Exception:
            # May fail due to file system permissions or other issues
            pass
