#!/usr/bin/env python3
"""
Database initialization script for Hydepark Lyve Middleware
Creates PostgreSQL database and tables
"""

import asyncio
import asyncpg
import sys
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        
        # Check if database exists
        result = await conn.fetchrow(
            "SELECT 1 FROM pg_database WHERE datname = 'hyde_lyve'"
        )
        
        if not result:
            print("🗄️ Creating database 'hyde_lyve'...")
            await conn.execute("CREATE DATABASE hyde_lyve")
            print("✅ Database created successfully")
        else:
            print("📋 Database 'hyde_lyve' already exists")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

async def create_tables():
    """Create database tables"""
    try:
        # Create engine
        engine = create_async_engine(settings.database_url, echo=True)
        
        print("🔧 Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tables created successfully")
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

async def main():
    """Main initialization function"""
    print("🚀 Hydepark Lyve Middleware - Database Initialization")
    print("=" * 60)
    
    # Create database
    db_success = await create_database()
    if not db_success:
        print("❌ Database creation failed")
        return 1
    
    # Create tables
    tables_success = await create_tables()
    if not tables_success:
        print("❌ Table creation failed")
        return 1
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the application: python -m app.main")
    print("2. Test the API: curl -X GET http://localhost:3000/health")
    print("3. Check API docs: http://localhost:3000/docs")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)