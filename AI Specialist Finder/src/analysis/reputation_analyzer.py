"""
Reputation analyzer for evaluating journalist credibility and influence
"""
import math
from typing import Dict, Any, List, Optional
from loguru import logger

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import REPUTATION_WEIGHTS

class ReputationAnalyzer:
    """Analyzes and scores journalist reputation based on various metrics"""
    
    def __init__(self):
        """Initialize reputation analyzer with scoring weights"""
        self.weights = REPUTATION_WEIGHTS
    
    def calculate_reputation_score(self, journalist_data: Dict[str, Any]) -> float:
        """Calculate overall reputation score for a journalist"""
        try:
            # Extract metrics with proper null handling
            article_count = journalist_data.get('article_count') or 0
            twitter_followers = journalist_data.get('twitter_followers') or 0
            linkedin_connections = journalist_data.get('linkedin_connections') or 0
            current_publication = journalist_data.get('current_publication', '')
            ai_relevance_score = journalist_data.get('ai_relevance_score') or 0
            is_verified = journalist_data.get('is_verified', False)

            # Extract academic metrics (for Google Scholar and ResearchGate)
            citation_count = journalist_data.get('citation_count') or 0
            h_index = journalist_data.get('h_index') or 0
            publication_count = journalist_data.get('publication_count') or 0
            source_platform = journalist_data.get('source_platform', '')

            # Calculate individual scores
            article_score = self._calculate_article_score(article_count)
            social_score = self._calculate_social_score(twitter_followers, linkedin_connections)
            engagement_score = self._calculate_engagement_score(journalist_data)
            publication_score = self._calculate_publication_quality_score(current_publication)
            expertise_score = self._calculate_expertise_score(ai_relevance_score, journalist_data)

            # Calculate academic score for researchers
            academic_score = self._calculate_academic_score(citation_count, h_index, publication_count, source_platform)

            # Apply verification bonus
            verification_bonus = 0.1 if is_verified else 0.0

            # Adjust weights based on platform type
            if source_platform in ['google_scholar', 'researchgate']:
                # For academic researchers, weight academic metrics more heavily
                reputation_score = (
                    academic_score * 0.6 +
                    publication_score * self.weights['publication_quality'] +
                    expertise_score * self.weights['expertise_relevance'] +
                    verification_bonus
                )
            else:
                # For traditional journalists, use original weighting
                reputation_score = (
                    article_score * self.weights['article_count'] +
                    social_score * self.weights['social_followers'] +
                    engagement_score * self.weights['engagement_rate'] +
                    publication_score * self.weights['publication_quality'] +
                    expertise_score * self.weights['expertise_relevance'] +
                    verification_bonus
                )

            # Normalize to 0-1 range
            final_score = min(max(reputation_score, 0.0), 1.0)

            logger.debug(f"Reputation score calculated: {final_score:.3f} for {journalist_data.get('name', 'Unknown')}")

            return final_score

        except Exception as e:
            logger.error(f"Error calculating reputation score: {e}")
            return 0.0
    
    def _calculate_article_score(self, article_count: int) -> float:
        """Calculate score based on number of articles published"""
        if article_count <= 0:
            return 0.0
        
        # Logarithmic scale to prevent extremely high article counts from dominating
        # Score ranges from 0 to 1, with diminishing returns
        max_articles = 1000  # Articles needed for maximum score
        score = math.log10(article_count + 1) / math.log10(max_articles + 1)
        
        return min(score, 1.0)
    
    def _calculate_social_score(self, twitter_followers: int, linkedin_connections: int) -> float:
        """Calculate score based on social media following"""
        # Combine Twitter and LinkedIn metrics
        total_social = twitter_followers + (linkedin_connections * 2)  # Weight LinkedIn higher
        
        if total_social <= 0:
            return 0.0
        
        # Logarithmic scale for social following
        max_social = 100000  # Followers needed for maximum score
        score = math.log10(total_social + 1) / math.log10(max_social + 1)
        
        return min(score, 1.0)
    
    def _calculate_engagement_score(self, journalist_data: Dict[str, Any]) -> float:
        """Calculate engagement score based on interaction metrics"""
        twitter_followers = journalist_data.get('twitter_followers', 0)
        
        # Simple engagement calculation (can be enhanced with actual engagement data)
        if twitter_followers <= 0:
            return 0.5  # Default score if no social data
        
        # Estimate engagement based on follower count and other factors
        # Higher follower counts typically have lower engagement rates
        if twitter_followers < 1000:
            base_engagement = 0.8
        elif twitter_followers < 10000:
            base_engagement = 0.6
        elif twitter_followers < 100000:
            base_engagement = 0.4
        else:
            base_engagement = 0.2
        
        # Adjust based on verification and publication quality
        is_verified = journalist_data.get('is_verified', False)
        publication = journalist_data.get('current_publication', '')
        
        if is_verified:
            base_engagement += 0.1
        
        if self._is_major_publication(publication):
            base_engagement += 0.1
        
        return min(base_engagement, 1.0)
    
    def _calculate_publication_quality_score(self, publication: str) -> float:
        """Calculate score based on publication quality and reputation"""
        if not publication:
            return 0.3  # Default score for unknown publication
        
        publication_lower = publication.lower()
        
        # Tier 1: Top-tier publications
        tier1_publications = [
            'new york times', 'wall street journal', 'washington post', 'reuters',
            'bloomberg', 'financial times', 'the guardian', 'bbc', 'cnn',
            'techcrunch', 'wired', 'ars technica', 'the verge'
        ]
        
        # Tier 2: Well-known publications
        tier2_publications = [
            'forbes', 'fortune', 'business insider', 'mashable', 'engadget',
            'zdnet', 'venturebeat', 'recode', 'axios', 'fast company',
            'mit technology review', 'ieee spectrum'
        ]
        
        # Tier 3: Specialized tech publications
        tier3_publications = [
            'techradar', 'computerworld', 'infoworld', 'network world',
            'security week', 'ai news', 'machine learning mastery'
        ]
        
        for pub in tier1_publications:
            if pub in publication_lower:
                return 1.0
        
        for pub in tier2_publications:
            if pub in publication_lower:
                return 0.8
        
        for pub in tier3_publications:
            if pub in publication_lower:
                return 0.6
        
        # Check for academic or research institutions
        academic_keywords = ['university', 'institute', 'research', 'academic']
        if any(keyword in publication_lower for keyword in academic_keywords):
            return 0.7
        
        # Default score for other publications
        return 0.4
    
    def _calculate_academic_score(self, citation_count: int, h_index: int, publication_count: int, source_platform: str) -> float:
        """Calculate academic reputation score based on scholarly metrics"""
        if citation_count == 0 and h_index == 0 and publication_count == 0:
            return 0.0

        # Citation score (logarithmic scale)
        citation_score = min(math.log10(max(citation_count, 1)) / math.log10(10000), 1.0)

        # H-index score (normalized)
        h_index_score = min(h_index / 50.0, 1.0)

        # Publication score (logarithmic scale)
        publication_score = min(math.log10(max(publication_count, 1)) / math.log10(500), 1.0)

        # Combine academic metrics
        academic_score = (
            citation_score * 0.5 +
            h_index_score * 0.3 +
            publication_score * 0.2
        )

        return min(academic_score, 1.0)

    def _calculate_expertise_score(self, ai_relevance_score: float, journalist_data: Dict[str, Any]) -> float:
        """Calculate score based on AI/programming expertise"""
        # Base score from AI relevance
        expertise_score = ai_relevance_score

        # Bonus for programming expertise
        programming_expertise = journalist_data.get('programming_expertise', False)
        if programming_expertise:
            expertise_score += 0.2

        # Bonus for relevant specializations
        specializations = journalist_data.get('specializations', [])
        if isinstance(specializations, str):
            try:
                import json
                specializations = json.loads(specializations)
            except:
                specializations = [specializations]

        high_value_specializations = [
            'artificial intelligence', 'machine learning', 'programming',
            'data science', 'cybersecurity', 'robotics'
        ]

        specialization_bonus = 0.0
        for spec in specializations:
            if spec.lower() in [s.lower() for s in high_value_specializations]:
                specialization_bonus += 0.1

        expertise_score += min(specialization_bonus, 0.3)  # Cap bonus at 0.3

        return min(expertise_score, 1.0)
    
    def _is_major_publication(self, publication: str) -> bool:
        """Check if publication is a major news outlet"""
        if not publication:
            return False
        
        major_publications = [
            'new york times', 'wall street journal', 'washington post', 'reuters',
            'bloomberg', 'financial times', 'the guardian', 'bbc', 'cnn',
            'techcrunch', 'wired', 'ars technica', 'the verge', 'forbes'
        ]
        
        publication_lower = publication.lower()
        return any(pub in publication_lower for pub in major_publications)
    
    def analyze_journalist_portfolio(self, journalist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed analysis of journalist's reputation factors"""
        analysis = {
            'overall_score': self.calculate_reputation_score(journalist_data),
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # Analyze individual components
        article_count = journalist_data.get('article_count', 0)
        twitter_followers = journalist_data.get('twitter_followers', 0)
        publication = journalist_data.get('current_publication', '')
        ai_relevance = journalist_data.get('ai_relevance_score', 0)
        
        # Identify strengths
        if article_count > 100:
            analysis['strengths'].append('High article output')
        
        if twitter_followers > 10000:
            analysis['strengths'].append('Strong social media presence')
        
        if self._is_major_publication(publication):
            analysis['strengths'].append('Works for reputable publication')
        
        if ai_relevance > 0.7:
            analysis['strengths'].append('Strong AI/tech expertise')
        
        # Identify weaknesses
        if article_count < 10:
            analysis['weaknesses'].append('Limited published work')
        
        if twitter_followers < 1000:
            analysis['weaknesses'].append('Small social media following')
        
        if not publication:
            analysis['weaknesses'].append('No clear publication affiliation')
        
        if ai_relevance < 0.3:
            analysis['weaknesses'].append('Limited AI/tech focus')
        
        # Generate recommendations
        if article_count < 50:
            analysis['recommendations'].append('Look for more published articles to verify expertise')
        
        if not journalist_data.get('email'):
            analysis['recommendations'].append('Find contact information for outreach')
        
        if ai_relevance < 0.5:
            analysis['recommendations'].append('Verify AI/tech specialization before interview')
        
        return analysis
    
    def rank_journalists(self, journalists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank journalists by reputation score"""
        try:
            # Calculate reputation scores for all journalists
            for journalist in journalists:
                if 'reputation_score' not in journalist:
                    journalist['reputation_score'] = self.calculate_reputation_score(journalist)
            
            # Sort by reputation score (descending)
            ranked_journalists = sorted(
                journalists,
                key=lambda x: x.get('reputation_score', 0),
                reverse=True
            )
            
            logger.info(f"Ranked {len(ranked_journalists)} journalists by reputation")
            
            return ranked_journalists
            
        except Exception as e:
            logger.error(f"Error ranking journalists: {e}")
            return journalists
    
    def get_top_journalists_by_criteria(self, 
                                      journalists: List[Dict[str, Any]], 
                                      min_reputation: float = 0.5,
                                      specialization: Optional[str] = None,
                                      publication_tier: Optional[int] = None) -> List[Dict[str, Any]]:
        """Filter and return top journalists based on specific criteria"""
        filtered_journalists = []
        
        for journalist in journalists:
            # Check minimum reputation
            reputation_score = journalist.get('reputation_score', 0)
            if reputation_score < min_reputation:
                continue
            
            # Check specialization
            if specialization:
                specializations = journalist.get('specializations', [])
                if isinstance(specializations, str):
                    try:
                        import json
                        specializations = json.loads(specializations)
                    except:
                        specializations = [specializations]
                
                if not any(specialization.lower() in spec.lower() for spec in specializations):
                    continue
            
            # Check publication tier
            if publication_tier:
                publication = journalist.get('current_publication', '')
                pub_score = self._calculate_publication_quality_score(publication)
                
                if publication_tier == 1 and pub_score < 0.9:
                    continue
                elif publication_tier == 2 and pub_score < 0.7:
                    continue
                elif publication_tier == 3 and pub_score < 0.5:
                    continue
            
            filtered_journalists.append(journalist)
        
        # Rank filtered results
        return self.rank_journalists(filtered_journalists)
