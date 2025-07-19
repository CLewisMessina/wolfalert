# services/content_filters.py
"""
Content filtering and AI relevance detection.
Single responsibility: Determine if content is AI-relevant and assess quality.
"""
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RelevanceLevel(str, Enum):
    HIGH = "high"           # Directly AI-focused
    MEDIUM = "medium"       # AI-adjacent or AI-enabled
    LOW = "low"            # Mentions AI but not core focus
    NONE = "none"          # No AI relevance

class ContentType(str, Enum):
    PRODUCT_ANNOUNCEMENT = "product_announcement"
    RESEARCH_PAPER = "research_paper"
    COMPANY_NEWS = "company_news"
    TECHNICAL_UPDATE = "technical_update"
    OPINION_ANALYSIS = "opinion_analysis"
    COMMUNITY_DISCUSSION = "community_discussion"

class ContentFilter:
    """Filters and classifies content for AI relevance and business value"""
    
    def __init__(self):
        self.ai_keywords = self._initialize_ai_keywords()
        self.business_keywords = self._initialize_business_keywords()
        self.noise_patterns = self._initialize_noise_patterns()
        
    def _initialize_ai_keywords(self) -> Dict[str, List[str]]:
        """Initialize AI-related keyword categories with weights"""
        return {
            "core_ai": [
                "artificial intelligence", "machine learning", "deep learning",
                "neural network", "natural language processing", "computer vision",
                "large language model", "LLM", "generative AI", "foundation model"
            ],
            "ai_products": [
                "GPT", "Claude", "Gemini", "ChatGPT", "Copilot", "Bard",
                "Dall-E", "Midjourney", "Stable Diffusion", "OpenAI",
                "Anthropic", "Hugging Face", "LangChain"
            ],
            "ai_techniques": [
                "transformer", "attention mechanism", "fine-tuning", "RLHF",
                "prompt engineering", "few-shot learning", "zero-shot",
                "reinforcement learning", "supervised learning", "unsupervised learning"
            ],
            "ai_applications": [
                "chatbot", "virtual assistant", "automation", "predictive analytics",
                "recommendation system", "fraud detection", "sentiment analysis",
                "image recognition", "speech recognition", "text generation"
            ],
            "ai_infrastructure": [
                "GPU", "TPU", "CUDA", "PyTorch", "TensorFlow", "MLOps",
                "model deployment", "inference", "training", "vector database"
            ]
        }
    
    def _initialize_business_keywords(self) -> Dict[str, List[str]]:
        """Initialize business impact keywords by industry"""
        return {
            "utilities": [
                "smart grid", "energy management", "demand response", "load balancing",
                "renewable energy", "power generation", "grid optimization",
                "electric vehicle", "charging infrastructure", "outage prediction"
            ],
            "financial": [
                "fintech", "fraud detection", "risk management", "algorithmic trading",
                "credit scoring", "compliance", "regulatory", "blockchain",
                "cryptocurrency", "payment processing", "robo-advisor"
            ],
            "healthcare": [
                "medical diagnosis", "drug discovery", "clinical trial", 
                "medical imaging", "electronic health record", "telemedicine",
                "genomics", "precision medicine", "patient monitoring"
            ],
            "manufacturing": [
                "industrial automation", "predictive maintenance", "quality control",
                "supply chain", "robotics", "digital twin", "IoT sensors",
                "production optimization", "defect detection"
            ]
        }
    
    def _initialize_noise_patterns(self) -> List[str]:
        """Patterns that indicate low-value content"""
        return [
            r"click here", r"subscribe now", r"limited time",
            r"you won't believe", r"shocking", r"amazing trick",
            r"[0-9]+ ways to", r"ultimate guide", r"secret",
            r"deleted.*comment", r"removed.*moderator"
        ]
    
    def assess_ai_relevance(self, title: str, content: str) -> Tuple[RelevanceLevel, float]:
        """
        Assess AI relevance of content.
        Returns: (RelevanceLevel, confidence_score)
        """
        text = f"{title} {content}".lower()
        
        # Score different keyword categories
        scores = {}
        for category, keywords in self.ai_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            scores[category] = score
        
        # Calculate weighted relevance score
        weighted_score = (
            scores.get("core_ai", 0) * 3.0 +
            scores.get("ai_products", 0) * 2.5 +
            scores.get("ai_techniques", 0) * 2.0 +
            scores.get("ai_applications", 0) * 1.5 +
            scores.get("ai_infrastructure", 0) * 1.0
        )
        
        # Normalize score based on content length
        word_count = len(text.split())
        normalized_score = weighted_score / max(word_count / 100, 1.0)
        
        # Determine relevance level
        if normalized_score >= 2.0:
            return RelevanceLevel.HIGH, min(normalized_score / 5.0, 1.0)
        elif normalized_score >= 1.0:
            return RelevanceLevel.MEDIUM, min(normalized_score / 3.0, 1.0)
        elif normalized_score >= 0.3:
            return RelevanceLevel.LOW, min(normalized_score / 1.5, 1.0)
        else:
            return RelevanceLevel.NONE, 0.0
    
    def assess_business_relevance(self, title: str, content: str, 
                                target_industries: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Assess business relevance for specific industries.
        Returns: {industry: relevance_score}
        """
        text = f"{title} {content}".lower()
        industry_scores = {}
        
        industries = target_industries or list(self.business_keywords.keys())
        
        for industry in industries:
            if industry in self.business_keywords:
                keywords = self.business_keywords[industry]
                score = sum(1 for keyword in keywords if keyword.lower() in text)
                # Normalize by keyword count and content length
                normalized_score = score / (len(keywords) * max(len(text.split()) / 200, 1.0))
                industry_scores[industry] = min(normalized_score, 1.0)
        
        return industry_scores
    
    def detect_content_type(self, title: str, content: str, source_name: str) -> ContentType:
        """Classify the type of content"""
        text = f"{title} {content}".lower()
        
        # GitHub releases
        if "github.com" in source_name.lower() or "releases" in source_name.lower():
            return ContentType.TECHNICAL_UPDATE
            
        # Reddit content
        if "reddit" in source_name.lower():
            return ContentType.COMMUNITY_DISCUSSION
            
        # Product announcement patterns
        announcement_patterns = [
            r"announce", r"launch", r"introduce", r"unveil", r"release",
            r"available now", r"coming soon", r"new feature"
        ]
        if any(re.search(pattern, text) for pattern in announcement_patterns):
            return ContentType.PRODUCT_ANNOUNCEMENT
            
        # Research patterns
        research_patterns = [
            r"research", r"study", r"paper", r"findings", r"methodology",
            r"experiment", r"analysis", r"survey"
        ]
        if any(re.search(pattern, text) for pattern in research_patterns):
            return ContentType.RESEARCH_PAPER
            
        # Opinion/analysis patterns
        opinion_patterns = [
            r"opinion", r"analysis", r"perspective", r"think", r"believe",
            r"future of", r"trend", r"prediction"
        ]
        if any(re.search(pattern, text) for pattern in opinion_patterns):
            return ContentType.OPINION_ANALYSIS
            
        return ContentType.COMPANY_NEWS
    
    def is_noise(self, title: str, content: str) -> bool:
        """Detect if content is likely noise/spam"""
        text = f"{title} {content}".lower()
        
        # Check noise patterns
        for pattern in self.noise_patterns:
            if re.search(pattern, text):
                return True
                
        # Check for excessive punctuation or caps
        if title.count('!') > 2 or title.count('?') > 2:
            return True
            
        if len([c for c in title if c.isupper()]) / max(len(title), 1) > 0.3:
            return True
            
        # Check for very short content
        if len(content.strip()) < 50:
            return True
            
        return False
    
    def calculate_content_score(self, title: str, content: str, source_reliability: str,
                              target_industries: Optional[List[str]] = None) -> Dict:
        """
        Calculate comprehensive content score.
        Returns: {
            'ai_relevance': RelevanceLevel,
            'ai_confidence': float,
            'business_relevance': Dict[str, float],
            'content_type': ContentType,
            'is_noise': bool,
            'overall_score': float
        }
        """
        # Get AI relevance
        ai_relevance, ai_confidence = self.assess_ai_relevance(title, content)
        
        # Get business relevance
        business_relevance = self.assess_business_relevance(title, content, target_industries)
        
        # Detect content type
        content_type = self.detect_content_type(title, content, "")
        
        # Check for noise
        is_noise = self.is_noise(title, content)
        
        # Calculate overall score
        ai_score = ai_confidence if ai_relevance != RelevanceLevel.NONE else 0.0
        business_score = max(business_relevance.values()) if business_relevance else 0.0
        
        # Weight by source reliability
        reliability_multiplier = {
            "high": 1.0,
            "medium": 0.8,
            "community": 0.6
        }.get(source_reliability, 0.5)
        
        overall_score = (ai_score * 0.6 + business_score * 0.4) * reliability_multiplier
        
        if is_noise:
            overall_score *= 0.1  # Heavily penalize noise
            
        return {
            'ai_relevance': ai_relevance,
            'ai_confidence': ai_confidence,
            'business_relevance': business_relevance,
            'content_type': content_type,
            'is_noise': is_noise,
            'overall_score': overall_score
        }
    
    def should_include_content(self, title: str, content: str, source_reliability: str,
                             min_score: float = 0.3) -> bool:
        """Determine if content should be included based on filters"""
        score_data = self.calculate_content_score(title, content, source_reliability)
        
        return (not score_data['is_noise'] and 
                score_data['overall_score'] >= min_score and
                score_data['ai_relevance'] != RelevanceLevel.NONE)

if __name__ == "__main__":
    # Test the content filter
    filter_engine = ContentFilter()
    
    # Test cases
    test_cases = [
        ("OpenAI Announces GPT-5 with Advanced Reasoning", 
         "OpenAI today announced GPT-5, featuring breakthrough advances in artificial intelligence reasoning capabilities...",
         "high"),
        ("10 Amazing AI Tricks You Won't Believe!", 
         "Click here to see these shocking AI secrets that will amaze you...",
         "medium"),
        ("New Study on Machine Learning in Healthcare",
         "Researchers at Stanford published findings on using deep learning for medical diagnosis in clinical settings...",
         "high")
    ]
    
    for title, content, reliability in test_cases:
        result = filter_engine.calculate_content_score(title, content, reliability)
        print(f"\nTitle: {title}")
        print(f"AI Relevance: {result['ai_relevance']} (confidence: {result['ai_confidence']:.2f})")
        print(f"Content Type: {result['content_type']}")
        print(f"Is Noise: {result['is_noise']}")
        print(f"Overall Score: {result['overall_score']:.2f}")
        print(f"Should Include: {filter_engine.should_include_content(title, content, reliability)}")
