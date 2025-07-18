# api/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db, Article, Classification, Analysis
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_analysis_summary(db: Session = Depends(get_db)):
    """Get analysis summary statistics"""
    
    total_classifications = db.query(Classification).count()
    total_analysis = db.query(Analysis).count()
    
    # Count by impact level
    threats = db.query(Classification).filter(Classification.impact_level == "THREAT").count()
    opportunities = db.query(Classification).filter(Classification.impact_level == "OPPORTUNITY").count()
    watch = db.query(Classification).filter(Classification.impact_level == "WATCH").count()
    noise = db.query(Classification).filter(Classification.impact_level == "NOISE").count()
    
    return {
        "total_classifications": total_classifications,
        "total_analysis": total_analysis,
        "impact_breakdown": {
            "threats": threats,
            "opportunities": opportunities,
            "watch": watch,
            "noise": noise
        }
    }

@router.post("/classify/{article_id}")
async def classify_article(article_id: int, db: Session = Depends(get_db)):
    """Classify an article (placeholder for Day 2)"""
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # TODO: Implement AI classification on Day 2
    return {
        "message": "Article classification will be implemented on Day 2",
        "article_id": article_id,
        "article_title": article.title
    }