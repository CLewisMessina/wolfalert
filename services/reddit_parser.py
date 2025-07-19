# services/reddit_parser.py
"""
Reddit-specific content parsing and processing.
Single responsibility: Handle Reddit RSS feed parsing and content extraction.
"""
import re
from typing import Dict, Optional, List
from datetime import datetime, timezone
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)

class RedditParser:
    """Handles Reddit RSS feed parsing and content extraction"""
    
    def __init__(self):
        self.reddit_domains = [
            "reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com"
        ]
        
    def is_reddit_source(self, url: str) -> bool:
        """Check if URL is from Reddit"""
        return any(domain in url.lower() for domain in self.reddit_domains)
    
    def extract_reddit_content(self, entry) -> Dict:
        """
        Extract content from Reddit RSS entry.
        Reddit RSS entries have unique structure compared to blog posts.
        """
        try:
            # Extract basic information
            title = self._clean_reddit_title(entry.title)
            content = self._extract_reddit_description(entry)
            url = entry.link
            published_date = self._parse_reddit_date(entry.get('published'))
            
            # Extract Reddit-specific metadata
            subreddit = self._extract_subreddit(entry)
            author = self._extract_author(entry)
            upvotes = self._extract_upvotes(entry)
            comments_count = self._extract_comments_count(entry)
            
            # Determine post type
            post_type = self._determine_post_type(title, content, url)
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'published_date': published_date,
                'subreddit': subreddit,
                'author': author,
                'upvotes': upvotes,
                'comments_count': comments_count,
                'post_type': post_type,
                'is_reddit': True
            }
            
        except Exception as e:
            logger.error(f"Error extracting Reddit content: {str(e)}")
            return None
    
    def _clean_reddit_title(self, title: str) -> str:
        """Clean Reddit post title"""
        if not title:
            return ""
            
        # Remove common Reddit prefixes
        prefixes_to_remove = [
            r'^\[.*?\]\s*',  # Remove [tags]
            r'^r/\w+\s*[-:]\s*',  # Remove subreddit prefix
        ]
        
        cleaned_title = title
        for prefix in prefixes_to_remove:
            cleaned_title = re.sub(prefix, '', cleaned_title)
        
        return cleaned_title.strip()
    
    def _extract_reddit_description(self, entry) -> str:
        """Extract description/content from Reddit entry"""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if content:
            # Clean HTML and Reddit-specific formatting
            content = self._clean_reddit_html(content)
            
        return content[:1500]  # Limit content length for Reddit posts
    
    def _clean_reddit_html(self, html_content: str) -> str:
        """Clean HTML content from Reddit RSS"""
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove common Reddit HTML elements
            for element in soup.find_all(['a', 'span'], class_=lambda x: x and 'reddit' in x.lower()):
                element.decompose()
            
            # Extract text and clean up
            text = soup.get_text()
            
            # Remove Reddit-specific noise
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                
                # Skip Reddit metadata lines
                if any(skip_phrase in line.lower() for skip_phrase in [
                    'submitted by', 'comments', 'share', 'report',
                    '[link]', '[comments]', 'reddit.com'
                ]):
                    continue
                    
                if line and len(line) > 10:  # Keep substantial lines
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.warning(f"Error cleaning Reddit HTML: {str(e)}")
            return html_content
    
    def _extract_subreddit(self, entry) -> Optional[str]:
        """Extract subreddit name from entry"""
        try:
            if hasattr(entry, 'tags') and entry.tags:
                for tag in entry.tags:
                    if hasattr(tag, 'term') and tag.term.startswith('r/'):
                        return tag.term
            
            # Try to extract from link
            if hasattr(entry, 'link'):
                match = re.search(r'/r/([^/]+)/', entry.link)
                if match:
                    return f"r/{match.group(1)}"
                    
            return None
            
        except Exception:
            return None
    
    def _extract_author(self, entry) -> Optional[str]:
        """Extract author username from entry"""
        try:
            if hasattr(entry, 'author'):
                return entry.author
            elif hasattr(entry, 'author_detail') and hasattr(entry.author_detail, 'name'):
                return entry.author_detail.name
                
            # Try to extract from content
            if hasattr(entry, 'summary'):
                match = re.search(r'submitted by.*?/u/([^\s\]]+)', entry.summary)
                if match:
                    return f"u/{match.group(1)}"
                    
            return None
            
        except Exception:
            return None
    
    def _extract_upvotes(self, entry) -> Optional[int]:
        """Extract upvote count from entry (may not always be available)"""
        try:
            # Reddit RSS doesn't always include vote counts
            # This is a placeholder for potential future enhancement
            return None
        except Exception:
            return None
    
    def _extract_comments_count(self, entry) -> Optional[int]:
        """Extract comment count from entry"""
        try:
            if hasattr(entry, 'summary'):
                # Look for comment count patterns
                match = re.search(r'(\d+)\s+comments?', entry.summary.lower())
                if match:
                    return int(match.group(1))
                    
            return None
            
        except Exception:
            return None
    
    def _determine_post_type(self, title: str, content: str, url: str) -> str:
        """Determine the type of Reddit post"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Question posts
        if any(indicator in title_lower for indicator in ['?', 'how to', 'help', 'question']):
            return "question"
            
        # Discussion posts
        if any(indicator in title_lower for indicator in ['discussion', 'thoughts', 'opinion']):
            return "discussion"
            
        # News/article posts
        if any(indicator in content_lower for indicator in ['announced', 'released', 'launched']):
            return "news"
            
        # Link posts (external links)
        if url and not any(domain in url for domain in self.reddit_domains):
            return "link"
            
        # Tutorial/guide posts
        if any(indicator in title_lower for indicator in ['tutorial', 'guide', 'how to']):
            return "tutorial"
            
        return "general"
    
    def _parse_reddit_date(self, date_string: str) -> Optional[datetime]:
        """Parse Reddit date format"""
        if not date_string:
            return datetime.now(timezone.utc)
        
        try:
            return date_parser.parse(date_string)
        except Exception:
            return datetime.now(timezone.utc)
    
    def filter_reddit_quality(self, reddit_data: Dict) -> bool:
        """
        Filter Reddit posts for quality and relevance.
        Returns True if post should be included.
        """
        if not reddit_data:
            return False
            
        title = reddit_data.get('title', '')
        content = reddit_data.get('content', '')
        post_type = reddit_data.get('post_type', '')
        
        # Skip very short posts
        if len(title) < 10 or len(content) < 30:
            return False
            
        # Skip certain post types that are usually low quality
        skip_types = ['question']  # Questions are often too specific
        if post_type in skip_types:
            return False
            
        # Skip posts with common noise indicators
        noise_indicators = [
            'eli5', 'explain like', 'daily thread', 'weekly thread',
            'deleted', 'removed', '[removed]', '[deleted]'
        ]
        
        title_content = f"{title} {content}".lower()
        if any(indicator in title_content for indicator in noise_indicators):
            return False
            
        # Prefer news and discussion posts
        preferred_types = ['news', 'discussion', 'link']
        if post_type in preferred_types:
            return True
            
        # For other types, do basic quality check
        return len(content) > 100
    
    def enhance_reddit_metadata(self, reddit_data: Dict) -> Dict:
        """Add Reddit-specific metadata for better classification"""
        if not reddit_data or not reddit_data.get('is_reddit'):
            return reddit_data
            
        subreddit = reddit_data.get('subreddit', '')
        
        # Add subreddit-specific context
        subreddit_context = {
            'r/MachineLearning': {
                'focus': 'research',
                'technical_level': 'high',
                'industry_relevance': ['technology', 'research']
            },
            'r/OpenAI': {
                'focus': 'product',
                'technical_level': 'medium',
                'industry_relevance': ['technology', 'financial']
            },
            'r/LocalLLaMA': {
                'focus': 'implementation',
                'technical_level': 'high',
                'industry_relevance': ['technology', 'utilities']
            },
            'r/artificial': {
                'focus': 'general',
                'technical_level': 'low',
                'industry_relevance': ['technology']
            }
        }
        
        if subreddit in subreddit_context:
            reddit_data['subreddit_context'] = subreddit_context[subreddit]
        else:
            reddit_data['subreddit_context'] = {
                'focus': 'general',
                'technical_level': 'medium',
                'industry_relevance': ['technology']
            }
            
        return reddit_data

if __name__ == "__main__":
    # Test Reddit parser
    parser = RedditParser()
    
    # Test URL detection
    test_urls = [
        "https://www.reddit.com/r/MachineLearning/comments/123/test/",
        "https://techcrunch.com/article/",
        "https://old.reddit.com/r/OpenAI/comments/456/"
    ]
    
    for url in test_urls:
        print(f"Is Reddit: {url} -> {parser.is_reddit_source(url)}")
    
    # Test post type determination
    test_cases = [
        ("How to fine-tune GPT models?", "I'm looking for guidance on...", ""),
        ("OpenAI announces GPT-5", "OpenAI today announced...", "https://openai.com/blog"),
        ("Discussion: Future of AI", "What do you think about...", "")
    ]
    
    for title, content, url in test_cases:
        post_type = parser._determine_post_type(title, content, url)
        print(f"Post type: '{title}' -> {post_type}")
