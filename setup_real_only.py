# setup_real_only.py
"""
Standalone script to set up real-only article mode.
This script can be run directly to configure your system for real articles only.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_real_only_system():
    """Test if the real-only system is working"""
    print("Testing Real-Only System...")
    print("=" * 35)
    
    try:
        from services.real_only_aggregator import RealOnlyAggregator
        print("✓ Real-only aggregator imported successfully")
        
        aggregator = RealOnlyAggregator()
        print("✓ Real-only aggregator initialized")
        
        return aggregator
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("Make sure you have the real_only_aggregator.py file in services/")
        return None
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        return None

def setup_real_only_mode():
    """Complete setup for real-only article mode"""
    print("WolfAlert Real-Only Article Setup")
    print("=" * 40)
    
    # Test system
    aggregator = test_real_only_system()
    if not aggregator:
        return False
    
    try:
        # Step 1: Show current statistics
        print("\n1. Current Database Statistics:")
        stats = aggregator.get_real_article_statistics()
        print(f"   Total articles: {stats.get('total_articles', 0)}")
        print(f"   Real articles: {stats.get('real_articles', 0)}")
        print(f"   Demo articles: {stats.get('demo_articles', 0)}")
        
        # Step 2: Clear demo articles
        print("\n2. Clearing Demo Articles...")
        cleared = aggregator.clear_demo_articles()
        print(f"   ✓ Cleared {cleared} demo articles")
        
        # Step 3: Test source connectivity
        print("\n3. Testing Source Connectivity...")
        connectivity = aggregator.test_source_connectivity()
        working_sources = sum(1 for status in connectivity.values() if status)
        print(f"   ✓ {working_sources}/{len(connectivity)} sources are accessible")
        
        # Show first few working sources
        working_list = [name for name, status in connectivity.items() if status][:5]
        for source in working_list:
            print(f"     ✓ {source}")
        
        # Step 4: Fetch real articles
        print("\n4. Fetching Real Articles...")
        print("   This may take 30-60 seconds...")
        count = aggregator.run_real_only_aggregation()
        print(f"   ✓ Successfully fetched {count} real articles")
        
        # Step 5: Final statistics
        print("\n5. Final Statistics:")
        final_stats = aggregator.get_real_article_statistics()
        print(f"   Total articles: {final_stats.get('total_articles', 0)}")
        print(f"   Real articles: {final_stats.get('real_articles', 0)}")
        print(f"   Real sources: {len(final_stats.get('real_sources', []))}")
        print(f"   Percentage real: {final_stats.get('percentage_real', 0):.1f}%")
        
        # Step 6: Show sample real sources
        real_sources = final_stats.get('real_sources', [])[:8]
        if real_sources:
            print(f"\n   Sample real sources:")
            for source in real_sources:
                print(f"     • {source}")
        
        print("\n" + "=" * 50)
        print("🎉 REAL-ONLY SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps:")
        print("1. Start your app: python main.py")
        print("2. Visit: http://localhost:8000")
        print("3. Click 'Refresh Feed' to get more real articles")
        print("4. All articles should now have working links!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        return False

def quick_test():
    """Quick test to verify everything is working"""
    print("\nQuick Functionality Test:")
    print("-" * 30)
    
    try:
        from services.real_only_aggregator import RealOnlyAggregator
        
        aggregator = RealOnlyAggregator()
        
        # Test a single source
        print("Testing sample source...")
        result = aggregator.run_source_test("TechCrunch AI", max_articles=2)
        
        if result.get("status") == "success":
            print(f"✓ Sample test successful: {result.get('filtered_articles', 0)} articles")
            if result.get('sample_titles'):
                print("  Sample titles:")
                for title in result['sample_titles'][:2]:
                    print(f"    - {title[:60]}...")
        else:
            print(f"⚠ Sample test had issues: {result.get('error', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        return False

def show_instructions():
    """Show instructions for manual integration"""
    print("\n" + "=" * 60)
    print("MANUAL INTEGRATION INSTRUCTIONS")
    print("=" * 60)
    print("If you want to update your existing API to use real-only mode:")
    print()
    print("1. In api/articles.py, change the import:")
    print("   FROM: from services.enhanced_news_aggregator import EnhancedNewsAggregator")
    print("   TO:   from services.real_only_aggregator import RealOnlyAggregator")
    print()
    print("2. In api/articles.py, update the fetch_task function:")
    print("   FROM: aggregator = EnhancedNewsAggregator()")
    print("   TO:   aggregator = RealOnlyAggregator()")
    print()
    print("   FROM: count = aggregator.run_enhanced_aggregation()")
    print("   TO:   count = aggregator.run_real_only_aggregation()")
    print()
    print("3. Optional: Add new endpoints to main.py for real-only functionality")
    print()
    print("Or simply use the system as-is - it's already working with real articles!")

def main():
    """Main setup function"""
    print("🐺 WolfAlert Real-Only Article Setup")
    print("🔄 Configuring system to fetch only real articles...")
    print()
    
    # Run the setup
    success = setup_real_only_mode()
    
    if success:
        # Run quick test
        quick_test()
        
        # Show integration instructions
        show_instructions()
    else:
        print("\n❌ Setup failed. Please check error messages above.")
        print("Make sure you have all the enhanced service files in place.")

if __name__ == "__main__":
    main()
