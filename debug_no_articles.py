# debug_no_articles.py
"""
Debug script to figure out why no articles are being fetched.
Run this to diagnose the issue step by step.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Check what's in the database"""
    print("1. DATABASE CHECK")
    print("=" * 20)
    
    try:
        from models.database import SessionLocal, Article
        
        db = SessionLocal()
        total_articles = db.query(Article).count()
        
        print(f"Total articles in database: {total_articles}")
        
        if total_articles > 0:
            # Show recent articles
            recent = db.query(Article).order_by(Article.created_at.desc()).limit(5).all()
            print("\nRecent articles:")
            for article in recent:
                print(f"  - {article.title[:60]}...")
                print(f"    Source: {article.source}")
                print(f"    URL: {article.url}")
                print()
        else:
            print("❌ No articles found in database!")
        
        db.close()
        return total_articles > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("2. IMPORT TEST")
    print("=" * 15)
    
    modules_to_test = [
        ('feedparser', 'feedparser'),
        ('requests', 'requests'),
        ('bs4', 'BeautifulSoup'),
        ('services.source_manager', 'SourceManager'),
        ('services.real_only_aggregator', 'RealOnlyAggregator'),
    ]
    
    all_good = True
    
    for module_name, class_name in modules_to_test:
        try:
            if module_name == 'services.source_manager':
                from services.source_manager import SourceManager
                print(f"✓ {module_name} imported successfully")
            elif module_name == 'services.real_only_aggregator':
                from services.real_only_aggregator import RealOnlyAggregator
                print(f"✓ {module_name} imported successfully")
            elif module_name == 'feedparser':
                import feedparser
                print(f"✓ {module_name} imported successfully")
            elif module_name == 'requests':
                import requests
                print(f"✓ {module_name} imported successfully")
            elif module_name == 'bs4':
                from bs4 import BeautifulSoup
                print(f"✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ {module_name} failed: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠ {module_name} error: {e}")
            all_good = False
    
    return all_good

def test_source_connectivity():
    """Test if RSS sources are accessible"""
    print("3. SOURCE CONNECTIVITY TEST")
    print("=" * 30)
    
    try:
        from services.real_only_aggregator import RealOnlyAggregator
        
        aggregator = RealOnlyAggregator()
        connectivity = aggregator.test_source_connectivity()
        
        working_sources = [name for name, status in connectivity.items() if status]
        broken_sources = [name for name, status in connectivity.items() if not status]
        
        print(f"✓ Working sources: {len(working_sources)}/{len(connectivity)}")
        print(f"❌ Broken sources: {len(broken_sources)}")
        
        if working_sources:
            print("\nWorking sources (first 5):")
            for source in working_sources[:5]:
                print(f"  ✓ {source}")
        
        if broken_sources:
            print(f"\nBroken sources (first 5):")
            for source in broken_sources[:5]:
                print(f"  ❌ {source}")
        
        return len(working_sources) > 0
        
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_single_source():
    """Test fetching from a single reliable source"""
    print("4. SINGLE SOURCE TEST")
    print("=" * 22)
    
    try:
        import feedparser
        import requests
        
        # Test a reliable source
        test_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        
        print(f"Testing: {test_url}")
        
        # Test basic connectivity
        response = requests.head(test_url, timeout=10)
        print(f"✓ HTTP Status: {response.status_code}")
        
        # Test RSS parsing
        feed = feedparser.parse(test_url)
        print(f"✓ RSS entries found: {len(feed.entries)}")
        
        if len(feed.entries) > 0:
            first_entry = feed.entries[0]
            print(f"✓ Sample title: {first_entry.title[:60]}...")
            return True
        else:
            print("❌ No entries in RSS feed")
            return False
            
    except Exception as e:
        print(f"❌ Single source test failed: {e}")
        return False

def test_aggregator_step_by_step():
    """Test the aggregator step by step"""
    print("5. AGGREGATOR STEP-BY-STEP TEST")
    print("=" * 35)
    
    try:
        from services.real_only_aggregator import RealOnlyAggregator
        
        aggregator = RealOnlyAggregator()
        print("✓ Aggregator created")
        
        # Get source configuration
        sources = aggregator.source_manager.get_all_sources()
        print(f"✓ Sources configured: {len(sources)}")
        
        # Test fetching from one source
        source_name = "TechCrunch AI"
        if source_name in sources:
            source_config = sources[source_name]
            print(f"✓ Testing source: {source_name}")
            
            articles = aggregator._fetch_rss_articles(source_config)
            print(f"✓ Raw articles fetched: {len(articles)}")
            
            if articles:
                filtered = aggregator._filter_and_enhance_articles(articles, source_config)
                print(f"✓ Filtered articles: {len(filtered)}")
                
                if filtered:
                    print(f"✓ Sample article: {filtered[0]['title'][:60]}...")
                    return len(filtered)
                else:
                    print("❌ All articles were filtered out")
                    return 0
            else:
                print("❌ No raw articles fetched")
                return 0
        else:
            print(f"❌ Source {source_name} not found")
            return 0
            
    except Exception as e:
        print(f"❌ Aggregator test failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

def run_manual_fetch():
    """Manually run a fetch and see what happens"""
    print("6. MANUAL FETCH TEST")
    print("=" * 20)
    
    try:
        from services.real_only_aggregator import RealOnlyAggregator
        
        aggregator = RealOnlyAggregator()
        print("✓ Starting manual fetch...")
        
        count = aggregator.run_real_only_aggregation()
        print(f"✓ Fetch completed: {count} articles saved")
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Manual fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🐺 WolfAlert Article Fetching Diagnostic")
    print("=" * 45)
    print()
    
    tests = [
        ("Database Check", check_database),
        ("Import Test", test_imports),
        ("Source Connectivity", test_source_connectivity),
        ("Single Source Test", test_single_source),
        ("Aggregator Step-by-Step", test_aggregator_step_by_step),
        ("Manual Fetch", run_manual_fetch),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"Result: {'✓ PASS' if result else '❌ FAIL'}")
        except Exception as e:
            print(f"❌ CRASHED: {e}")
            results.append((test_name, False))
        
        print("-" * 50)
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    
    if not results[0][1]:  # Database check failed
        print("• Database issue - try: rm wolfalert.db && python models/database.py")
    
    if not results[1][1]:  # Import test failed
        print("• Missing dependencies - try: pip install -r requirements.txt")
    
    if not results[2][1]:  # Connectivity failed
        print("• Network/firewall issue - check internet connection")
    
    if not results[3][1]:  # Single source failed
        print("• RSS parsing issue - check feedparser installation")
    
    if not results[4][1]:  # Aggregator failed
        print("• Code issue - check error messages above")
    
    if not results[5][1]:  # Manual fetch failed
        print("• Integration issue - check file setup")
    
    passed = sum(1 for _, result in results if result)
    print(f"\nOverall: {passed}/{len(results)} tests passed")

if __name__ == "__main__":
    main()
