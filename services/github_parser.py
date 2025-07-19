# services/github_parser.py
"""
GitHub release parsing and processing.
Single responsibility: Handle GitHub release RSS feed parsing and content extraction.
"""
import re
from typing import Dict, Optional, List
from datetime import datetime, timezone
from dateutil import parser as date_parser
import logging

logger = logging.getLogger(__name__)

class GitHubParser:
    """Handles GitHub release RSS feed parsing and content extraction"""
    
    def __init__(self):
        self.github_domains = [
            "github.com", "api.github.com", "raw.githubusercontent.com"
        ]
        
    def is_github_source(self, url: str) -> bool:
        """Check if URL is from GitHub"""
        return any(domain in url.lower() for domain in self.github_domains)
    
    def extract_github_content(self, entry) -> Dict:
        """
        Extract content from GitHub release RSS entry.
        GitHub release entries have structured format with version info.
        """
        try:
            # Extract basic information
            title = self._clean_github_title(entry.title)
            content = self._extract_github_description(entry)
            url = entry.link
            published_date = self._parse_github_date(entry.get('published'))
            
            # Extract GitHub-specific metadata
            repository = self._extract_repository(entry)
            version = self._extract_version(title, content)
            release_type = self._determine_release_type(title, content)
            is_prerelease = self._is_prerelease(title, content)
            
            # Extract technical details
            breaking_changes = self._has_breaking_changes(content)
            features = self._extract_features(content)
            bug_fixes = self._extract_bug_fixes(content)
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'published_date': published_date,
                'repository': repository,
                'version': version,
                'release_type': release_type,
                'is_prerelease': is_prerelease,
                'breaking_changes': breaking_changes,
                'features': features,
                'bug_fixes': bug_fixes,
                'is_github': True
            }
            
        except Exception as e:
            logger.error(f"Error extracting GitHub content: {str(e)}")
            return None
    
    def _clean_github_title(self, title: str) -> str:
        """Clean GitHub release title"""
        if not title:
            return ""
            
        # GitHub release titles often have format: "Repository v1.2.3"
        # Clean up for better readability
        cleaned_title = title.strip()
        
        # If title is just a version number, make it more descriptive
        if re.match(r'^v?\d+\.\d+', cleaned_title):
            cleaned_title = f"Release {cleaned_title}"
            
        return cleaned_title
    
    def _extract_github_description(self, entry) -> str:
        """Extract description/content from GitHub release entry"""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if content:
            # Clean HTML and GitHub-specific formatting
            content = self._clean_github_markdown(content)
            
        return content[:2000]  # Reasonable limit for release notes
    
    def _clean_github_markdown(self, content: str) -> str:
        """Clean GitHub markdown content"""
        from bs4 import BeautifulSoup
        
        try:
            # First, handle HTML if present
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            # Clean up GitHub-specific markdown patterns
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                
                # Skip common GitHub noise
                if any(skip_phrase in line.lower() for skip_phrase in [
                    'full changelog:', 'compare/', 'commits', 'sha-',
                    '**download:**', 'assets', 'checksum'
                ]):
                    continue
                
                # Clean up markdown formatting
                line = re.sub(r'^#+\s*', '', line)  # Remove heading markers
                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold
                line = re.sub(r'\*(.*?)\*', r'\1', line)  # Remove italic
                line = re.sub(r'`(.*?)`', r'\1', line)  # Remove code formatting
                
                if line and len(line) > 5:  # Keep substantial lines
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.warning(f"Error cleaning GitHub content: {str(e)}")
            return content
    
    def _extract_repository(self, entry) -> Optional[str]:
        """Extract repository name from entry"""
        try:
            if hasattr(entry, 'link'):
                # GitHub release URLs have format: https://github.com/owner/repo/releases/tag/v1.0.0
                match = re.search(r'github\.com/([^/]+/[^/]+)', entry.link)
                if match:
                    return match.group(1)
                    
            return None
            
        except Exception:
            return None
    
    def _extract_version(self, title: str, content: str) -> Optional[str]:
        """Extract version number from title or content"""
        try:
            # Look for semantic version patterns
            text = f"{title} {content}"
            
            # Common version patterns
            patterns = [
                r'v?(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?)',  # v1.2.3 or 1.2.3-alpha
                r'version\s+([0-9.]+)',
                r'release\s+([0-9.]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
                    
            return None
            
        except Exception:
            return None
    
    def _determine_release_type(self, title: str, content: str) -> str:
        """Determine the type of release"""
        text = f"{title} {content}".lower()
        
        # Check for specific release types
        if any(indicator in text for indicator in ['alpha', 'beta', 'rc', 'preview']):
            return "prerelease"
        elif any(indicator in text for indicator in ['patch', 'hotfix', 'bugfix']):
            return "patch"
        elif any(indicator in text for indicator in ['major', 'breaking']):
            return "major"
        elif any(indicator in text for indicator in ['minor', 'feature']):
            return "minor"
        else:
            return "release"
    
    def _is_prerelease(self, title: str, content: str) -> bool:
        """Check if this is a prerelease"""
        text = f"{title} {content}".lower()
        prerelease_indicators = [
            'alpha', 'beta', 'rc', 'preview', 'dev', 'nightly',
            'pre-release', 'prerelease'
        ]
        return any(indicator in text for indicator in prerelease_indicators)
    
    def _has_breaking_changes(self, content: str) -> bool:
        """Check if release contains breaking changes"""
        content_lower = content.lower()
        breaking_indicators = [
            'breaking change', 'breaking:', 'breaking',
            'incompatible', 'migration', 'upgrade guide'
        ]
        return any(indicator in content_lower for indicator in breaking_indicators)
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract new features from release notes"""
        features = []
        
        try:
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for feature indicators
                if any(indicator in line.lower() for indicator in [
                    'new:', 'added:', 'feature:', 'enhancement:', '+ '
                ]):
                    # Clean up the feature description
                    feature = re.sub(r'^[+\-*•]\s*', '', line)
                    feature = re.sub(r'^(new|added|feature|enhancement):\s*', '', feature, flags=re.IGNORECASE)
                    
                    if len(feature) > 10 and len(feature) < 200:
                        features.append(feature.strip())
                        
        except Exception as e:
            logger.warning(f"Error extracting features: {str(e)}")
            
        return features[:5]  # Limit to top 5 features
    
    def _extract_bug_fixes(self, content: str) -> List[str]:
        """Extract bug fixes from release notes"""
        bug_fixes = []
        
        try:
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for bug fix indicators
                if any(indicator in line.lower() for indicator in [
                    'fixed:', 'fix:', 'bug:', 'resolved:', 'patch:'
                ]):
                    # Clean up the bug fix description
                    fix = re.sub(r'^[+\-*•]\s*', '', line)
                    fix = re.sub(r'^(fixed|fix|bug|resolved|patch):\s*', '', fix, flags=re.IGNORECASE)
                    
                    if len(fix) > 10 and len(fix) < 200:
                        bug_fixes.append(fix.strip())
                        
        except Exception as e:
            logger.warning(f"Error extracting bug fixes: {str(e)}")
            
        return bug_fixes[:5]  # Limit to top 5 fixes
    
    def _parse_github_date(self, date_string: str) -> Optional[datetime]:
        """Parse GitHub date format"""
        if not date_string:
            return datetime.now(timezone.utc)
        
        try:
            return date_parser.parse(date_string)
        except Exception:
            return datetime.now(timezone.utc)
    
    def filter_github_quality(self, github_data: Dict) -> bool:
        """
        Filter GitHub releases for quality and relevance.
        Returns True if release should be included.
        """
        if not github_data:
            return False
            
        repository = github_data.get('repository', '')
        version = github_data.get('version', '')
        is_prerelease = github_data.get('is_prerelease', False)
        features = github_data.get('features', [])
        
        # Skip if no repository info
        if not repository:
            return False
            
        # Skip very early prereleases unless they're from major projects
        major_projects = [
            'microsoft/semantic-kernel', 'openai/openai-python',
            'langchain-ai/langchain', 'google/generative-ai-python'
        ]
        
        if is_prerelease and repository not in major_projects:
            return False
            
        # Skip patch releases unless they have notable features
        if github_data.get('release_type') == 'patch' and len(features) == 0:
            return False
            
        # Prefer releases with substantial content
        content_length = len(github_data.get('content', ''))
        if content_length < 50:
            return False
            
        return True
    
    def enhance_github_metadata(self, github_data: Dict) -> Dict:
        """Add GitHub-specific metadata for better classification"""
        if not github_data or not github_data.get('is_github'):
            return github_data
            
        repository = github_data.get('repository', '')
        
        # Add repository-specific context
        repo_context = {
            'microsoft/semantic-kernel': {
                'company': 'Microsoft',
                'focus': 'AI orchestration',
                'industry_relevance': ['technology', 'financial', 'utilities'],
                'importance': 'high'
            },
            'openai/openai-python': {
                'company': 'OpenAI',
                'focus': 'AI API client',
                'industry_relevance': ['technology'],
                'importance': 'high'
            },
            'langchain-ai/langchain': {
                'company': 'LangChain',
                'focus': 'AI application framework',
                'industry_relevance': ['technology'],
                'importance': 'high'
            },
            'google/generative-ai-python': {
                'company': 'Google',
                'focus': 'AI API client',
                'industry_relevance': ['technology'],
                'importance': 'medium'
            }
        }
        
        if repository in repo_context:
            github_data['repo_context'] = repo_context[repository]
        else:
            github_data['repo_context'] = {
                'company': 'Unknown',
                'focus': 'general',
                'industry_relevance': ['technology'],
                'importance': 'low'
            }
            
        return github_data

if __name__ == "__main__":
    # Test GitHub parser
    parser = GitHubParser()
    
    # Test URL detection
    test_urls = [
        "https://github.com/microsoft/semantic-kernel/releases/tag/v1.0.0",
        "https://techcrunch.com/article/",
        "https://api.github.com/repos/openai/openai-python/releases"
    ]
    
    for url in test_urls:
        print(f"Is GitHub: {url} -> {parser.is_github_source(url)}")
    
    # Test version extraction
    test_cases = [
        ("Release v1.2.3", "This is version 1.2.3 with new features"),
        ("Semantic Kernel v2.0.0-alpha", "Major breaking changes in this alpha release"),
        ("Patch release", "Fixed several bugs in this patch")
    ]
    
    for title, content in test_cases:
        version = parser._extract_version(title, content)
        release_type = parser._determine_release_type(title, content)
        print(f"Version: '{title}' -> {version}, Type: {release_type}")
