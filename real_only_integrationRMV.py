# real_only_integration.py
"""
Integration code to update your existing files for real-only article fetching.
Copy these changes to your existing files.
"""

# ===== 1. UPDATE api/articles.py =====
# Replace the fetch_task function in @router.post("/fetch"):

def fetch_task():
    """Fetch real articles only - no demo content"""
    from services.real_only_aggregator import RealOnlyAggregator
    
    aggregator = RealOnlyAggregator()
    count = aggregator.run_real_only_aggregation()
    logger.info(f"Background fetch completed: {count} real articles")

# ===== 2. ADD TO main.py =====
# Add these new endpoints to main.py:

@app.get("/clear-demo")
async def clear_demo_articles():
    """Clear all demo articles from database"""
    from services.real_only_aggregator import RealOnlyAggregator
    
    aggregator = RealOnlyAggregator()
    cleared_count = aggregator.clear_demo_articles()
    
    return {"message": f"Cleared {cleared_count} demo articles"}

@app.get("/real-only-fetch")
async def real_only_fetch():
    """Fetch ONLY real articles from RSS sources"""
    from services.real_only_aggregator import RealOnlyAggregator
    
    aggregator = RealOnlyAggregator()
    count = aggregator.run_real_only_aggregation()
    
    return {"message": f"Fetched {count} real articles", "demo_articles": 0}

@app.get("/debug/real-stats")
async def real_article_stats():
    """Get statistics about real vs demo articles"""
    from services.real_only_aggregator import RealOnlyAggregator
    
    aggregator = RealOnlyAggregator()
    stats = aggregator.get_real_article_statistics()
    
    return stats

@app.get("/articles/real-only")
async def real_articles_only(request: Request, db: Session = Depends(get_db)):
    """Show only real articles (no demo content)"""
    
    # Get only real articles
    real_articles = (
        db.query(Article)
        .filter(~Article.title.like('[DEMO]%'))
        .filter(~Article.title.like('%DEMO%'))
        .filter(~Article.source.like('%Demo%'))
        .order_by(Article.created_at.desc())
        .limit(50)
        .all()
    )
    
    return templates.TemplateResponse(
        "articles.html",
        {
            "request": request,
            "articles": real_articles,
            "selected_industry": None,
            "selected_impact": None,
            "industries": [e.value for e in Industry],
            "impact_levels": [e.value for e in ImpactLevel],
            "page_title": "Real Articles Only"
        }
    )

# ===== 3. SIMPLE SETUP SCRIPT =====

def setup_real_only_mode():
    """Simple script to set up real-only mode"""
    from services.real_only_aggregator import RealOnlyAggregator
    
    print("Setting up Real-Only Article Mode")
    print("=" * 40)
    
    aggregator = RealOnlyAggregator()
    
    # Step 1: Clear existing demo articles
    print("1. Clearing demo articles...")
    cleared = aggregator.clear_demo_articles()
    print(f"   Cleared {cleared} demo articles")
    
    # Step 2: Fetch real articles
    print("2. Fetching real articles...")
    count = aggregator.run_real_only_aggregation()
    print(f"   Fetched {count} real articles")
    
    # Step 3: Show statistics
    print("3. Final statistics:")
    stats = aggregator.get_real_article_statistics()
    print(f"   Total articles: {stats.get('total_articles', 0)}")
    print(f"   Real articles: {stats.get('real_articles', 0)}")
    print(f"   Real sources: {len(stats.get('real_sources', []))}")
    print(f"   Percentage real: {stats.get('percentage_real', 0):.1f}%")
    
    print("\n✅ Real-only mode setup complete!")
    print("Visit http://localhost:8000/articles/real-only to see only real articles")

if __name__ == "__main__":
    setup_real_only_mode()
