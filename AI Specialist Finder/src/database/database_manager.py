"""
Database manager for the Journalist Finder application
"""
import sqlite3
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
from loguru import logger
import json

from .models import Base, Journalist, Article, SearchQuery
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import DATABASE_URL

class DatabaseManager:
    """Manages database operations for the Journalist Finder application"""
    
    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize database connection and create tables"""
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def add_journalist(self, journalist_data: Dict[str, Any]) -> Optional[Journalist]:
        """Add a new journalist to the database or update existing one"""
        session = self.get_session()
        try:
            # Check if journalist already exists by email or name
            existing = None
            if journalist_data.get('email'):
                existing = session.query(Journalist).filter(Journalist.email == journalist_data.get('email')).first()
            if not existing and journalist_data.get('name'):
                existing = session.query(Journalist).filter(Journalist.name == journalist_data.get('name')).first()

            if existing:
                # Update existing journalist with new information
                logger.debug(f"Updating existing journalist: {journalist_data.get('name')}")

                # Convert specializations list to JSON string if needed
                if 'specializations' in journalist_data and isinstance(journalist_data['specializations'], list):
                    journalist_data['specializations'] = json.dumps(journalist_data['specializations'])

                # Update fields if they are not None and different
                for key, value in journalist_data.items():
                    if hasattr(existing, key) and value is not None:
                        current_value = getattr(existing, key)
                        if current_value is None or (isinstance(current_value, str) and current_value.strip() == ""):
                            setattr(existing, key, value)
                        elif key in ['reputation_score', 'ai_relevance_score'] and value > current_value:
                            # Update scores if new value is higher
                            setattr(existing, key, value)

                session.commit()
                session.refresh(existing)
                return existing

            # Convert specializations list to JSON string if needed
            if 'specializations' in journalist_data and isinstance(journalist_data['specializations'], list):
                journalist_data['specializations'] = json.dumps(journalist_data['specializations'])

            journalist = Journalist(**journalist_data)
            session.add(journalist)
            session.commit()
            session.refresh(journalist)

            logger.info(f"Added journalist: {journalist.name}")
            return journalist

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding/updating journalist: {e}")
            return None
        finally:
            session.close()
    
    def update_journalist(self, journalist_id: int, update_data: Dict[str, Any]) -> Optional[Journalist]:
        """Update an existing journalist"""
        session = self.get_session()
        try:
            journalist = session.query(Journalist).filter(Journalist.id == journalist_id).first()
            if not journalist:
                logger.warning(f"Journalist with ID {journalist_id} not found")
                return None
            
            # Convert specializations list to JSON string if needed
            if 'specializations' in update_data and isinstance(update_data['specializations'], list):
                update_data['specializations'] = json.dumps(update_data['specializations'])
            
            for key, value in update_data.items():
                if hasattr(journalist, key):
                    setattr(journalist, key, value)
            
            session.commit()
            session.refresh(journalist)
            logger.info(f"Updated journalist: {journalist.name}")
            return journalist
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating journalist: {e}")
            return None
        finally:
            session.close()
    
    def search_journalists(self, 
                          specialization: Optional[str] = None,
                          min_reputation: Optional[float] = None,
                          country: Optional[str] = None,
                          platform: Optional[str] = None,
                          limit: int = 50) -> List[Journalist]:
        """Search journalists based on criteria"""
        session = self.get_session()
        try:
            query = session.query(Journalist)
            
            # Apply filters
            if specialization:
                query = query.filter(Journalist.specializations.contains(specialization))
            
            if min_reputation:
                query = query.filter(Journalist.reputation_score >= min_reputation)
            
            if country:
                # Handle multiple countries separated by commas
                countries = [c.strip() for c in country.split(',')]
                if len(countries) == 1:
                    query = query.filter(Journalist.country == countries[0])
                else:
                    query = query.filter(Journalist.country.in_(countries))
            
            if platform:
                query = query.filter(Journalist.source_platform == platform)
            
            # Order by reputation score descending
            query = query.order_by(Journalist.reputation_score.desc())
            
            # Apply limit
            journalists = query.limit(limit).all()
            
            logger.info(f"Found {len(journalists)} journalists matching criteria")
            return journalists
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching journalists: {e}")
            return []
        finally:
            session.close()
    
    def add_article(self, article_data: Dict[str, Any]) -> Optional[Article]:
        """Add a new article to the database"""
        session = self.get_session()
        try:
            # Check if article already exists by URL
            existing = session.query(Article).filter(Article.url == article_data.get('url')).first()
            if existing:
                logger.warning(f"Article with URL {article_data.get('url')} already exists")
                return existing
            
            article = Article(**article_data)
            session.add(article)
            session.commit()
            session.refresh(article)
            
            logger.info(f"Added article: {article.title[:50]}...")
            return article
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error adding article: {e}")
            return None
        finally:
            session.close()
    
    def get_journalist_by_id(self, journalist_id: int) -> Optional[Journalist]:
        """Get a journalist by ID"""
        session = self.get_session()
        try:
            journalist = session.query(Journalist).filter(Journalist.id == journalist_id).first()
            return journalist
        except SQLAlchemyError as e:
            logger.error(f"Error getting journalist by ID: {e}")
            return None
        finally:
            session.close()
    
    def get_top_journalists(self, limit: int = 10) -> List[Journalist]:
        """Get top journalists by reputation score"""
        session = self.get_session()
        try:
            journalists = session.query(Journalist)\
                .order_by(Journalist.reputation_score.desc())\
                .limit(limit).all()
            return journalists
        except SQLAlchemyError as e:
            logger.error(f"Error getting top journalists: {e}")
            return []
        finally:
            session.close()
    
    def log_search_query(self, query_data: Dict[str, Any]) -> Optional[SearchQuery]:
        """Log a search query for analytics"""
        session = self.get_session()
        try:
            search_query = SearchQuery(**query_data)
            session.add(search_query)
            session.commit()
            session.refresh(search_query)
            return search_query
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error logging search query: {e}")
            return None
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            
            # Get top publications
            top_publications = session.query(Journalist.current_publication, func.count(Journalist.id))\
                .filter(Journalist.current_publication.isnot(None))\
                .group_by(Journalist.current_publication)\
                .order_by(func.count(Journalist.id).desc())\
                .limit(5).all()
            
            stats = {
                'total_journalists': session.query(Journalist).count(),
                'total_articles': session.query(Article).count(),
                'verified_journalists': session.query(Journalist).filter(Journalist.is_verified == True).count(),
                'avg_reputation_score': session.query(func.avg(Journalist.reputation_score)).filter(Journalist.reputation_score > 0).scalar() or 0,
                'avg_ai_relevance_score': session.query(func.avg(Journalist.ai_relevance_score)).filter(Journalist.ai_relevance_score > 0).scalar() or 0,
                'countries_covered': session.query(Journalist.country).distinct().count(),
                'platforms_used': session.query(Journalist.source_platform).distinct().count(),
                'top_publications': [pub[0] for pub in top_publications] if top_publications else []
            }
            return stats
        except SQLAlchemyError as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            session.close()
    
    def close(self):
        """Close database connections"""
        try:
            self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
