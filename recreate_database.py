#!/usr/bin/env python3
"""
Database migration script for Hydepark Lyve Middleware
Recreates database with proper schema
"""

import sqlite3
import os
import shutil

def recreate_database():
    """Recreate database with proper schema"""
    db_path = "hydepark_lyve.db"
    backup_path = f"hydepark_lyve_backup_{int(time.time())}.db"
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"📋 Database backed up to: {backup_path}")
        os.remove(db_path)
        print("🗑️  Old database removed")
    
    # Create new database with proper schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create person_mappings table
        cursor.execute("""
            CREATE TABLE person_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lyve_person_id VARCHAR(100) UNIQUE NOT NULL,
                hikcentral_person_id VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                given_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                gender INTEGER DEFAULT 1,
                certificate_type INTEGER,
                certificate_num VARCHAR(50),
                person_type INTEGER DEFAULT 1,
                face_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                org_index_code VARCHAR(50) DEFAULT '1',
                begin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create api_logs table
        cursor.execute("""
            CREATE TABLE api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint VARCHAR(200) NOT NULL,
                method VARCHAR(10) NOT NULL,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent VARCHAR(500)
            )
        """)
        
        # Create face_data table
        cursor.execute("""
            CREATE TABLE face_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_mapping_id INTEGER NOT NULL,
                face_data TEXT NOT NULL,
                face_name VARCHAR(100) NOT NULL,
                face_type INTEGER DEFAULT 1,
                face_quality INTEGER DEFAULT 80,
                born_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sex INTEGER DEFAULT 1,
                certificate_type INTEGER,
                certificate_num VARCHAR(50),
                image_format VARCHAR(10),
                image_size INTEGER,
                image_dimensions VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_mapping_id) REFERENCES person_mappings (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_lyve_person_id ON person_mappings(lyve_person_id)")
        cursor.execute("CREATE INDEX idx_hikcentral_person_id ON person_mappings(hikcentral_person_id)")
        cursor.execute("CREATE INDEX idx_created_at ON api_logs(created_at)")
        cursor.execute("CREATE INDEX idx_person_mapping_id ON face_data(person_mapping_id)")
        
        conn.commit()
        print("✅ Database recreated successfully with proper schema!")
        
    except Exception as e:
        print(f"❌ Database recreation failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import time
    
    print("🔧 Hydepark Lyve Middleware - Database Recreation")
    print("=" * 60)
    
    recreate_database()
    
    print("\n🎉 Database recreation completed!")
    print("The middleware will automatically use the new schema when restarted.")