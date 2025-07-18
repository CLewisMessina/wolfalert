# models/articles.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ImpactLevel(str, Enum):
    THREAT = "THREAT"
    OPPORTUNITY = "OPPORTUNITY"
    WATCH = "WATCH"
    NOISE = "NOISE"

class UrgencyLevel(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    SHORT_TERM = "SHORT_TERM"
    STRATEGIC = "STRATEGIC"

class Industry(str, Enum):
    UTILITIES = "utilities"
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    TECHNOLOGY = "technology"

# Pydantic models for API
class ArticleBase(BaseModel):
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassificationBase(BaseModel):
    industry: Industry
    impact_level: ImpactLevel
    urgency: UrgencyLevel
    relevance_score: float
    business_functions: Optional[List[str]] = []

class ClassificationCreate(ClassificationBase):
    article_id: int

class Classification(ClassificationBase):
    id: int
    article_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisBase(BaseModel):
    impact_summary: str
    action_recommendations: str
    competitive_implications: Optional[str] = None
    timeline_assessment: Optional[str] = None
    confidence_score: float

class AnalysisCreate(AnalysisBase):
    classification_id: int

class Analysis(AnalysisBase):
    id: int
    classification_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArticleWithAnalysis(Article):
    classifications: List[Classification] = []

class AlertSummary(BaseModel):
    total_articles: int
    threats: int
    opportunities: int
    watch_items: int
    noise: int
    industries_covered: List[str]
    latest_update: Optional[datetime] = None