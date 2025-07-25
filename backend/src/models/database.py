"""
Database models for WolfAlert application.
Single responsibility: Define all database table structures and relationships.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal as PythonDecimal
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, Index, ARRAY, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()

class UserProfile(Base):
    """User profile configurations for personalized AI analysis"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String(100), nullable=False)
    industry = Column(String(50), nullable=False)  # 'electric', 'broadband', etc.
    department = Column(String(50), nullable=False)  # 'engineering', 'marketing', etc.
    role_level = Column(String(30), nullable=False)  # 'individual', 'manager', etc.
    user_session_id = Column(String(100), nullable=True)  # Anonymous session tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    interactions = relationship("UserInteraction", back_populates="profile")
    reports = relationship("Report", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.profile_name}', industry='{self.industry}')>"


class Article(Base):
    """Articles fetched from RSS sources with lifecycle management"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    source_name = Column(String(100), nullable=False)
    source_reliability = Column(String(20), nullable=False)  # 'high', 'medium', 'community'
    published_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)  # Auto-cleanup after 30 days
    is_processed = Column(Boolean, default=False)
    processing_attempts = Column(Integer, default=0)
    
    # Relationships
    insights = relationship("ArticleInsight", back_populates="article")
    interactions = relationship("UserInteraction", back_populates="article")
    
    # Indexes
    __table_args__ = (
        Index('idx_article_processed', 'is_processed'),
        Index('idx_article_expires', 'expires_at'),
        Index('idx_article_published', 'published_at'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source='{self.source_name}')>"


class ArticleInsight(Base):
    """AI-generated profile-specific insights for articles"""
    __tablename__ = "article_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    profile_hash = Column(String(64), nullable=False)  # MD5 of industry+department+role
    summary = Column(Text, nullable=False)
    impact_reasoning = Column(Text, nullable=False)  # "Why this matters to you"
    impact_type = Column(String(20), nullable=False)  # 'threat', 'opportunity', 'watch'
    impact_score = Column(Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="insights")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_profile_score', 'profile_hash', 'impact_score'),
        Index('idx_article_profile', 'article_id', 'profile_hash'),
    )
    
    def __repr__(self):
        return f"<ArticleInsight(id={self.id}, score={self.impact_score}, type='{self.impact_type}')>"


class UserInteraction(Base):
    """User interactions for learning and analytics"""
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    action = Column(String(20), nullable=False)  # 'viewed', 'saved', 'dismissed', 'not_relevant'
    interaction_time = Column(DateTime, default=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="interactions")
    article = relationship("Article", back_populates="interactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_profile_interactions', 'profile_id', 'interaction_time'),
        Index('idx_article_interactions', 'article_id', 'action'),
    )
    
    def __repr__(self):
        return f"<UserInteraction(id={self.id}, action='{self.action}', profile_id={self.profile_id})>"


class Report(Base):
    """Generated reports for users"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # JSON of included articles and analysis
    generated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)  # Reports expire after 90 days
    
    # Relationships
    profile = relationship("UserProfile", back_populates="reports")
    
    # Indexes
    __table_args__ = (
        Index('idx_profile_reports', 'profile_id', 'generated_at'),
        Index('idx_report_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title}', profile_id={self.profile_id})>"


class RSSSource(Base):
    """RSS source configuration and metadata"""
    __tablename__ = "rss_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    url = Column(String(500), nullable=False, unique=True)
    source_type = Column(String(30), nullable=False)  # 'official_blog', 'news', etc.
    reliability = Column(String(20), nullable=False)  # 'high', 'medium', 'community'
    company = Column(String(100), nullable=True)
    industries = Column(ARRAY(String), nullable=False, default=[])
    weight = Column(Numeric(3, 2), default=1.0)
    is_active = Column(Boolean, default=True)
    last_fetched = Column(DateTime, nullable=True)
    fetch_frequency_hours = Column(Integer, default=4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_source_active', 'is_active'),
        Index('idx_source_fetch', 'last_fetched'),
    )
    
    def __repr__(self):
        return f"<RSSSource(id={self.id}, name='{self.name}', reliability='{self.reliability}')>"


# Database utility functions
def create_profile_hash(industry: str, department: str, role_level: str) -> str:
    """Create a hash for profile-specific insights"""
    import hashlib
    profile_string = f"{industry}:{department}:{role_level}"
    return hashlib.md5(profile_string.encode()).hexdigest()


def get_article_expiry_date(days: int = 30) -> datetime:
    """Calculate article expiry date"""
    return datetime.utcnow() + timedelta(days=days)


def get_report_expiry_date(days: int = 90) -> datetime:
    """Calculate report expiry date"""
    return datetime.utcnow() + timedelta(days=days)