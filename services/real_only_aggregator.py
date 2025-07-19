# services/real_only_aggregator.py
"""
Real-only news aggregation - no demo content, only live RSS feeds.
Single responsibility: Fetch ONLY real articles from live sources.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.enhanced_news_aggregator import EnhancedNewsAggregator
from services.source_manager import SourceManager, SourceType
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class RealOnlyAggregator(EnhancedNewsAggregator):
    """Enhanced aggregator that fetches ONLY real articles, no demo content"""
    
    def __init__(self):
        super().__init__()
        # Override demo creation to do nothing
        self._demo_mode = False
        
    def run_real_only_aggregation(self, target_industries: Optional[List[str]] = None) -> int:
        """
        Run aggregation with ONLY real RSS sources - no demo content.
        Returns: Number of real articles saved
        """
        logger.info("Starting REAL-ONLY news aggregation...")
        
        all_articles = []
        
        # Get all sources
        sources = self.source_manager.get_all_sources()
        
        # Process each source type (skip any demo-related sources)
        for source_name, source_config in sources.items():
            try:
                logger.info(f"Processing {source_name} ({source_config.source_type.value})")
                
                # Fetch articles based on source type
                if source_config.source_type == SourceType.COMMUNITY and "reddit" in source_name.lower():
                    articles = self._fetch_reddit_articles(source_config)
                elif source_config.source_type == SourceType.PRODUCT_RELEASES:
                    articles = self._fetch_github_articles(source_config)
                else:
                    articles = self._fetch_rss_articles(source_config)
                
                # Filter and enhance articles
                filtered_articles = self._filter_and_enhance_articles(
                    articles, source_config, target_industries
                )
                
                all_articles.extend(filtered_articles)
                logger.info(f"  Collected {len(filtered_articles)} real articles from {source_name}")
                
            except Exception as e:
                logger.error(f"Error processing {source_name}: {str(e)}")
                continue
        
        # Remove duplicates
        unique_articles = self._deduplicate_articles(all_articles)
        
        # Save ONLY real articles to database
        saved_count = self._save_real_articles_only(unique_articles)
        
        logger.info(f"Real-only aggregation complete: {saved_count} new articles from {len(sources)} sources")
        return saved_count
    
    def _save_real_articles_only(self, articles: List[Dict]) -> int:
        """Save only real articles to database (no demo content)"""
        from models.database import Article, SessionLocal
        
        db = SessionLocal()
        saved_count = 0
        
        try:
            for article_data in articles:
                # Skip any potential demo content
                title = article_data.get('title', '')
                source = article_data.get('source', '')
                
                # Skip demo articles
                if any(demo_indicator in title.lower() for demo_indicator in ['[demo]', 'demo:', 'demo article']):
                    continue
                    
                if any(demo_indicator in source.lower() for demo_indicator in ['demo', 'sample', 'test']):
                    continue
                
                # Check if article already exists
                existing = db.query(Article).filter(
                    Article.url == article_data.get('url')
                ).first()
                
                if existing:
                    continue
                
                # Create new article
                article = Article(
                    title=article_data.get('title', ''),
                    content=article_data.get('content', ''),
                    source=article_data.get('source', ''),
                    url=article_data.get('url', ''),
                    published_date=article_data.get('published_date'),
                    processed=False
                )
                
                db.add(article)
                saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} real articles to database")
            
        except Exception as e:
            logger.error(f"Error saving real articles: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        return saved_count
    
    def create_demo_articles(self) -> int:
        """Override to prevent demo article creation"""
        logger.info("Demo article creation disabled in real-only mode")
        return 0
    
    def clear_demo_articles(self) -> int:
        """Clear any existing demo articles from database"""
        from models.database import Article, SessionLocal
        
        db = SessionLocal()
        cleared_count = 0
        
        try:
            # Find and delete demo articles
            demo_articles = db.query(Article).filter(
                Article.title.like('[DEMO]%') |
                Article.title.like('%DEMO%') |
                Article.source.like('%Demo%') |
                Article.source.like('%Sample%')
            ).all()
            
            for article in demo_articles:
                db.delete(article)
                cleared_count += 1
            
            db.commit()
            logger.info(f"Cleared {cleared_count} demo articles")
            
        except Exception as e:
            logger.error(f"Error clearing demo articles: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        return cleared_count
    
    def get_real_article_statistics(self) -> Dict:
        """Get statistics about real articles only"""
        from models.database import Article, SessionLocal
        
        db = SessionLocal()
        
        try:
            # Count total articles
            total_articles = db.query(Article).count()
            
            # Count demo articles
            demo_articles = db.query(Article).filter(
                Article.title.like('[DEMO]%') |
                Article.title.like('%DEMO%') |
                Article.source.like('%Demo%')
            ).count()
            
            # Count real articles
            real_articles = total_articles - demo_articles
            
            # Get real article sources
            real_sources = db.query(Article.source).filter(
                ~Article.source.like('%Demo%')
            ).distinct().all()
            
            return {
                "total_articles": total_articles,
                "real_articles": real_articles,
                "demo_articles": demo_articles,
                "real_sources": [source[0] for source in real_sources if source[0]],
                "percentage_real": (real_articles / max(total_articles, 1)) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()

if __name__ == "__main__":
    # Test real-only aggregator
    aggregator = RealOnlyAggregator()
    
    print("Real-Only News Aggregator Test")
    print("=" * 40)
    
    # Show current statistics
    stats = aggregator.get_real_article_statistics()
    print(f"Current articles: {stats.get('total_articles', 0)}")
    print(f"Real articles: {stats.get('real_articles', 0)}")
    print(f"Demo articles: {stats.get('demo_articles', 0)}")
    
    # Test connectivity
    print("\nTesting source connectivity...")
    connectivity = aggregator.test_source_connectivity()
    working = sum(1 for status in connectivity.values() if status)
    print(f"Working sources: {working}/{len(connectivity)}")
    
    # Clear demo articles
    print(f"\nClearing demo articles...")
    cleared = aggregator.clear_demo_articles()
    print(f"Cleared {cleared} demo articles")
    
    # Run real aggregation
    print(f"\nRunning real-only aggregation...")
    count = aggregator.run_real_only_aggregation()
    print(f"Fetched {count} real articles")
    
    # Show final statistics
    final_stats = aggregator.get_real_article_statistics()
    print(f"\nFinal statistics:")
    print(f"Total articles: {final_stats.get('total_articles', 0)}")
    print(f"Real articles: {final_stats.get('real_articles', 0)}")
    print(f"Real sources: {len(final_stats.get('real_sources', []))}")
