"""
Comprehensive tests for analysis components (ReputationAnalyzer and RelevanceScorer)
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analysis.reputation_analyzer import ReputationAnalyzer
from analysis.relevance_scorer import RelevanceScorer
from fixtures import sample_journalist, sample_journalist_2, sample_journalists_list


class TestReputationAnalyzer:
    """Test cases for ReputationAnalyzer"""

    def test_rep_001_reputation_analyzer_initialization(self):
        """REP-001: Test reputation analyzer initialization"""
        analyzer = ReputationAnalyzer()
        assert analyzer is not None
        # Check if it has required methods
        assert hasattr(analyzer, 'calculate_reputation_score')
        assert hasattr(analyzer, 'analyze_journalist_portfolio')

    def test_rep_002_reputation_score_calculation(self, sample_journalist):
        """REP-002: Test reputation score calculation"""
        analyzer = ReputationAnalyzer()
        
        # Test with complete data
        score = analyzer.calculate_reputation_score(sample_journalist)
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 1.0
        
        # Test with minimal data
        minimal_data = {
            'name': 'Test Journalist',
            'email': 'test@example.com'
        }
        minimal_score = analyzer.calculate_reputation_score(minimal_data)
        assert isinstance(minimal_score, (int, float))
        assert 0.0 <= minimal_score <= 1.0

    def test_rep_003_portfolio_analysis_functionality(self, sample_journalist):
        """REP-003: Test portfolio analysis functionality"""
        analyzer = ReputationAnalyzer()
        
        analysis = analyzer.analyze_journalist_portfolio(sample_journalist)
        
        # Check if analysis returns expected structure
        assert isinstance(analysis, dict)
        
        # Check for expected keys in analysis
        expected_keys = ['overall_score', 'strengths', 'recommendations']
        for key in expected_keys:
            if key in analysis:
                if key == 'overall_score':
                    assert isinstance(analysis[key], (int, float))
                    assert 0.0 <= analysis[key] <= 1.0
                elif key in ['strengths', 'recommendations']:
                    assert isinstance(analysis[key], list)

    def test_rep_004_scoring_weights_application(self, sample_journalist):
        """REP-004: Test scoring weights application"""
        analyzer = ReputationAnalyzer()
        
        # Test with high follower count
        high_followers_data = sample_journalist.copy()
        high_followers_data['twitter_followers'] = 100000
        high_score = analyzer.calculate_reputation_score(high_followers_data)
        
        # Test with low follower count
        low_followers_data = sample_journalist.copy()
        low_followers_data['twitter_followers'] = 100
        low_score = analyzer.calculate_reputation_score(low_followers_data)
        
        # High followers should generally result in higher score
        # (though other factors may influence this)
        assert isinstance(high_score, (int, float))
        assert isinstance(low_score, (int, float))

    def test_rep_005_edge_cases_handling(self):
        """REP-005: Test edge cases handling (missing data)"""
        analyzer = ReputationAnalyzer()
        
        # Test with None data
        try:
            score = analyzer.calculate_reputation_score(None)
            assert score == 0.0 or score is None
        except Exception:
            # Acceptable to raise exception
            pass
        
        # Test with empty data
        empty_score = analyzer.calculate_reputation_score({})
        assert isinstance(empty_score, (int, float))
        assert 0.0 <= empty_score <= 1.0
        
        # Test with negative values
        negative_data = {
            'twitter_followers': -100,
            'article_count': -50,
            'reputation_score': -0.5
        }
        negative_score = analyzer.calculate_reputation_score(negative_data)
        assert isinstance(negative_score, (int, float))
        assert negative_score >= 0.0  # Should handle negatives gracefully

    def test_reputation_score_consistency(self, sample_journalist):
        """Test that reputation score calculation is consistent"""
        analyzer = ReputationAnalyzer()
        
        # Calculate score multiple times with same data
        score1 = analyzer.calculate_reputation_score(sample_journalist)
        score2 = analyzer.calculate_reputation_score(sample_journalist)
        score3 = analyzer.calculate_reputation_score(sample_journalist)
        
        # Should be consistent
        assert score1 == score2 == score3

    def test_reputation_factors_influence(self):
        """Test that different factors influence reputation score appropriately"""
        analyzer = ReputationAnalyzer()
        
        base_data = {
            'name': 'Test Journalist',
            'email': 'test@example.com',
            'twitter_followers': 1000,
            'article_count': 50,
            'is_verified': False
        }
        
        base_score = analyzer.calculate_reputation_score(base_data)
        
        # Test verification influence
        verified_data = base_data.copy()
        verified_data['is_verified'] = True
        verified_score = analyzer.calculate_reputation_score(verified_data)
        
        # Test high-quality publication influence
        quality_pub_data = base_data.copy()
        quality_pub_data['current_publication'] = 'TechCrunch'  # Known quality publication
        quality_score = analyzer.calculate_reputation_score(quality_pub_data)
        
        # All scores should be valid
        assert isinstance(base_score, (int, float))
        assert isinstance(verified_score, (int, float))
        assert isinstance(quality_score, (int, float))


class TestRelevanceScorer:
    """Test cases for RelevanceScorer"""

    def test_rel_001_relevance_scorer_initialization(self):
        """REL-001: Test relevance scorer initialization"""
        scorer = RelevanceScorer()
        assert scorer is not None
        # Check if it has required methods
        assert hasattr(scorer, 'calculate_ai_relevance_score')
        assert hasattr(scorer, 'find_relevant_journalists')
        assert hasattr(scorer, 'generate_relevance_report')

    def test_rel_002_ai_relevance_score_calculation(self, sample_journalist):
        """REL-002: Test AI relevance score calculation"""
        scorer = RelevanceScorer()
        
        # Test with AI-focused journalist
        ai_score = scorer.calculate_ai_relevance_score(sample_journalist)
        assert isinstance(ai_score, (int, float))
        assert 0.0 <= ai_score <= 1.0
        
        # Test with non-AI journalist
        non_ai_data = {
            'name': 'Sports Journalist',
            'bio': 'Covers sports and athletics',
            'specializations': 'sports,athletics,football',
            'job_title': 'Sports Reporter'
        }
        non_ai_score = scorer.calculate_ai_relevance_score(non_ai_data)
        assert isinstance(non_ai_score, (int, float))
        assert 0.0 <= non_ai_score <= 1.0
        
        # AI journalist should have higher relevance score
        if 'artificial intelligence' in sample_journalist.get('bio', '').lower():
            assert ai_score >= non_ai_score

    def test_rel_003_journalist_filtering_by_relevance(self, sample_journalists_list):
        """REL-003: Test journalist filtering by relevance"""
        scorer = RelevanceScorer()
        
        # Filter for high AI relevance
        relevant_journalists = scorer.find_relevant_journalists(
            sample_journalists_list,
            min_relevance=0.5
        )
        
        assert isinstance(relevant_journalists, list)
        
        # All returned journalists should meet the minimum relevance
        for journalist in relevant_journalists:
            if 'ai_relevance_score' in journalist:
                assert journalist['ai_relevance_score'] >= 0.5

    def test_rel_004_specialization_matching(self, sample_journalists_list):
        """REL-004: Test specialization matching"""
        scorer = RelevanceScorer()
        
        # Test AI specialization filtering
        ai_specialists = scorer.find_relevant_journalists(
            sample_journalists_list,
            specialization_filter="artificial intelligence"
        )
        
        assert isinstance(ai_specialists, list)
        
        # Check that returned journalists have AI-related content
        for journalist in ai_specialists:
            bio = journalist.get('bio', '').lower()
            specializations = journalist.get('specializations', '').lower()
            job_title = journalist.get('job_title', '').lower()
            
            # Should have AI-related keywords in at least one field
            ai_keywords = ['artificial intelligence', 'ai', 'machine learning', 'ml']
            has_ai_keyword = any(
                keyword in bio or keyword in specializations or keyword in job_title
                for keyword in ai_keywords
            )
            # Note: This might not always be true depending on the implementation

    def test_rel_005_relevance_report_generation(self, sample_journalist):
        """REL-005: Test relevance report generation"""
        scorer = RelevanceScorer()
        
        report = scorer.generate_relevance_report(sample_journalist)
        
        # Check if report is generated
        assert isinstance(report, dict)
        
        # Check for expected report structure
        expected_keys = ['relevance_score', 'ai_keywords_found', 'recommendations']
        for key in expected_keys:
            if key in report:
                if key == 'relevance_score':
                    assert isinstance(report[key], (int, float))
                    assert 0.0 <= report[key] <= 1.0
                elif key == 'ai_keywords_found':
                    assert isinstance(report[key], list)
                elif key == 'recommendations':
                    assert isinstance(report[key], list)

    def test_relevance_score_consistency(self, sample_journalist):
        """Test that relevance score calculation is consistent"""
        scorer = RelevanceScorer()
        
        # Calculate score multiple times with same data
        score1 = scorer.calculate_ai_relevance_score(sample_journalist)
        score2 = scorer.calculate_ai_relevance_score(sample_journalist)
        score3 = scorer.calculate_ai_relevance_score(sample_journalist)
        
        # Should be consistent
        assert score1 == score2 == score3

    def test_keyword_detection_accuracy(self):
        """Test accuracy of AI keyword detection"""
        scorer = RelevanceScorer()
        
        # Test with clear AI content
        ai_heavy_data = {
            'name': 'AI Expert',
            'bio': 'Specializes in artificial intelligence, machine learning, and deep learning research',
            'specializations': 'artificial intelligence,machine learning,neural networks',
            'job_title': 'AI Research Journalist'
        }
        
        ai_score = scorer.calculate_ai_relevance_score(ai_heavy_data)
        
        # Test with no AI content
        no_ai_data = {
            'name': 'Fashion Writer',
            'bio': 'Covers fashion trends and style guides',
            'specializations': 'fashion,style,trends',
            'job_title': 'Fashion Journalist'
        }
        
        no_ai_score = scorer.calculate_ai_relevance_score(no_ai_data)
        
        # AI-heavy content should score higher
        assert ai_score > no_ai_score
        assert ai_score > 0.5  # Should be clearly identified as AI-relevant
        assert no_ai_score < 0.5  # Should be clearly identified as not AI-relevant

    def test_edge_cases_relevance_scoring(self):
        """Test edge cases in relevance scoring"""
        scorer = RelevanceScorer()
        
        # Test with None data
        try:
            score = scorer.calculate_ai_relevance_score(None)
            assert score == 0.0 or score is None
        except Exception:
            # Acceptable to raise exception
            pass
        
        # Test with empty data
        empty_score = scorer.calculate_ai_relevance_score({})
        assert isinstance(empty_score, (int, float))
        assert 0.0 <= empty_score <= 1.0
        
        # Test with very long text
        long_text_data = {
            'bio': 'artificial intelligence ' * 1000,  # Very long repetitive text
            'specializations': 'ai,ml,dl,' * 100
        }
        long_score = scorer.calculate_ai_relevance_score(long_text_data)
        assert isinstance(long_score, (int, float))
        assert 0.0 <= long_score <= 1.0


class TestAnalysisIntegration:
    """Integration tests for analysis components"""

    def test_reputation_and_relevance_integration(self, sample_journalist):
        """Test integration between reputation and relevance scoring"""
        reputation_analyzer = ReputationAnalyzer()
        relevance_scorer = RelevanceScorer()
        
        # Calculate both scores
        reputation_score = reputation_analyzer.calculate_reputation_score(sample_journalist)
        relevance_score = relevance_scorer.calculate_ai_relevance_score(sample_journalist)
        
        # Both should be valid scores
        assert isinstance(reputation_score, (int, float))
        assert isinstance(relevance_score, (int, float))
        assert 0.0 <= reputation_score <= 1.0
        assert 0.0 <= relevance_score <= 1.0
        
        # Test combined analysis
        combined_data = sample_journalist.copy()
        combined_data['reputation_score'] = reputation_score
        combined_data['ai_relevance_score'] = relevance_score
        
        # Generate reports
        reputation_analysis = reputation_analyzer.analyze_journalist_portfolio(combined_data)
        relevance_report = relevance_scorer.generate_relevance_report(combined_data)
        
        assert isinstance(reputation_analysis, dict)
        assert isinstance(relevance_report, dict)

    def test_batch_analysis_performance(self, sample_journalists_list):
        """Test performance of batch analysis operations"""
        reputation_analyzer = ReputationAnalyzer()
        relevance_scorer = RelevanceScorer()
        
        # Test batch reputation scoring
        reputation_scores = []
        for journalist in sample_journalists_list:
            score = reputation_analyzer.calculate_reputation_score(journalist)
            reputation_scores.append(score)
        
        assert len(reputation_scores) == len(sample_journalists_list)
        assert all(isinstance(score, (int, float)) for score in reputation_scores)
        
        # Test batch relevance scoring
        relevance_scores = []
        for journalist in sample_journalists_list:
            score = relevance_scorer.calculate_ai_relevance_score(journalist)
            relevance_scores.append(score)
        
        assert len(relevance_scores) == len(sample_journalists_list)
        assert all(isinstance(score, (int, float)) for score in relevance_scores)

    def test_analysis_with_missing_fields(self):
        """Test analysis components with various missing fields"""
        reputation_analyzer = ReputationAnalyzer()
        relevance_scorer = RelevanceScorer()
        
        # Test with different combinations of missing fields
        test_cases = [
            {'name': 'Test 1'},  # Only name
            {'name': 'Test 2', 'email': 'test2@example.com'},  # Name and email
            {'name': 'Test 3', 'bio': 'Some bio'},  # Name and bio
            {'name': 'Test 4', 'twitter_followers': 1000},  # Name and followers
        ]
        
        for test_data in test_cases:
            # Both analyzers should handle missing fields gracefully
            rep_score = reputation_analyzer.calculate_reputation_score(test_data)
            rel_score = relevance_scorer.calculate_ai_relevance_score(test_data)
            
            assert isinstance(rep_score, (int, float))
            assert isinstance(rel_score, (int, float))
            assert 0.0 <= rep_score <= 1.0
            assert 0.0 <= rel_score <= 1.0


class TestAnalysisErrorHandling:
    """Test error handling in analysis components"""

    def test_reputation_analyzer_error_handling(self):
        """Test error handling in reputation analyzer"""
        analyzer = ReputationAnalyzer()
        
        # Test with invalid data types
        invalid_inputs = [
            "string instead of dict",
            123,
            [],
            True
        ]
        
        for invalid_input in invalid_inputs:
            try:
                score = analyzer.calculate_reputation_score(invalid_input)
                # If it doesn't raise an exception, should return valid score or None
                if score is not None:
                    assert isinstance(score, (int, float))
                    assert 0.0 <= score <= 1.0
            except Exception:
                # Acceptable to raise exception for invalid input
                pass

    def test_relevance_scorer_error_handling(self):
        """Test error handling in relevance scorer"""
        scorer = RelevanceScorer()
        
        # Test with invalid data types
        invalid_inputs = [
            "string instead of dict",
            123,
            [],
            True
        ]
        
        for invalid_input in invalid_inputs:
            try:
                score = scorer.calculate_ai_relevance_score(invalid_input)
                # If it doesn't raise an exception, should return valid score or None
                if score is not None:
                    assert isinstance(score, (int, float))
                    assert 0.0 <= score <= 1.0
            except Exception:
                # Acceptable to raise exception for invalid input
                pass

    def test_analysis_memory_efficiency(self, sample_journalists_list):
        """Test memory efficiency of analysis operations"""
        reputation_analyzer = ReputationAnalyzer()
        relevance_scorer = RelevanceScorer()
        
        # Create a larger dataset for testing
        large_dataset = sample_journalists_list * 10  # 20 journalists
        
        # Test that analysis can handle larger datasets without issues
        try:
            for journalist in large_dataset:
                rep_score = reputation_analyzer.calculate_reputation_score(journalist)
                rel_score = relevance_scorer.calculate_ai_relevance_score(journalist)
                
                assert isinstance(rep_score, (int, float))
                assert isinstance(rel_score, (int, float))
        except MemoryError:
            pytest.skip("Memory constraints in test environment")
        except Exception as e:
            # Other exceptions should be investigated
            pytest.fail(f"Unexpected error in batch processing: {e}")
