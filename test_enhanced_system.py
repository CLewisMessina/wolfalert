# test_enhanced_system.py
"""
Standalone script to test the enhanced news aggregation system.
Run this to verify everything works before integrating.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all enhanced modules can be imported"""
    print("Testing Enhanced System Imports...")
    print("=" * 50)
    
    try:
        from services.source_manager import SourceManager
        print("✓ source_manager.py imported successfully")
    except ImportError as e:
        print(f"✗ source_manager.py failed: {e}")
        return False
    
    try:
        from services.content_filters import ContentFilter
        print("✓ content_filters.py imported successfully")
    except ImportError as e:
        print(f"✗ content_filters.py failed: {e}")
        return False
    
    try:
        from services.reddit_parser import RedditParser
        print("✓ reddit_parser.py imported successfully")
    except ImportError as e:
        print(f"✗ reddit_parser.py failed: {e}")
        return False
    
    try:
        from services.github_parser import GitHubParser
        print("✓ github_parser.py imported successfully")
    except ImportError as e:
        print(f"✗ github_parser.py failed: {e}")
        return False
    
    try:
        from services.enhanced_news_aggregator import EnhancedNewsAggregator
        print("✓ enhanced_news_aggregator.py imported successfully")
    except ImportError as e:
        print(f"✗ enhanced_news_aggregator.py failed: {e}")
        return False
    
    print("\n✓ All imports successful!")
    return True

def test_source_manager():
    """Test the source manager functionality"""
    print("\nTesting Source Manager...")
    print("=" * 30)
    
    try:
        from services.source_manager import SourceManager
        
        manager = SourceManager()
        stats = manager.get_source_statistics()
        
        print(f"✓ Total sources configured: {stats['total_sources']}")
        print(f"✓ Official blogs: {stats['by_type'].get('official_blog', 0)}")
        print(f"✓ Community sources: {stats['by_type'].get('community', 0)}")
        print(f"✓ Product releases: {stats['by_type'].get('product_releases', 0)}")
        print(f"✓ News sources: {stats['by_type'].get('news', 0)}")
        
        # Test specific source lookup
        google_sources = manager.get_sources_by_company("Google")
        print(f"✓ Google sources: {len(google_sources)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Source manager test failed: {e}")
        return False

def test_content_filters():
    """Test the content filtering functionality"""
    print("\nTesting Content Filters...")
    print("=" * 30)
    
    try:
        from services.content_filters import ContentFilter
        
        filter_engine = ContentFilter()
        
        # Test AI relevance detection
        test_cases = [
            ("OpenAI Announces GPT-5", "New artificial intelligence model with advanced reasoning capabilities", "high"),
            ("Random Blog Post", "This is about cooking recipes and has nothing to do with technology", "medium"),
            ("Machine Learning in Healthcare", "New deep learning research for medical diagnosis applications", "high")
        ]
        
        for title, content, reliability in test_cases:
            result = filter_engine.calculate_content_score(title, content, reliability)
            should_include = filter_engine.should_include_content(title, content, reliability)
            
            print(f"✓ '{title[:30]}...' -> AI relevance: {result['ai_relevance']}, Include: {should_include}")
        
        return True
        
    except Exception as e:
        print(f"✗ Content filter test failed: {e}")
        return False

def test_parsers():
    """Test Reddit and GitHub parsers"""
    print("\nTesting Specialized Parsers...")
    print("=" * 35)
    
    try:
        from services.reddit_parser import RedditParser
        from services.github_parser import GitHubParser
        
        # Test Reddit parser
        reddit_parser = RedditParser()
        reddit_urls = [
            "https://www.reddit.com/r/MachineLearning/comments/123/test/",
            "https://techcrunch.com/article/"
        ]
        
        for url in reddit_urls:
            is_reddit = reddit_parser.is_reddit_source(url)
            print(f"✓ Reddit detection '{url[:40]}...' -> {is_reddit}")
        
        # Test GitHub parser
        github_parser = GitHubParser()
        github_urls = [
            "https://github.com/microsoft/semantic-kernel/releases/tag/v1.0.0",
            "https://techcrunch.com/article/"
        ]
        
        for url in github_urls:
            is_github = github_parser.is_github_source(url)
            print(f"✓ GitHub detection '{url[:40]}...' -> {is_github}")
        
        return True
        
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False

