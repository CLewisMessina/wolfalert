# api/articles.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db, Article, Classification
from models.articles import Article as ArticleSchema, ArticleCreate, ArticleWithAnalysis
from services.real_only_aggregator import RealOnlyAggregator
from typing import List, Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ArticleSchema])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    impact: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get articles with optional filtering"""
    
    query = db.query(Article)
    
    # Filter by industry or impact if provided
    if industry or impact:
        query = query.join(Classification)
        if industry:
            query = query.filter(Classification.industry == industry)
        if impact:
            query = query.filter(Classification.impact_level == impact)
    
    articles = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
    return articles

@router.get("/{article_id}", response_model=ArticleWithAnalysis)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get single article with classifications"""
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Get classifications for this article
    classifications = db.query(Classification).filter(Classification.article_id == article_id).all()
    
    # Convert to response model
    article_dict = {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "source": article.source,
        "url": article.url,
        "published_date": article.published_date,
        "processed": article.processed,
        "created_at": article.created_at,
        "classifications": classifications
    }
    
    return ArticleWithAnalysis(**article_dict)

@router.post("/", response_model=ArticleSchema)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """Create new article manually"""
    
    # Check if article already exists
    existing = db.query(Article).filter(Article.url == article.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Article with this URL already exists")
    
    db_article = Article(
        title=article.title,
        content=article.content,
        source=article.source,
        url=article.url,
        published_date=article.published_date,
        processed=False
    )
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    return db_article

@router.post("/fetch")
async def fetch_articles(background_tasks: BackgroundTasks):
    """Trigger article fetching from RSS sources"""
    
    def fetch_task():
        aggregator = RealOnlyAggregator()
        count = aggregator.run_real_only_aggregation()
        logger.info(f"Background fetch completed: {count} real articles")
    
    background_tasks.add_task(fetch_task)
    return {"message": "Article fetching started in background"}

@router.get("/stats/summary")
async def get_article_stats(db: Session = Depends(get_db)):
    """Get article statistics"""
    
    total = db.query(Article).count()
    processed = db.query(Article).filter(Article.processed == True).count()
    unprocessed = total - processed
    
    # Get source breakdown
    sources = db.query(Article.source).distinct().all()
    source_counts = {}
    for source in sources:
        if source[0]:  # Check if source is not None
            count = db.query(Article).filter(Article.source == source[0]).count()
            source_counts[source[0]] = count
    
    return {
        "total_articles": total,
        "processed": processed,
        "unprocessed": unprocessed,
        "sources": source_counts
    }