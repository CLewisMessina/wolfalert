# services/enhanced_news_aggregator.py
"""
Enhanced news aggregation with multiple source types and intelligent filtering.
Single responsibility: Orchestrate the complete news aggregation pipeline.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
import requests
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.database import Article, SessionLocal
from services.source_manager import SourceManager, SourceType, SourceReliability
from services.content_filters import ContentFilter
from services.reddit_parser import RedditParser
from services.github_parser import GitHubParser
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNewsAggregator:
    """Enhanced news aggregation with intelligent filtering and multi-source support"""
    
    def __init__(self):
        self.source_manager = SourceManager()
        self.content_filter = ContentFilter()
        self.reddit_parser = RedditParser()
        self.github_parser = GitHubParser()
        
        # Configuration
        self.max_articles_per_source = 20
        self.min_content_score = 0.3
        self.request_timeout = 30
        
    def run_enhanced_aggregation(self, target_industries: Optional[List[str]] = None) -> int:
        """
        Run the complete enhanced aggregation pipeline.
        Returns: Number of articles saved
        """
        logger.info("Starting enhanced news aggregation...")
        
        all_articles = []
        
        # Get all sources
        sources = self.source_manager.get_all_sources()
        
        # Process each source type
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
                logger.info(f"  Collected {len(filtered_articles)} articles from {source_name}")
                
            except Exception as e:
                logger.error(f"Error processing {source_name}: {str(e)}")
                continue
        
        # Remove duplicates
        unique_articles = self._deduplicate_articles(all_articles)
        
        # Save to database
        saved_count = self._save_articles_to_db(unique_articles)
        
        logger.info(f"Enhanced aggregation complete: {saved_count} new articles from {len(sources)} sources")
        return saved_count
    
    def _fetch_rss_articles(self, source_config) -> List[Dict]:
        """Fetch articles from standard RSS feeds"""
        articles = []
        
        try:
            logger.debug(f"Fetching RSS from: {source_config.url}")
            
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'WolfAlert/1.0 (AI Business Intelligence Platform)'
            }
            
            # Parse RSS feed
            feed = feedparser.parse(source_config.url, 
                                  request_headers=headers)

            if feed.bozo and feed.bozo_exception:
                logger.warning(f"RSS parsing warning for {source_config.name}: {feed.bozo_exception}")
            
            # Process entries
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    article = {
                        'title': entry.title,
                        'content': self._extract_rss_content(entry),
                        'source': source_config.name,
                        'url': entry.link,
                        'published_date': self._parse_date(entry.get('published')),
                        'source_config': source_config
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.debug(f"Error processing RSS entry: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching RSS from {source_config.name}: {str(e)}")
            
        return articles
    
    def _fetch_reddit_articles(self, source_config) -> List[Dict]:
        """Fetch articles from Reddit RSS feeds"""
        articles = []
        
        try:
            feed = feedparser.parse(source_config.url)
            
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    # Use Reddit parser for specialized extraction
                    reddit_data = self.reddit_parser.extract_reddit_content(entry)
                    
                    if reddit_data and self.reddit_parser.filter_reddit_quality(reddit_data):
                        # Enhance with Reddit metadata
                        reddit_data = self.reddit_parser.enhance_reddit_metadata(reddit_data)
                        
                        # Convert to standard article format
                        article = {
                            'title': reddit_data['title'],
                            'content': reddit_data['content'],
                            'source': source_config.name,
                            'url': reddit_data['url'],
                            'published_date': reddit_data['published_date'],
                            'source_config': source_config,
                            'reddit_metadata': reddit_data
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logger.debug(f"Error processing Reddit entry: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching Reddit feed {source_config.name}: {str(e)}")
            
        return articles
    
    def _fetch_github_articles(self, source_config) -> List[Dict]:
        """Fetch articles from GitHub release feeds"""
        articles = []
        
        try:
            feed = feedparser.parse(source_config.url)
            
            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    # Use GitHub parser for specialized extraction
                    github_data = self.github_parser.extract_github_content(entry)
                    
                    if github_data and self.github_parser.filter_github_quality(github_data):
                        # Enhance with GitHub metadata
                        github_data = self.github_parser.enhance_github_metadata(github_data)
                        
                        # Convert to standard article format
                        article = {
                            'title': github_data['title'],
                            'content': github_data['content'],
                            'source': source_config.name,
                            'url': github_data['url'],
                            'published_date': github_data['published_date'],
                            'source_config': source_config,
                            'github_metadata': github_data
                        }
                        articles.append(article)
                        
                except Exception as e:
                    logger.debug(f"Error processing GitHub entry: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching GitHub feed {source_config.name}: {str(e)}")
            
        return articles
    
    def _extract_rss_content(self, entry) -> str:
        """Extract content from standard RSS entry"""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # Clean HTML if present
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
        
        return content[:2000]  # Limit content length
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_string:
            return datetime.now(timezone.utc)
        
        try:
            from dateutil import parser as date_parser
            return date_parser.parse(date_string)
        except:
            return datetime.now(timezone.utc)
    
    def _filter_and_enhance_articles(self, articles: List[Dict], 
                                   source_config, 
                                   target_industries: Optional[List[str]] = None) -> List[Dict]:
        """Filter articles for relevance and enhance with metadata"""
        filtered_articles = []
        
        for article in articles:
            try:
                title = article.get('title', '')
                content = article.get('content', '')
                
                # Calculate content score
                score_data = self.content_filter.calculate_content_score(
                    title, content, source_config.reliability.value, target_industries
                )
                
                # Check if article should be included
                if self.content_filter.should_include_content(
                    title, content, source_config.reliability.value, self.min_content_score
                ):
                    # Enhance article with analysis metadata
                    article['content_analysis'] = score_data
                    article['source_weight'] = source_config.weight
                    article['source_reliability'] = source_config.reliability.value
                    article['source_type'] = source_config.source_type.value
                    
                    # Add company context if available
                    if source_config.company:
                        article['company'] = source_config.company
                    
                    filtered_articles.append(article)
                    
            except Exception as e:
                logger.debug(f"Error filtering article: {str(e)}")
                continue
        
        return filtered_articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL and title similarity"""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()
            
            # Skip if URL already seen
            if url and url in seen_urls:
                continue
                
            # Skip if very similar title already seen
            title_words = set(title.split())
            is_duplicate = False
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                if len(title_words & seen_words) / max(len(title_words | seen_words), 1) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_articles.append(article)
        
        logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles
    
    def _save_articles_to_db(self, articles: List[Dict]) -> int:
        """Save articles to database"""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for article_data in articles:
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
            logger.info(f"Saved {saved_count} new articles to database")
            
        except Exception as e:
            logger.error(f"Error saving articles: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        return saved_count
    
    def get_aggregation_statistics(self) -> Dict:
        """Get statistics about the current aggregation setup"""
        source_stats = self.source_manager.get_source_statistics()
        
        return {
            "sources": source_stats,
            "configuration": {
                "max_articles_per_source": self.max_articles_per_source,
                "min_content_score": self.min_content_score,
                "request_timeout": self.request_timeout
            },
            "processors": {
                "reddit_parser": "enabled",
                "github_parser": "enabled", 
                "content_filter": "enabled"
            }
        }
    
    def test_source_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all configured sources"""
        results = {}
        sources = self.source_manager.get_all_sources()
        
        for source_name, source_config in sources.items():
            try:
                response = requests.head(source_config.url, timeout=10)
                results[source_name] = response.status_code == 200
            except Exception:
                results[source_name] = False
        
        return results
    
    def run_source_test(self, source_name: str, max_articles: int = 5) -> Dict:
        """Test a specific source and return sample articles"""
        source_config = self.source_manager.get_source_config(source_name)
        
        if not source_config:
            return {"error": f"Source {source_name} not found"}
        
        try:
            # Fetch sample articles
            if source_config.source_type == SourceType.COMMUNITY and "reddit" in source_name.lower():
                articles = self._fetch_reddit_articles(source_config)
            elif source_config.source_type == SourceType.PRODUCT_RELEASES:
                articles = self._fetch_github_articles(source_config)
            else:
                articles = self._fetch_rss_articles(source_config)
            
            # Limit and filter
            sample_articles = articles[:max_articles]
            filtered_articles = self._filter_and_enhance_articles(sample_articles, source_config)
            
            return {
                "source": source_name,
                "status": "success",
                "raw_articles": len(sample_articles),
                "filtered_articles": len(filtered_articles),
                "sample_titles": [article.get('title', '') for article in filtered_articles[:3]]
            }
            
        except Exception as e:
            return {
                "source": source_name,
                "status": "error",
                "error": str(e)
            }
    
    def create_demo_articles(self) -> int:
        """Create demo articles for presentation (enhanced version)"""
        demo_articles = [
            {
                'title': 'Anthropic Announces Claude for Financial Services',
                'content': 'Anthropic today announced Claude for Financial Services, a specialized version of its AI assistant designed specifically for the financial industry. The new offering includes enhanced compliance features, risk assessment capabilities, and integration with major banking platforms. Early adopters report 40% reduction in manual compliance tasks and improved fraud detection rates. The solution addresses key regulatory requirements including GDPR, SOX compliance, and financial data protection standards.',
                'source': 'Anthropic Press Release',
                'url': 'https://anthropic.com/news/claude-financial-services',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'Google Unveils AI-Powered Smart Grid Optimization Platform',
                'content': 'Google Cloud announced a new AI platform that optimizes electrical grid operations in real-time. The system uses machine learning to predict energy demand, optimize renewable energy integration, and prevent blackouts. Pilot programs with three major utilities showed 20% improvement in grid efficiency and 15% reduction in operational costs. The platform integrates with existing SCADA systems and supports both traditional and renewable energy sources including solar, wind, and battery storage.',
                'source': 'Google Cloud Blog',
                'url': 'https://cloud.google.com/blog/ai-smart-grid',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'EU Publishes Final AI Act Implementation Guidelines',
                'content': 'The European Union released detailed implementation guidelines for the AI Act, which takes effect in 2025. The guidelines specify requirements for high-risk AI systems, including those used in critical infrastructure, financial services, and healthcare. Companies have 12 months to ensure compliance or face penalties up to 7% of global revenue. Key requirements include algorithmic transparency, human oversight mechanisms, and regular bias testing for AI systems in regulated industries.',
                'source': 'EU AI Office',
                'url': 'https://eu.ai-act.com/implementation-guidelines',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'Microsoft Semantic Kernel v2.0 Released with Enterprise Features',
                'content': 'Microsoft released Semantic Kernel 2.0, adding enterprise-grade security, scalability improvements, and new orchestration capabilities for AI workflows. The update includes built-in compliance monitoring, audit trails, and integration with Azure Active Directory. New features support complex multi-agent workflows and improved integration with Microsoft 365 applications. Enterprise customers can now deploy AI agents with role-based access control and comprehensive logging.',
                'source': 'Microsoft Semantic Kernel',
                'url': 'https://github.com/microsoft/semantic-kernel/releases/tag/v2.0.0',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'OpenAI Introduces Function Calling for Healthcare Applications',
                'content': 'OpenAI announced specialized function calling capabilities for healthcare applications, enabling secure integration with electronic health records and medical databases. The new features include HIPAA-compliant data handling, medical terminology understanding, and integration with major EHR systems. Clinical trials show 35% improvement in diagnostic assistance accuracy and 50% reduction in administrative tasks for healthcare providers.',
                'source': 'OpenAI Blog',
                'url': 'https://openai.com/blog/healthcare-function-calling',
                'published_date': datetime.now(timezone.utc)
            }
        ]
        
        self._save_articles_to_db(demo_articles)
        return len(demo_articles)

if __name__ == "__main__":
    # Test the enhanced aggregator
    aggregator = EnhancedNewsAggregator()
    
    # Show statistics
    print("Aggregation Statistics:")
    stats = aggregator.get_aggregation_statistics()
    print(f"Total sources: {stats['sources']['total_sources']}")
    print(f"By type: {stats['sources']['by_type']}")
    print(f"By reliability: {stats['sources']['by_reliability']}")
    
    # Test connectivity
    print("\nTesting source connectivity...")
    connectivity = aggregator.test_source_connectivity()
    for source, status in connectivity.items():
        status_text = "✓" if status else "✗"
        print(f"  {status_text} {source}")
    
    # Run sample test
    print("\nTesting sample source...")
    test_result = aggregator.run_source_test("Google AI Blog")
    print(f"Test result: {test_result}")
    
    # Run full aggregation (commented out for testing)
    # count = aggregator.run_enhanced_aggregation()
    # print(f"Aggregated {count} articles")