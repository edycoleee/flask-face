#!/usr/bin/env python3
"""
Migration script to add password column to existing users table
Run this once to update the database schema
"""

import sqlite3
import os

DB_PATH = os.path.join("instance", "app.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. No migration needed.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if password column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'password' in columns:
        print("✅ Password column already exists. No migration needed.")
        conn.close()
        return
    
    print("🔄 Adding password column to users table...")
    
    try:
        # Add password column with default value
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT NOT NULL DEFAULT 'password123'")
        conn.commit()
        
        # Update existing users with default password
        cursor.execute("UPDATE users SET password = 'password123' WHERE password = 'password123'")
        conn.commit()
        
        print("✅ Migration successful!")
        print("📝 All existing users now have default password: 'password123'")
        print("💡 You can update passwords through the UI or API")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration: Add Password Column")
    print("=" * 50)
    migrate()
    print("=" * 50)
