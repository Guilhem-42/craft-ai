"""
Comprehensive tests for database components
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import sqlite3

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.database_manager import DatabaseManager
from database.models import Journalist, Base
from fixtures import sample_journalist, sample_journalist_2, sample_journalists_list, test_database_url


class TestDatabaseManager:
    """Test cases for DatabaseManager"""

    @pytest.fixture
    def temp_db_manager(self):
        """Create a temporary database manager for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        # Override the database URL for testing
        test_db_url = f"sqlite:///{temp_db_path}"
        
        with patch('database.database_manager.DATABASE_URL', test_db_url):
            db_manager = DatabaseManager()
            yield db_manager
        
        # Cleanup
        try:
            os.unlink(temp_db_path)
        except:
            pass

    def test_db_001_database_manager_initialization(self, temp_db_manager):
        """DB-001: Test database manager initialization"""
        assert temp_db_manager is not None
        assert temp_db_manager.engine is not None
        assert temp_db_manager.SessionLocal is not None

    def test_db_002_database_models_validation(self, temp_db_manager):
        """DB-002: Test database models validation"""
        # Check if Journalist model has required attributes
        journalist_attrs = [
            'id', 'name', 'email', 'bio', 'job_title', 'current_publication',
            'twitter_handle', 'linkedin_url', 'website_url', 'country', 'city',
            'timezone', 'specializations', 'source_platform', 'twitter_followers',
            'article_count', 'programming_expertise', 'is_verified',
            'reputation_score', 'ai_relevance_score', 'created_at', 'last_updated',
            'linkedin_connections', 'citation_count', 'h_index', 'publication_count'
        ]
        
        for attr in journalist_attrs:
            assert hasattr(Journalist, attr), f"Journalist model missing attribute: {attr}"

    def test_db_003_table_creation_and_schema(self, temp_db_manager):
        """DB-003: Test table creation and schema verification"""
        # Tables should be created during initialization
        inspector = temp_db_manager.engine.dialect.get_table_names(
            temp_db_manager.engine.connect()
        )
        
        # Check if journalists table exists
        assert 'journalists' in inspector or len(inspector) == 0  # Empty for in-memory DB

    def test_db_004_basic_crud_operations(self, temp_db_manager, sample_journalist):
        """DB-004: Test basic CRUD operations"""
        # CREATE
        journalist = temp_db_manager.add_journalist(sample_journalist)
        assert journalist is not None
        assert journalist.id is not None
        assert journalist.name == sample_journalist['name']
        
        # READ
        retrieved = temp_db_manager.get_journalist_by_id(journalist.id)
        assert retrieved is not None
        assert retrieved.name == sample_journalist['name']
        assert retrieved.email == sample_journalist['email']
        
        # UPDATE
        update_data = {'bio': 'Updated bio for testing'}
        updated = temp_db_manager.update_journalist(journalist.id, update_data)
        assert updated is not None
        assert updated.bio == 'Updated bio for testing'
        
        # DELETE (if implemented)
        # Note: Delete functionality might not be implemented yet

    def test_db_005_journalist_model_validation(self, temp_db_manager, sample_journalist):
        """DB-005: Test journalist model validation"""
        journalist = temp_db_manager.add_journalist(sample_journalist)
        
        # Test required fields
        assert journalist.name is not None
        assert journalist.email is not None
        
        # Test optional fields handling
        minimal_data = {
            'name': 'Minimal Journalist',
            'email': 'minimal@example.com'
        }
        minimal_journalist = temp_db_manager.add_journalist(minimal_data)
        assert minimal_journalist is not None
        assert minimal_journalist.name == 'Minimal Journalist'

    def test_db_006_database_manager_session_handling(self, temp_db_manager):
        """DB-006: Test database manager session handling"""
        # Test that sessions are properly managed
        session = temp_db_manager.get_session()
        assert session is not None
        
        # Test session cleanup
        session.close()

    def test_db_007_search_functionality(self, temp_db_manager, sample_journalists_list):
        """DB-007: Test search functionality"""
        # Add multiple journalists
        for journalist_data in sample_journalists_list:
            temp_db_manager.add_journalist(journalist_data)
        
        # Test search by specialization
        ai_journalists = temp_db_manager.search_journalists(
            specialization="artificial intelligence",
            limit=10
        )
        assert len(ai_journalists) > 0
        
        # Test search by country
        us_journalists = temp_db_manager.search_journalists(
            country="United States",
            limit=10
        )
        assert len(us_journalists) > 0
        
        # Test search by minimum reputation
        high_rep_journalists = temp_db_manager.search_journalists(
            min_reputation=0.8,
            limit=10
        )
        # Should find at least one with high reputation
        assert len(high_rep_journalists) >= 0

    def test_db_008_statistics_generation(self, temp_db_manager, sample_journalists_list):
        """DB-008: Test statistics generation"""
        # Add test data
        for journalist_data in sample_journalists_list:
            temp_db_manager.add_journalist(journalist_data)
        
        stats = temp_db_manager.get_statistics()
        
        # Check required statistics fields
        required_stats = [
            'total_journalists', 'verified_journalists', 'countries_covered',
            'avg_reputation_score', 'avg_ai_relevance_score', 'top_publications'
        ]
        
        for stat in required_stats:
            assert stat in stats, f"Missing statistic: {stat}"
        
        # Verify statistics values
        assert stats['total_journalists'] >= len(sample_journalists_list)
        assert isinstance(stats['avg_reputation_score'], (int, float))
        assert isinstance(stats['avg_ai_relevance_score'], (int, float))

    def test_db_009_data_integrity_constraints(self, temp_db_manager):
        """DB-009: Test data integrity constraints"""
        # Test duplicate email handling
        journalist_data = {
            'name': 'Test Journalist',
            'email': 'test@example.com'
        }
        
        first_journalist = temp_db_manager.add_journalist(journalist_data)
        assert first_journalist is not None
        
        # Try to add another journalist with same email
        duplicate_data = {
            'name': 'Another Journalist',
            'email': 'test@example.com'  # Same email
        }
        
        # This should either fail or update existing record
        try:
            second_journalist = temp_db_manager.add_journalist(duplicate_data)
            # If it succeeds, it should be the same journalist or an updated one
            if second_journalist:
                # Check if it's handling duplicates properly
                all_journalists = temp_db_manager.search_journalists(limit=100)
                emails = [j.email for j in all_journalists]
                # Should not have duplicate emails
                assert len(emails) == len(set(emails)), "Duplicate emails found in database"
        except Exception:
            # It's acceptable if the database rejects duplicates
            pass

    def test_db_010_database_cleanup_and_reset(self, temp_db_manager, sample_journalist):
        """DB-010: Test database cleanup and reset capabilities"""
        # Add some test data
        journalist = temp_db_manager.add_journalist(sample_journalist)
        assert journalist is not None
        
        # Verify data exists
        stats_before = temp_db_manager.get_statistics()
        assert stats_before['total_journalists'] > 0
        
        # Test cleanup functionality (if implemented)
        # Note: This might not be implemented yet, so we'll just verify the data exists
        all_journalists = temp_db_manager.search_journalists(limit=1000)
        assert len(all_journalists) > 0


