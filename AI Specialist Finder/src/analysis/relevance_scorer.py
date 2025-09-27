"""
Relevance scorer for evaluating how relevant journalists are for AI/Programming topics
"""
import re
import math
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from textblob import TextBlob
import json

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import AI_KEYWORDS

class RelevanceScorer:
    """Scores journalists based on their relevance to AI and programming topics"""
    
    def __init__(self):
        """Initialize relevance scorer with AI/programming keywords and weights"""
        self.ai_keywords = self._build_keyword_weights()
        self.programming_languages = self._build_programming_languages()
        self.tech_companies = self._build_tech_companies()
        self.ai_concepts = self._build_ai_concepts()
    
    def _build_keyword_weights(self) -> Dict[str, float]:
        """Build weighted keyword dictionary for AI/programming relevance"""
        return {
            # Core AI terms (highest weight)
            'artificial intelligence': 1.0,
            'machine learning': 1.0,
            'deep learning': 0.95,
            'neural networks': 0.9,
            'natural language processing': 0.9,
            'computer vision': 0.9,
            'reinforcement learning': 0.85,
            
            # AI applications and concepts
            'automation': 0.7,
            'robotics': 0.75,
            'chatbot': 0.6,
            'algorithm': 0.65,
            'data science': 0.7,
            'big data': 0.6,
            'predictive analytics': 0.65,
            
            # Programming and software
            'programming': 0.8,
            'software development': 0.75,
            'coding': 0.7,
            'software engineering': 0.75,
            'web development': 0.6,
            'mobile development': 0.6,
            'devops': 0.65,
            
            # Tech industry terms
            'tech startup': 0.6,
            'silicon valley': 0.5,
            'innovation': 0.4,
            'digital transformation': 0.6,
            'cloud computing': 0.65,
            'cybersecurity': 0.7,
            'blockchain': 0.6,
            
            # General tech terms (lower weight)
            'technology': 0.3,
            'tech': 0.3,
            'digital': 0.25,
            'internet': 0.2,
            'software': 0.4
        }
    
    def _build_programming_languages(self) -> Dict[str, float]:
        """Build programming language weights"""
        return {
            'python': 0.9,  # High relevance for AI/ML
            'r': 0.8,       # Data science
            'julia': 0.8,   # Scientific computing
            'tensorflow': 0.95,
            'pytorch': 0.95,
            'scikit-learn': 0.9,
            'javascript': 0.6,
            'java': 0.6,
            'c++': 0.7,
            'scala': 0.7,
            'go': 0.6,
            'rust': 0.6,
            'swift': 0.5,
            'kotlin': 0.5,
            'sql': 0.5,
            'matlab': 0.7,
            'hadoop': 0.7,
            'spark': 0.8
        }
    
    def _build_tech_companies(self) -> Dict[str, float]:
        """Build tech company relevance weights"""
        return {
            # AI-focused companies
            'openai': 1.0,
            'deepmind': 1.0,
            'anthropic': 1.0,
            'nvidia': 0.9,
            
            # Big tech with AI focus
            'google': 0.8,
            'microsoft': 0.8,
            'amazon': 0.7,
            'meta': 0.7,
            'apple': 0.7,
            'tesla': 0.8,
            
            # Other tech companies
            'uber': 0.6,
            'airbnb': 0.5,
            'spotify': 0.5,
            'netflix': 0.6,
            'salesforce': 0.6,
            'oracle': 0.5,
            'ibm': 0.7,
            'intel': 0.7,
            'amd': 0.6
        }
    
    def _build_ai_concepts(self) -> Dict[str, float]:
        """Build AI concept weights"""
        return {
            'supervised learning': 0.9,
            'unsupervised learning': 0.9,
            'semi-supervised learning': 0.85,
            'transfer learning': 0.85,
            'generative ai': 0.95,
            'large language model': 0.95,
            'transformer': 0.9,
            'gpt': 0.9,
            'bert': 0.85,
            'convolutional neural network': 0.9,
            'recurrent neural network': 0.85,
            'gradient descent': 0.8,
            'backpropagation': 0.8,
            'feature engineering': 0.75,
            'model training': 0.8,
            'hyperparameter tuning': 0.75,
            'overfitting': 0.7,
            'cross-validation': 0.7,
            'ensemble methods': 0.75,
            'random forest': 0.7,
            'support vector machine': 0.7,
            'k-means clustering': 0.65,
            'decision tree': 0.6,
            'linear regression': 0.6,
            'logistic regression': 0.6
        }
    
    def calculate_ai_relevance_score(self, journalist_data: Dict[str, Any]) -> float:
        """Calculate comprehensive AI relevance score for a journalist"""
        try:
            # Combine all text sources
            text_sources = [
                journalist_data.get('bio', ''),
                journalist_data.get('job_title', ''),
                ' '.join(journalist_data.get('specializations', [])) if isinstance(journalist_data.get('specializations'), list) else journalist_data.get('specializations', ''),
                journalist_data.get('name', '')
            ]
            
            combined_text = ' '.join(filter(None, text_sources)).lower()
            
            if not combined_text.strip():
                return 0.0
            
            # Calculate different relevance components
            keyword_score = self._calculate_keyword_score(combined_text)
            programming_score = self._calculate_programming_score(combined_text)
            company_score = self._calculate_company_score(combined_text)
            concept_score = self._calculate_concept_score(combined_text)
            
            # Weight the different components
            weights = {
                'keywords': 0.4,
                'programming': 0.25,
                'companies': 0.2,
                'concepts': 0.15
            }
            
            final_score = (
                keyword_score * weights['keywords'] +
                programming_score * weights['programming'] +
                company_score * weights['companies'] +
                concept_score * weights['concepts']
            )
            
            # Apply bonus for explicit AI journalist mentions
            if self._is_explicit_ai_journalist(combined_text):
                final_score += 0.2
            
            # Normalize to 0-1 range
            final_score = min(max(final_score, 0.0), 1.0)
            
            logger.debug(f"AI relevance score: {final_score:.3f} for {journalist_data.get('name', 'Unknown')}")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating AI relevance score: {e}")
            return 0.0
    
    def _calculate_keyword_score(self, text: str) -> float:
        """Calculate score based on AI/tech keywords"""
        score = 0.0
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.0
        
        for keyword, weight in self.ai_keywords.items():
            # Count occurrences of keyword
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
            if count > 0:
                # Apply diminishing returns for multiple occurrences
                keyword_score = weight * (1 - math.exp(-count))
                score += keyword_score
        
        # Normalize by text length to prevent bias toward longer texts
        normalized_score = score / max(math.log(word_count + 1), 1)
        
        return min(normalized_score, 1.0)
    
    def _calculate_programming_score(self, text: str) -> float:
        """Calculate score based on programming languages and frameworks"""
        score = 0.0
        
        for language, weight in self.programming_languages.items():
            if re.search(r'\b' + re.escape(language) + r'\b', text, re.IGNORECASE):
                score += weight
        
        # Normalize (assume max 3 programming languages mentioned)
        return min(score / 3.0, 1.0)
    
    def _calculate_company_score(self, text: str) -> float:
        """Calculate score based on tech company mentions"""
        score = 0.0
        
        for company, weight in self.tech_companies.items():
            if re.search(r'\b' + re.escape(company) + r'\b', text, re.IGNORECASE):
                score += weight
        
        # Normalize (assume max 2 companies mentioned)
        return min(score / 2.0, 1.0)
    
    def _calculate_concept_score(self, text: str) -> float:
        """Calculate score based on AI concepts and techniques"""
        score = 0.0
        
        for concept, weight in self.ai_concepts.items():
            if re.search(r'\b' + re.escape(concept) + r'\b', text, re.IGNORECASE):
                score += weight
        
        # Normalize (assume max 5 concepts mentioned)
        return min(score / 5.0, 1.0)
    
    def _is_explicit_ai_journalist(self, text: str) -> bool:
        """Check if text explicitly mentions AI journalism"""
        explicit_patterns = [
            r'ai\s+journalist',
            r'artificial\s+intelligence\s+reporter',
            r'machine\s+learning\s+correspondent',
            r'tech\s+journalist.*ai',
            r'ai.*journalist',
            r'covers?\s+artificial\s+intelligence',
            r'specializes?\s+in\s+ai',
            r'focuses?\s+on\s+machine\s+learning'
        ]
        
        for pattern in explicit_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def analyze_content_relevance(self, content: str) -> Dict[str, Any]:
        """Analyze the relevance of article content or bio text"""
        try:
            content_lower = content.lower()
            
            analysis = {
                'overall_relevance': 0.0,
                'ai_keywords_found': [],
                'programming_languages_found': [],
                'tech_companies_found': [],
                'ai_concepts_found': [],
                'sentiment': 'neutral',
                'technical_depth': 'basic'
            }
            
            # Find AI keywords
            for keyword, weight in self.ai_keywords.items():
                if keyword in content_lower:
                    analysis['ai_keywords_found'].append({
                        'keyword': keyword,
                        'weight': weight,
                        'count': content_lower.count(keyword)
                    })
            
            # Find programming languages
            for lang, weight in self.programming_languages.items():
                if re.search(r'\b' + re.escape(lang) + r'\b', content_lower):
                    analysis['programming_languages_found'].append({
                        'language': lang,
                        'weight': weight
                    })
            
            # Find tech companies
            for company, weight in self.tech_companies.items():
                if re.search(r'\b' + re.escape(company) + r'\b', content_lower):
                    analysis['tech_companies_found'].append({
                        'company': company,
                        'weight': weight
                    })
            
            # Find AI concepts
            for concept, weight in self.ai_concepts.items():
                if concept in content_lower:
                    analysis['ai_concepts_found'].append({
                        'concept': concept,
                        'weight': weight
                    })
            
            # Calculate overall relevance
            total_weight = 0.0
            if analysis['ai_keywords_found']:
                total_weight += sum(item['weight'] for item in analysis['ai_keywords_found'])
            if analysis['programming_languages_found']:
                total_weight += sum(item['weight'] for item in analysis['programming_languages_found'])
            if analysis['tech_companies_found']:
                total_weight += sum(item['weight'] for item in analysis['tech_companies_found'])
            if analysis['ai_concepts_found']:
                total_weight += sum(item['weight'] for item in analysis['ai_concepts_found'])
            
            analysis['overall_relevance'] = min(total_weight / 5.0, 1.0)  # Normalize
            
            # Analyze sentiment using TextBlob
            try:
                blob = TextBlob(content)
                sentiment_score = blob.sentiment.polarity
                if sentiment_score > 0.1:
                    analysis['sentiment'] = 'positive'
                elif sentiment_score < -0.1:
                    analysis['sentiment'] = 'negative'
                else:
                    analysis['sentiment'] = 'neutral'
            except:
                analysis['sentiment'] = 'neutral'
            
            # Determine technical depth
            technical_terms = len(analysis['ai_concepts_found']) + len(analysis['programming_languages_found'])
            if technical_terms >= 5:
                analysis['technical_depth'] = 'expert'
            elif technical_terms >= 3:
                analysis['technical_depth'] = 'intermediate'
            elif technical_terms >= 1:
                analysis['technical_depth'] = 'basic'
            else:
                analysis['technical_depth'] = 'minimal'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content relevance: {e}")
            return {'overall_relevance': 0.0, 'error': str(e)}
    
    def score_journalist_articles(self, articles: List[Dict[str, Any]]) -> float:
        """Score journalist based on their published articles"""
        if not articles:
            return 0.0
        
        total_relevance = 0.0
        article_count = len(articles)
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            
            # Combine title and content for analysis
            combined_text = f"{title} {content}"
            
            # Analyze article relevance
            article_analysis = self.analyze_content_relevance(combined_text)
            article_relevance = article_analysis.get('overall_relevance', 0.0)
            
            # Weight recent articles higher
            publication_date = article.get('publication_date')
            recency_weight = self._calculate_recency_weight(publication_date)
            
            weighted_relevance = article_relevance * recency_weight
            total_relevance += weighted_relevance
        
        # Average relevance across all articles
        average_relevance = total_relevance / article_count
        
        # Apply bonus for high article count
        volume_bonus = min(article_count / 50.0, 0.2)  # Max 20% bonus
        
        final_score = min(average_relevance + volume_bonus, 1.0)
        
        return final_score
    
    def _calculate_recency_weight(self, publication_date) -> float:
        """Calculate weight based on article recency"""
        if not publication_date:
            return 0.5  # Default weight for unknown dates
        
        try:
            from datetime import datetime, timedelta
            
            if isinstance(publication_date, str):
                # Try to parse date string
                pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            else:
                pub_date = publication_date
            
            now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
            days_ago = (now - pub_date).days
            
            # Weight decreases with age
            if days_ago <= 30:
                return 1.0
            elif days_ago <= 90:
                return 0.9
            elif days_ago <= 180:
                return 0.8
            elif days_ago <= 365:
                return 0.7
            elif days_ago <= 730:
                return 0.6
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def find_relevant_journalists(self, 
                                journalists: List[Dict[str, Any]], 
                                min_relevance: float = 0.5,
                                specialization_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find journalists that meet relevance criteria"""
        relevant_journalists = []
        
        for journalist in journalists:
            # Calculate relevance score if not already present
            if 'ai_relevance_score' not in journalist:
                journalist['ai_relevance_score'] = self.calculate_ai_relevance_score(journalist)
            
            relevance_score = journalist.get('ai_relevance_score', 0.0)
            
            # Check minimum relevance threshold
            if relevance_score < min_relevance:
                continue
            
            # Apply specialization filter if specified
            if specialization_filter:
                specializations = journalist.get('specializations', [])
                if isinstance(specializations, str):
                    try:
                        specializations = json.loads(specializations)
                    except:
                        specializations = [specializations]
                
                if not any(specialization_filter.lower() in spec.lower() for spec in specializations):
                    continue
            
            relevant_journalists.append(journalist)
        
        # Sort by relevance score (descending)
        relevant_journalists.sort(key=lambda x: x.get('ai_relevance_score', 0), reverse=True)
        
        logger.info(f"Found {len(relevant_journalists)} relevant journalists (min_relevance: {min_relevance})")
        
        return relevant_journalists
    
    def generate_relevance_report(self, journalist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed relevance report for a journalist"""
        report = {
            'journalist_name': journalist_data.get('name', 'Unknown'),
            'overall_relevance_score': self.calculate_ai_relevance_score(journalist_data),
            'detailed_analysis': {},
            'recommendations': []
        }
        
        # Analyze bio/description
        bio = journalist_data.get('bio', '')
        if bio:
            report['detailed_analysis']['bio_analysis'] = self.analyze_content_relevance(bio)
        
        # Analyze specializations
        specializations = journalist_data.get('specializations', [])
        if isinstance(specializations, str):
            try:
                specializations = json.loads(specializations)
            except:
                specializations = [specializations]
        
        report['detailed_analysis']['specializations'] = specializations
        
        # Generate recommendations
        relevance_score = report['overall_relevance_score']
        
        if relevance_score >= 0.8:
            report['recommendations'].append('Excellent candidate for AI/tech interviews')
        elif relevance_score >= 0.6:
            report['recommendations'].append('Good candidate, verify specific AI expertise')
        elif relevance_score >= 0.4:
            report['recommendations'].append('Moderate relevance, may cover AI occasionally')
        else:
            report['recommendations'].append('Low AI relevance, consider other candidates')
        
        # Check for specific expertise gaps
        bio_analysis = report['detailed_analysis'].get('bio_analysis', {})
        if not bio_analysis.get('programming_languages_found'):
            report['recommendations'].append('No programming background evident')
        
        if not bio_analysis.get('ai_concepts_found'):
            report['recommendations'].append('Limited technical AI knowledge apparent')
        
        return report
