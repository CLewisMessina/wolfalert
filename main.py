# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import get_db, init_db, Article, Classification, Analysis
from models.articles import ArticleWithAnalysis, AlertSummary, ImpactLevel, Industry
from api import articles, analysis, reports
from dotenv import load_dotenv

load_dotenv()

# Initialize database
init_db()

app = FastAPI(
    title="WolfAlert",
    description="AI Business Intelligence for Strategic Decision Making",
    version="1.0.0"
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard page"""
    
    # Get summary statistics
    total_articles = db.query(Article).count()
    processed_articles = db.query(Article).filter(Article.processed == True).count()
    
    # Get impact level counts
    threats = db.query(Classification).filter(Classification.impact_level == ImpactLevel.THREAT).count()
    opportunities = db.query(Classification).filter(Classification.impact_level == ImpactLevel.OPPORTUNITY).count()
    watch_items = db.query(Classification).filter(Classification.impact_level == ImpactLevel.WATCH).count()
    noise = db.query(Classification).filter(Classification.impact_level == ImpactLevel.NOISE).count()
    
    # Get recent articles (show all articles, not just processed)
    recent_articles = (
        db.query(Article)
        .order_by(Article.created_at.desc())
        .limit(10)
        .all()
    )
    
    summary = AlertSummary(
        total_articles=total_articles,
        threats=threats,
        opportunities=opportunities,
        watch_items=watch_items,
        noise=noise,
        industries_covered=["utilities", "financial", "healthcare"],
        latest_update=recent_articles[0].created_at if recent_articles else None
    )
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "summary": summary,
            "recent_articles": recent_articles
        }
    )

@app.get("/articles", response_class=HTMLResponse)
async def articles_page(request: Request, industry: str = None, impact: str = None, db: Session = Depends(get_db)):
    """Articles listing page with filters"""
    
    query = db.query(Article)
    
    # Only filter by industry/impact if we have classifications
    if industry or impact:
        query = query.join(Classification, Article.id == Classification.article_id, isouter=True)
        if industry:
            query = query.filter(Classification.industry == industry)
        if impact:
            query = query.filter(Classification.impact_level == impact)
    
    articles = query.order_by(Article.created_at.desc()).all()
    
    return templates.TemplateResponse(
        "articles.html",
        {
            "request": request,
            "articles": articles,
            "selected_industry": industry,
            "selected_impact": impact,
            "industries": [e.value for e in Industry],
            "impact_levels": [e.value for e in ImpactLevel]
        }
    )

@app.get("/articles/{article_id}", response_class=HTMLResponse)
async def article_detail(request: Request, article_id: int, db: Session = Depends(get_db)):
    """Individual article detail page"""
    
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    classifications = db.query(Classification).filter(Classification.article_id == article_id).all()
    
    # Get analysis for each classification
    for classification in classifications:
        classification.analysis = db.query(Analysis).filter(Analysis.classification_id == classification.id).first()
    
    return templates.TemplateResponse(
        "article_detail.html",
        {
            "request": request,
            "article": article,
            "classifications": classifications
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "WolfAlert"}

@app.get("/debug/articles")
async def debug_articles(db: Session = Depends(get_db)):
    """Debug endpoint to see what articles exist"""
    articles = db.query(Article).all()
    return {
        "total_count": len(articles),
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "source": article.source,
                "processed": article.processed,
                "created_at": article.created_at.isoformat() if article.created_at else None
            }
            for article in articles
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)