"""
Database models for the Journalist Finder application
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Journalist(Base):
    """Model for storing journalist information"""
    __tablename__ = 'journalists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    bio = Column(Text)
    
    # Professional Information
    current_publication = Column(String(255))
    job_title = Column(String(255))
    specializations = Column(Text)  # JSON string of specializations
    
    # Contact & Social Media
    twitter_handle = Column(String(100))
    linkedin_url = Column(String(500))
    website_url = Column(String(500))
    
    # Location Information
    country = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))
    
    # Reputation Metrics
    reputation_score = Column(Float, default=0.0)
    article_count = Column(Integer, default=0)
    twitter_followers = Column(Integer, default=0)
    linkedin_connections = Column(Integer, default=0)

    # Academic Metrics (for Google Scholar and ResearchGate)
    citation_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    publication_count = Column(Integer, default=0)
    
    # AI/Programming Relevance
    ai_relevance_score = Column(Float, default=0.0)
    programming_expertise = Column(Boolean, default=False)
    
    # Metadata
    source_platform = Column(String(50))  # twitter, linkedin, news_site
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Journalist(name='{self.name}', publication='{self.current_publication}')>"

class Article(Base):
    """Model for storing articles written by journalists"""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    journalist_id = Column(Integer, nullable=False)  # Foreign key to Journalist
    
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True)
    publication_date = Column(DateTime)
    publication_name = Column(String(255))
    
    # Content Analysis
    ai_keywords_count = Column(Integer, default=0)
    programming_keywords_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    
    # Engagement Metrics
    social_shares = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Metadata
    scraped_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Article(title='{self.title[:50]}...', journalist_id={self.journalist_id})>"

class SearchQuery(Base):
    """Model for tracking search queries and results"""
    __tablename__ = 'search_queries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    query_text = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)  # twitter, linkedin, news
    results_count = Column(Integer, default=0)
    
    # Query Parameters
    location_filter = Column(String(100))
    date_range = Column(String(50))
    min_reputation_score = Column(Float)
    
    # Execution Info
    executed_at = Column(DateTime, default=func.now())
    execution_time_seconds = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<SearchQuery(query='{self.query_text}', platform='{self.platform}')>"
