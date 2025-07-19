# services/source_manager.py
"""
Source configuration and categorization management.
Single responsibility: Manage all RSS source definitions and metadata.
"""
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SourceType(str, Enum):
    OFFICIAL_BLOG = "official_blog"
    COMMUNITY = "community" 
    RESEARCH = "research"
    PRODUCT_RELEASES = "product_releases"
    NEWS = "news"

class SourceReliability(str, Enum):
    HIGH = "high"           # Official company sources
    MEDIUM = "medium"       # Established tech blogs
    COMMUNITY = "community" # Reddit, HN - needs more filtering

class SourceConfig:
    """Configuration for a single RSS source"""
    
    def __init__(self, 
                 name: str, 
                 url: str, 
                 source_type: SourceType,
                 reliability: SourceReliability,
                 company: Optional[str] = None,
                 industries: Optional[List[str]] = None,
                 weight: float = 1.0):
        self.name = name
        self.url = url
        self.source_type = source_type
        self.reliability = reliability
        self.company = company
        self.industries = industries or []
        self.weight = weight

class SourceManager:
    """Manages all RSS source configurations and categorization"""
    
    def __init__(self):
        self.sources = self._initialize_sources()
        
    def _initialize_sources(self) -> Dict[str, SourceConfig]:
        """Initialize all RSS source configurations"""
        
        sources = {}
        
        # Original AI news sources
        original_sources = [
            SourceConfig(
                "TechCrunch AI", 
                "https://techcrunch.com/category/artificial-intelligence/feed/",
                SourceType.NEWS, 
                SourceReliability.MEDIUM,
                industries=["technology", "financial", "utilities"]
            ),
            SourceConfig(
                "VentureBeat AI",
                "https://venturebeat.com/ai/feed/",
                SourceType.NEWS,
                SourceReliability.MEDIUM,
                industries=["technology", "financial"]
            ),
            SourceConfig(
                "MIT Tech Review AI",
                "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                SourceType.RESEARCH,
                SourceReliability.HIGH,
                industries=["technology", "healthcare", "utilities"]
            ),
            SourceConfig(
                "AI News",
                "https://artificialintelligence-news.com/feed/",
                SourceType.NEWS,
                SourceReliability.MEDIUM
            )
        ]
        
        # Major platform official blogs
        platform_sources = [
            SourceConfig(
                "Google AI Blog",
                "https://blog.google/technology/ai/rss/",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Google",
                industries=["technology", "healthcare", "utilities"],
                weight=1.5
            ),
            SourceConfig(
                "Google Cloud Blog",
                "https://cloud.google.com/blog/rss/",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Google",
                industries=["utilities", "financial", "healthcare"],
                weight=1.5
            ),
            SourceConfig(
                "Microsoft Blog",
                "https://blogs.microsoft.com/feed/",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Microsoft",
                industries=["technology", "financial", "utilities"],
                weight=1.5
            ),
            SourceConfig(
                "AWS News Blog",
                "https://aws.amazon.com/blogs/aws/feed/",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Amazon",
                industries=["utilities", "financial", "technology"],
                weight=1.5
            ),
            SourceConfig(
                "Meta AI Blog",
                "https://ai.meta.com/feed.xml",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Meta",
                industries=["technology"],
                weight=1.3
            ),
            SourceConfig(
                "NVIDIA Blog",
                "https://blogs.nvidia.com/feed/",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="NVIDIA",
                industries=["utilities", "healthcare", "manufacturing"],
                weight=1.4
            ),
            SourceConfig(
                "Anthropic News",
                "https://www.anthropic.com/news/rss.xml",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="Anthropic",
                industries=["technology", "financial"],
                weight=1.3
            ),
            SourceConfig(
                "OpenAI Blog",
                "https://openai.com/blog/rss.xml",
                SourceType.OFFICIAL_BLOG,
                SourceReliability.HIGH,
                company="OpenAI",
                industries=["technology", "financial", "healthcare"],
                weight=1.5
            )
        ]
        
        # Community sources (Reddit RSS)
        community_sources = [
            SourceConfig(
                "Reddit MachineLearning",
                "https://www.reddit.com/r/MachineLearning/.rss",
                SourceType.COMMUNITY,
                SourceReliability.COMMUNITY,
                industries=["technology"],
                weight=0.8
            ),
            SourceConfig(
                "Reddit OpenAI",
                "https://www.reddit.com/r/OpenAI/.rss",
                SourceType.COMMUNITY,
                SourceReliability.COMMUNITY,
                industries=["technology"],
                weight=0.7
            ),
            SourceConfig(
                "Reddit LocalLLaMA",
                "https://www.reddit.com/r/LocalLLaMA/.rss",
                SourceType.COMMUNITY,
                SourceReliability.COMMUNITY,
                industries=["technology", "utilities"],
                weight=0.9
            ),
            SourceConfig(
                "Reddit Artificial",
                "https://www.reddit.com/r/artificial/.rss",
                SourceType.COMMUNITY,
                SourceReliability.COMMUNITY,
                weight=0.6
            )
        ]
        
        # GitHub product releases
        github_sources = [
            SourceConfig(
                "Microsoft Semantic Kernel",
                "https://github.com/microsoft/semantic-kernel/releases.atom",
                SourceType.PRODUCT_RELEASES,
                SourceReliability.HIGH,
                company="Microsoft",
                industries=["technology", "financial"]
            ),
            SourceConfig(
                "OpenAI Python SDK",
                "https://github.com/openai/openai-python/releases.atom",
                SourceType.PRODUCT_RELEASES,
                SourceReliability.HIGH,
                company="OpenAI",
                industries=["technology"]
            ),
            SourceConfig(
                "LangChain",
                "https://github.com/langchain-ai/langchain/releases.atom",
                SourceType.PRODUCT_RELEASES,
                SourceReliability.HIGH,
                industries=["technology"]
            ),
            SourceConfig(
                "Google Generative AI",
                "https://github.com/google/generative-ai-python/releases.atom",
                SourceType.PRODUCT_RELEASES,
                SourceReliability.HIGH,
                company="Google",
                industries=["technology"]
            )
        ]
        
        # Hacker News AI feed
        hn_sources = [
            SourceConfig(
                "Hacker News AI",
                "https://hnrss.org/newest?q=AI+OR+artificial+intelligence+OR+machine+learning",
                SourceType.COMMUNITY,
                SourceReliability.COMMUNITY,
                weight=0.7
            )
        ]
        
        # Combine all sources
        all_sources = (original_sources + platform_sources + 
                      community_sources + github_sources + hn_sources)
        
        for source in all_sources:
            sources[source.name] = source
            
        logger.info(f"Initialized {len(sources)} RSS sources")
        return sources
    
    def get_sources_by_type(self, source_type: SourceType) -> Dict[str, SourceConfig]:
        """Get all sources of a specific type"""
        return {name: config for name, config in self.sources.items() 
                if config.source_type == source_type}
    
    def get_sources_by_company(self, company: str) -> Dict[str, SourceConfig]:
        """Get all sources for a specific company"""
        return {name: config for name, config in self.sources.items() 
                if config.company and config.company.lower() == company.lower()}
    
    def get_sources_by_industry(self, industry: str) -> Dict[str, SourceConfig]:
        """Get all sources relevant to a specific industry"""
        return {name: config for name, config in self.sources.items() 
                if industry in config.industries}
    
    def get_high_reliability_sources(self) -> Dict[str, SourceConfig]:
        """Get only high reliability sources"""
        return {name: config for name, config in self.sources.items() 
                if config.reliability == SourceReliability.HIGH}
    
    def get_source_config(self, source_name: str) -> Optional[SourceConfig]:
        """Get configuration for a specific source"""
        return self.sources.get(source_name)
    
    def get_all_sources(self) -> Dict[str, SourceConfig]:
        """Get all configured sources"""
        return self.sources.copy()
    
    def add_custom_source(self, source_config: SourceConfig):
        """Add a custom source configuration"""
        self.sources[source_config.name] = source_config
        logger.info(f"Added custom source: {source_config.name}")
    
    def get_source_statistics(self) -> Dict:
        """Get statistics about configured sources"""
        stats = {
            "total_sources": len(self.sources),
            "by_type": {},
            "by_reliability": {},
            "by_company": {}
        }
        
        for source in self.sources.values():
            # Count by type
            type_key = source.source_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1
            
            # Count by reliability  
            reliability_key = source.reliability.value
            stats["by_reliability"][reliability_key] = stats["by_reliability"].get(reliability_key, 0) + 1
            
            # Count by company
            if source.company:
                company_key = source.company
                stats["by_company"][company_key] = stats["by_company"].get(company_key, 0) + 1
        
        return stats

if __name__ == "__main__":
    # Test the source manager
    manager = SourceManager()
    print("Source Statistics:")
    print(manager.get_source_statistics())
    
    print("\nHigh Reliability Sources:")
    for name in manager.get_high_reliability_sources():
        print(f"  - {name}")
