# services/news_aggregator.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from models.database import Article, SessionLocal
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAggregator:
    def __init__(self):
        self.rss_sources = {
            "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "VentureBeat AI": "https://venturebeat.com/ai/feed/",
            "MIT Tech Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
            "AI News": "https://artificialintelligence-news.com/feed/",
            "OpenAI Blog": "https://openai.com/blog/rss.xml",
            "Anthropic News": "https://www.anthropic.com/news/rss.xml"
        }
        
        # Keywords that indicate AI/ML relevance
        self.ai_keywords = [
            "artificial intelligence", "machine learning", "AI", "ML", "neural network",
            "deep learning", "natural language", "computer vision", "automation",
            "chatbot", "LLM", "large language model", "GPT", "claude", "gemini",
            "algorithm", "data science", "predictive analytics", "smart", "intelligent"
        ]
        
        # Industry-specific keywords
        self.industry_keywords = {
            "utilities": [
                "energy", "power grid", "smart grid", "utility", "electricity",
                "renewable", "solar", "wind", "electric vehicle", "EV", "charging",
                "demand response", "load balancing", "outage", "infrastructure"
            ],
            "financial": [
                "fintech", "banking", "finance", "trading", "investment", "credit",
                "fraud detection", "risk management", "compliance", "cryptocurrency",
                "blockchain", "payment", "lending", "insurance"
            ],
            "healthcare": [
                "healthcare", "medical", "clinical", "diagnosis", "treatment",
                "patient", "hospital", "drug discovery", "pharmaceutical",
                "telemedicine", "health record", "medical imaging", "genomics"
            ]
        }

    def fetch_rss_articles(self, max_articles: int = 50) -> List[Dict]:
        """Fetch articles from RSS sources"""
        all_articles = []
        
        for source_name, rss_url in self.rss_sources.items():
            try:
                logger.info(f"Fetching from {source_name}: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:max_articles]:
                    if self.is_ai_relevant(entry.title + " " + entry.get('summary', '')):
                        article = {
                            'title': entry.title,
                            'content': self.extract_content(entry),
                            'source': source_name,
                            'url': entry.link,
                            'published_date': self.parse_date(entry.get('published'))
                        }
                        all_articles.append(article)
                        
            except Exception as e:
                logger.error(f"Error fetching from {source_name}: {str(e)}")
                continue
        
        logger.info(f"Fetched {len(all_articles)} AI-relevant articles")
        return all_articles

    def is_ai_relevant(self, text: str) -> bool:
        """Check if article content is AI-relevant"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.ai_keywords)

    def extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
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
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
        
        return content[:2000]  # Limit content length

    def parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_string:
            return datetime.now(timezone.utc)
        
        try:
            return date_parser.parse(date_string)
        except:
            return datetime.now(timezone.utc)

    def save_articles_to_db(self, articles: List[Dict]):
        """Save articles to database"""
        db = SessionLocal()
        saved_count = 0
        
        try:
            for article_data in articles:
                # Check if article already exists
                existing = db.query(Article).filter(Article.url == article_data['url']).first()
                if existing:
                    continue
                
                article = Article(
                    title=article_data['title'],
                    content=article_data['content'],
                    source=article_data['source'],
                    url=article_data['url'],
                    published_date=article_data['published_date'],
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

    def create_demo_articles(self):
        """Create demo articles for presentation"""
        demo_articles = [
            {
                'title': 'Anthropic Announces Claude for Financial Services',
                'content': 'Anthropic today announced Claude for Financial Services, a specialized version of its AI assistant designed specifically for the financial industry. The new offering includes enhanced compliance features, risk assessment capabilities, and integration with major banking platforms. Early adopters report 40% reduction in manual compliance tasks and improved fraud detection rates.',
                'source': 'Anthropic Press Release',
                'url': 'https://anthropic.com/news/claude-financial-services',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'Google Unveils AI-Powered Smart Grid Optimization Platform',
                'content': 'Google Cloud announced a new AI platform that optimizes electrical grid operations in real-time. The system uses machine learning to predict energy demand, optimize renewable energy integration, and prevent blackouts. Pilot programs with three major utilities showed 20% improvement in grid efficiency and 15% reduction in operational costs.',
                'source': 'Google Cloud Blog',
                'url': 'https://cloud.google.com/blog/ai-smart-grid',
                'published_date': datetime.now(timezone.utc)
            },
            {
                'title': 'EU Publishes Final AI Act Implementation Guidelines',
                'content': 'The European Union released detailed implementation guidelines for the AI Act, which takes effect in 2025. The guidelines specify requirements for high-risk AI systems, including those used in critical infrastructure, financial services, and healthcare. Companies have 12 months to ensure compliance or face penalties up to 7% of global revenue.',
                'source': 'EU AI Office',
                'url': 'https://eu.ai-act.com/implementation-guidelines',
                'published_date': datetime.now(timezone.utc)
            }
        ]
        
        self.save_articles_to_db(demo_articles)
        return len(demo_articles)

    def run_aggregation(self):
        """Main aggregation process"""
        logger.info("Starting news aggregation...")
        
        # Fetch from RSS sources
        articles = self.fetch_rss_articles()
        
        # Add demo articles for presentation
        demo_count = self.create_demo_articles()
        
        # Save to database
        saved_count = self.save_articles_to_db(articles)
        
        logger.info(f"Aggregation complete: {saved_count} new articles, {demo_count} demo articles")
        return saved_count + demo_count

if __name__ == "__main__":
    aggregator = NewsAggregator()
    aggregator.run_aggregation()