"""
Quick database inspection script to check tables and locks.
Run this to diagnose migration issues.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def inspect_database():
    """Inspect database state"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    # Convert postgres:// to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"🔗 Connecting to: {database_url[:30]}...")
    
    # Create engine with minimal pooling
    engine = create_engine(database_url, poolclass=NullPool, echo=False)
    
    try:
        with engine.connect() as conn:
            # Check database info
            result = conn.execute(text("SELECT current_database(), current_user, version()"))
            db_info = result.fetchone()
            print(f"✅ Connected to: {db_info[0]} as {db_info[1]}")
            print(f"📊 PostgreSQL version: {db_info[2][:50]}...")
            
            # Check existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Existing tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            
            # Check alembic version
            if 'alembic_version' in tables:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.fetchone()
                print(f"\n🔖 Alembic version: {version[0] if version else 'None'}")
            else:
                print("\n⚠️ No alembic_version table found")
            
            # Check for locks
            result = conn.execute(text("""
                SELECT 
                    pid,
                    usename,
                    application_name,
                    state,
                    query_start,
                    state_change,
                    left(query, 100) as query_snippet
                FROM pg_stat_activity
                WHERE datname = current_database()
                    AND pid != pg_backend_pid()
                    AND state != 'idle'
                ORDER BY query_start
            """))
            
            active_queries = result.fetchall()
            if active_queries:
                print(f"\n⚠️ Active queries/locks ({len(active_queries)}):")
                for query in active_queries:
                    print(f"  PID {query[0]}: {query[6]}")
            else:
                print("\n✅ No active locks detected")
            
            # Check table sizes
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    n_tup_ins + n_tup_upd + n_tup_del as total_writes
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            
            print("\n📊 Table statistics:")
            for row in result.fetchall():
                print(f"  {row[1]}: {row[2]} ({row[3]} writes)")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    inspect_database()