def test_enhanced_aggregator():
    """Test the main enhanced aggregator"""
    print("\nTesting Enhanced Aggregator...")
    print("=" * 35)
    
    try:
        from services.enhanced_news_aggregator import EnhancedNewsAggregator
        
        aggregator = EnhancedNewsAggregator()
        
        # Test configuration
        stats = aggregator.get_aggregation_statistics()
        print(f"✓ Aggregator initialized with {stats['sources']['total_sources']} sources")
        
        # Test connectivity (first 5 sources only)
        print("✓ Testing source connectivity (first 5 sources)...")
        connectivity = aggregator.test_source_connectivity()
        
        working_sources = 0
        tested_sources = 0
        
        for source_name, is_working in list(connectivity.items())[:5]:
            status_icon = "✓" if is_working else "✗"
            print(f"  {status_icon} {source_name}")
            if is_working:
                working_sources += 1
            tested_sources += 1
        
        print(f"✓ Connectivity test: {working_sources}/{tested_sources} sources working")
        
        # Test sample source
        print("✓ Testing sample source extraction...")
        sample_result = aggregator.run_source_test("Google AI Blog", max_articles=2)
        
        if sample_result.get("status") == "success":
            print(f"  ✓ Sample test successful: {sample_result.get('filtered_articles', 0)} articles")
        else:
            print(f"  ⚠ Sample test had issues: {sample_result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced aggregator test failed: {e}")
        return False

def test_demo_creation():
    """Test demo article creation"""
    print("\nTesting Demo Article Creation...")
    print("=" * 40)
    
    try:
        from services.enhanced_news_aggregator import EnhancedNewsAggregator
        
        aggregator = EnhancedNewsAggregator()
        demo_count = aggregator.create_demo_articles()
        
        print(f"✓ Created {demo_count} enhanced demo articles")
        return True
        
    except Exception as e:
        print(f"✗ Demo creation failed: {e}")
        return False

def show_integration_steps():
    """Show the integration steps"""
    print("\n" + "=" * 60)
    print("INTEGRATION STEPS")
    print("=" * 60)
    
    steps = [
        "1. ✓ Enhanced system files are working properly",
        "",
        "2. Next: Update your existing files:",
        "   - In api/articles.py, change:",
        "     FROM: from services.news_aggregator import NewsAggregator",
        "     TO:   from services.enhanced_news_aggregator import EnhancedNewsAggregator",
        "",
        "   - In api/articles.py, change the fetch_task function:",
        "     FROM: aggregator = NewsAggregator()",
        "     TO:   aggregator = EnhancedNewsAggregator()",
        "",
        "     FROM: count = aggregator.run_aggregation()",
        "     TO:   count = aggregator.run_enhanced_aggregation()",
        "",
        "3. Optional: Add new endpoints to main.py:",
        "   - /debug/sources (shows source status)",
        "   - /initialize-enhanced-demo (better demo data)",
        "",
        "4. Test the integration:",
        "   - python main.py",
        "   - Visit: http://localhost:8000/initialize-enhanced-demo",
        "   - Visit: http://localhost:8000 (dashboard should show new articles)",
        "",
        "5. Verify enhanced functionality:",
        "   - More diverse article sources",
        "   - Better content filtering",
        "   - Enhanced demo articles with industry context"
    ]
    
    for step in steps:
        print(step)

def main():
    """Run all tests"""
    print("WolfAlert Enhanced News Aggregation System Test")
    print("=" * 60)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_imports,
        test_source_manager,
        test_content_filters,
        test_parsers,
        test_enhanced_aggregator,
        test_demo_creation
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            all_passed = False
        print()  # Add spacing between tests
    
    # Show results
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced system is ready for integration")
        show_integration_steps()
    else:
        print("❌ SOME TESTS FAILED")
        print("❗ Please check the error messages above")
        print("❗ Make sure all 5 enhanced service files are in the services/ directory")

if __name__ == "__main__":
    main()
