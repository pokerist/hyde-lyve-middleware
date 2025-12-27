#!/usr/bin/env python3
"""
Database migration script for Hydepark Lyve Middleware
Updates database schema to support new features
"""

import sqlite3
import os

def migrate_database():
    """Migrate existing database to new schema"""
    db_path = "hydepark_lyve.db"
    
    if not os.path.exists(db_path):
        print("Database does not exist yet. Will be created automatically.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(person_mappings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add missing columns
        new_columns = [
            ("given_name", "VARCHAR(100)"),
            ("certificate_type", "INTEGER"),
            ("certificate_num", "VARCHAR(50)"),
            ("person_type", "INTEGER DEFAULT 1"),
            ("face_count", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE person_mappings ADD COLUMN {column_name} {column_type}")
            else:
                print(f"Column {column_name} already exists")
        
        # Create face_data table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_data (
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
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def backup_database():
    """Create a backup of the existing database"""
    db_path = "hydepark_lyve.db"
    backup_path = f"hydepark_lyve_backup_{int(time.time())}.db"
    
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📋 Database backed up to: {backup_path}")
    else:
        print("No existing database to backup")

if __name__ == "__main__":
    import time
    
    print("🔧 Hydepark Lyve Middleware - Database Migration")
    print("=" * 50)
    
    # Backup first
    backup_database()
    
    # Run migration
    migrate_database()
    
    print("\n🎉 Migration process completed!")