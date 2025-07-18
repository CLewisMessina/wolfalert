# api/reports.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db, Article, Classification, Analysis
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_available_reports():
    """Get list of available report types"""
    
    return {
        "available_reports": [
            {
                "name": "weekly",
                "description": "Weekly AI intelligence digest",
                "endpoint": "/api/reports/weekly"
            },
            {
                "name": "industry",
                "description": "Industry-specific analysis",
                "endpoint": "/api/reports/industry/{industry_name}"
            },
            {
                "name": "summary",
                "description": "Executive summary report",
                "endpoint": "/api/reports/summary"
            }
        ]
    }

@router.get("/weekly")
async def generate_weekly_report(db: Session = Depends(get_db)):
    """Generate weekly intelligence report"""
    
    # Get articles from last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent_articles = (
        db.query(Article)
        .filter(Article.created_at >= week_ago)
        .order_by(Article.created_at.desc())
        .all()
    )
    
    return {
        "report_type": "weekly",
        "period": f"{week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        "articles_count": len(recent_articles),
        "summary": "Weekly report generation will be fully implemented on Day 5",
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "source": article.source,
                "created_at": article.created_at.isoformat()
            }
            for article in recent_articles[:10]  # Limit to 10 for demo
        ]
    }

@router.get("/industry/{industry_name}")
async def generate_industry_report(industry_name: str, db: Session = Depends(get_db)):
    """Generate industry-specific report"""
    
    return {
        "report_type": "industry",
        "industry": industry_name,
        "message": f"Industry-specific reports for {industry_name} will be implemented on Day 5",
        "features": [
            "Industry-relevant AI developments",
            "Competitive intelligence",
            "Actionable recommendations",
            "Risk assessment"
        ]
    }

@router.get("/summary")
async def generate_summary_report(db: Session = Depends(get_db)):
    """Generate executive summary report"""
    
    total_articles = db.query(Article).count()
    processed_articles = db.query(Article).filter(Article.processed == True).count()
    
    return {
        "report_type": "summary",
        "generated_at": datetime.now().isoformat(),
        "statistics": {
            "total_articles": total_articles,
            "processed_articles": processed_articles,
            "pending_analysis": total_articles - processed_articles
        },
        "message": "Full executive summary reports will be implemented on Day 5"
    }