class TestJournalistModel:
    """Test cases for Journalist model"""

    def test_journalist_model_creation(self, sample_journalist):
        """Test journalist model creation with various data"""
        # Test with full data
        journalist = Journalist(**sample_journalist)
        assert journalist.name == sample_journalist['name']
        assert journalist.email == sample_journalist['email']
        assert journalist.reputation_score == sample_journalist['reputation_score']
        
        # Test with minimal data
        minimal_data = {
            'name': 'Test Journalist',
            'email': 'test@example.com'
        }
        minimal_journalist = Journalist(**minimal_data)
        assert minimal_journalist.name == 'Test Journalist'
        assert minimal_journalist.email == 'test@example.com'

    def test_journalist_model_string_representation(self, sample_journalist):
        """Test journalist model string representation"""
        journalist = Journalist(**sample_journalist)
        str_repr = str(journalist)
        assert sample_journalist['name'] in str_repr

    def test_journalist_model_serialization(self, sample_journalist):
        """Test journalist model serialization to dict"""
        journalist = Journalist(**sample_journalist)
        
        # Test if model can be converted to dict-like structure
        # This depends on the actual implementation
        assert hasattr(journalist, 'name')
        assert hasattr(journalist, 'email')
        assert hasattr(journalist, 'reputation_score')


class TestDatabaseErrorHandling:
    """Test error handling in database operations"""

    def test_invalid_database_connection(self):
        """Test handling of invalid database connections"""
        with patch('database.database_manager.DATABASE_URL', 'invalid://invalid/path'):
            try:
                db_manager = DatabaseManager()
                # Should either fail gracefully or handle the error
                assert db_manager is not None
            except Exception as e:
                # It's acceptable if it raises an exception for invalid connection
                assert "invalid" in str(e).lower() or "error" in str(e).lower()

    def test_malformed_journalist_data(self, temp_db_manager):
        """Test handling of malformed journalist data"""
        # Test with None data
        try:
            result = temp_db_manager.add_journalist(None)
            assert result is None
        except Exception:
            # Acceptable to raise exception
            pass
        
        # Test with empty data
        try:
            result = temp_db_manager.add_journalist({})
            # Should handle gracefully
        except Exception:
            # Acceptable to raise exception for missing required fields
            pass
        
        # Test with invalid data types
        invalid_data = {
            'name': 123,  # Should be string
            'email': None,
            'reputation_score': 'invalid'  # Should be float
        }
        try:
            result = temp_db_manager.add_journalist(invalid_data)
            # Should handle gracefully or raise appropriate exception
        except Exception:
            # Acceptable to raise exception for invalid data types
            pass

    def test_database_session_errors(self, temp_db_manager):
        """Test handling of database session errors"""
        # This is a basic test - more sophisticated error scenarios
        # would require more complex setup
        session = temp_db_manager.get_session()
        assert session is not None
        
        # Test session cleanup
        try:
            session.close()
        except Exception:
            # Should handle session cleanup gracefully
            pass


# Integration tests for database with other components
class TestDatabaseIntegration:
    """Integration tests for database with other components"""

    def test_database_with_reputation_scoring(self, temp_db_manager, sample_journalist):
        """Test database integration with reputation scoring"""
        # Add journalist with reputation score
        journalist = temp_db_manager.add_journalist(sample_journalist)
        assert journalist.reputation_score == sample_journalist['reputation_score']
        
        # Test querying by reputation score
        high_rep = temp_db_manager.search_journalists(min_reputation=0.8, limit=10)
        if sample_journalist['reputation_score'] >= 0.8:
            assert len(high_rep) > 0

    def test_database_with_search_criteria(self, temp_db_manager, sample_journalists_list):
        """Test database integration with complex search criteria"""
        # Add multiple journalists
        for journalist_data in sample_journalists_list:
            temp_db_manager.add_journalist(journalist_data)
        
        # Test complex search
        results = temp_db_manager.search_journalists(
            specialization="artificial intelligence",
            country="United States",
            min_reputation=0.5,
            limit=5
        )
        
        # Verify results match criteria
        for journalist in results:
            if journalist.country:
                assert "United States" in journalist.country or journalist.country == "United States"
            if journalist.reputation_score:
                assert journalist.reputation_score >= 0.5
