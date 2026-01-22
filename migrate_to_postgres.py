#!/usr/bin/env python3
"""
Migration Script: SQLite + NPY → PostgreSQL + pgvector

This script migrates data from the old system:
- SQLite database (instance/app.db)
- NPY embeddings (models/face_db.npy + face_db.json)

To the new system:
- PostgreSQL database with pgvector extension
- Face embeddings stored in face_embeddings table

Usage:
    python migrate_to_postgres.py

Requirements:
    - PostgreSQL must be running with pgvector extension
    - init.sql must have been executed
    - Both SQLite and NPY files must exist
"""

import os
import sys
import sqlite3
import numpy as np
import json
import psycopg2
import psycopg2.extras
from pathlib import Path
from datetime import datetime

# PostgreSQL connection config
PG_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB', 'face_db'),
    'user': os.getenv('POSTGRES_USER', 'sultan'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Sulfat123#!'),
    'host': os.getenv('POSTGRES_HOST', '192.168.171.184'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# SQLite database path
SQLITE_DB_PATH = 'instance/app.db'

# NPY database paths
NPY_DB_PATH = 'models/face_db.npy'
NPY_META_PATH = 'models/face_db.json'

def check_files_exist():
    """Check if required files exist"""
    print("Checking required files...")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        return False
    print(f"✓ SQLite database found: {SQLITE_DB_PATH}")
    
    if not os.path.exists(NPY_DB_PATH):
        print(f"⚠ NPY database not found: {NPY_DB_PATH}")
        print("  (This is OK if you haven't trained the model yet)")
    else:
        print(f"✓ NPY database found: {NPY_DB_PATH}")
    
    if not os.path.exists(NPY_META_PATH):
        print(f"⚠ NPY metadata not found: {NPY_META_PATH}")
        print("  (This is OK if you haven't trained the model yet)")
    else:
        print(f"✓ NPY metadata found: {NPY_META_PATH}")
    
    return True

def test_postgres_connection():
    """Test PostgreSQL connection"""
    print("\nTesting PostgreSQL connection...")
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ PostgreSQL connected: {version[:50]}...")
        
        # Check pgvector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cursor.fetchone():
            print("✓ pgvector extension is installed")
        else:
            print("❌ pgvector extension not found!")
            print("   Please run init.sql first!")
            conn.close()
            return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        return False

def migrate_users():
    """Migrate users table from SQLite to PostgreSQL"""
    print("\n" + "=" * 60)
    print("MIGRATING USERS")
    print("=" * 60)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all users
    sqlite_cursor.execute("SELECT * FROM users ORDER BY id")
    users = sqlite_cursor.fetchall()
    
    if not users:
        print("⚠ No users found in SQLite database")
        sqlite_conn.close()
        return 0
    
    print(f"Found {len(users)} users in SQLite")
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    # Migrate each user
    migrated = 0
    for user in users:
        try:
            # Check if user already exists
            pg_cursor.execute("SELECT id FROM users WHERE email = %s", (user['email'],))
            existing = pg_cursor.fetchone()
            
            if existing:
                print(f"  ⊗ User already exists: {user['email']} (ID: {existing[0]})")
                continue
            
            # Insert user
            pg_cursor.execute("""
                INSERT INTO users (id, name, email, password, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user['id'],
                user['name'],
                user['email'],
                user['password'],
                datetime.now()
            ))
            
            print(f"  ✓ Migrated: {user['name']} ({user['email']})")
            migrated += 1
            
        except Exception as e:
            print(f"  ✗ Failed to migrate user {user['email']}: {str(e)}")
    
    # Reset sequence to max ID + 1
    pg_cursor.execute("SELECT MAX(id) FROM users")
    max_id = pg_cursor.fetchone()[0]
    if max_id:
        pg_cursor.execute(f"SELECT setval('users_id_seq', {max_id + 1})")
        print(f"\n✓ Reset users ID sequence to {max_id + 1}")
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"\n✅ Migrated {migrated} users")
    return migrated

def migrate_photos():
    """Migrate photos table from SQLite to PostgreSQL"""
    print("\n" + "=" * 60)
    print("MIGRATING PHOTOS")
    print("=" * 60)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all photos
    sqlite_cursor.execute("SELECT * FROM photos ORDER BY id")
    photos = sqlite_cursor.fetchall()
    
    if not photos:
        print("⚠ No photos found in SQLite database")
        sqlite_conn.close()
        return 0
    
    print(f"Found {len(photos)} photos in SQLite")
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    # Migrate each photo
    migrated = 0
    for photo in photos:
        try:
            # Check if photo filepath already exists
            pg_cursor.execute("SELECT id FROM photos WHERE filepath = %s", (photo['filepath'],))
            existing = pg_cursor.fetchone()
            
            if existing:
                print(f"  ⊗ Photo already exists: {photo['filename']}")
                continue
            
            # Insert photo
            pg_cursor.execute("""
                INSERT INTO photos (id, user_id, filename, filepath, width, height, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                photo['id'],
                photo['user_id'],
                photo['filename'],
                photo['filepath'],
                photo['width'],
                photo['height'],
                photo['created_at'] if photo['created_at'] else datetime.now()
            ))
            
            print(f"  ✓ Migrated: {photo['filename']} (User ID: {photo['user_id']})")
            migrated += 1
            
        except Exception as e:
            print(f"  ✗ Failed to migrate photo {photo['filename']}: {str(e)}")
    
    # Reset sequence
    pg_cursor.execute("SELECT MAX(id) FROM photos")
    max_id = pg_cursor.fetchone()[0]
    if max_id:
        pg_cursor.execute(f"SELECT setval('photos_id_seq', {max_id + 1})")
        print(f"\n✓ Reset photos ID sequence to {max_id + 1}")
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"\n✅ Migrated {migrated} photos")
    return migrated

def migrate_embeddings():
    """Migrate face embeddings from NPY to PostgreSQL pgvector"""
    print("\n" + "=" * 60)
    print("MIGRATING FACE EMBEDDINGS")
    print("=" * 60)
    
    if not os.path.exists(NPY_DB_PATH) or not os.path.exists(NPY_META_PATH):
        print("⚠ NPY database not found. Skipping embeddings migration.")
        print("  You can rebuild embeddings after migration using /api/training/start")
        return 0
    
    # Load NPY data
    print("Loading NPY database...")
    embeddings = np.load(NPY_DB_PATH)
    with open(NPY_META_PATH, 'r') as f:
        metadata = json.load(f)
    
    users = metadata.get('users', [])
    print(f"Found {len(embeddings)} embeddings for {len(users)} users")
    
    if len(embeddings) != len(users):
        print(f"⚠ Warning: Mismatch between embeddings ({len(embeddings)}) and users ({len(users)})")
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    # Migrate embeddings
    migrated = 0
    for idx, user_id_str in enumerate(users):
        try:
            user_id = int(user_id_str)
            embedding = embeddings[idx].tolist()  # Convert numpy array to list
            
            # Check if user exists
            pg_cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not pg_cursor.fetchone():
                print(f"  ⊗ Skipping embedding for non-existent user ID: {user_id}")
                continue
            
            # Check if embedding already exists for this user
            pg_cursor.execute("SELECT id FROM face_embeddings WHERE user_id = %s", (user_id,))
            if pg_cursor.fetchone():
                print(f"  ⊗ Embedding already exists for user ID: {user_id}")
                continue
            
            # Insert embedding
            pg_cursor.execute("""
                INSERT INTO face_embeddings (user_id, embedding, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                embedding,
                datetime.now(),
                datetime.now()
            ))
            
            print(f"  ✓ Migrated embedding for user ID: {user_id}")
            migrated += 1
            
        except Exception as e:
            print(f"  ✗ Failed to migrate embedding for user {user_id_str}: {str(e)}")
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    
    print(f"\n✅ Migrated {migrated} embeddings")
    return migrated

def verify_migration():
    """Verify migration results"""
    print("\n" + "=" * 60)
    print("VERIFYING MIGRATION")
    print("=" * 60)
    
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Count users
    pg_cursor.execute("SELECT COUNT(*) as count FROM users")
    users_count = pg_cursor.fetchone()['count']
    print(f"✓ Users in PostgreSQL: {users_count}")
    
    # Count photos
    pg_cursor.execute("SELECT COUNT(*) as count FROM photos")
    photos_count = pg_cursor.fetchone()['count']
    print(f"✓ Photos in PostgreSQL: {photos_count}")
    
    # Count embeddings
    pg_cursor.execute("SELECT COUNT(*) as count FROM face_embeddings")
    embeddings_count = pg_cursor.fetchone()['count']
    print(f"✓ Embeddings in PostgreSQL: {embeddings_count}")
    
    # Show sample data
    if users_count > 0:
        print("\nSample users:")
        pg_cursor.execute("SELECT id, name, email FROM users LIMIT 3")
        for user in pg_cursor.fetchall():
            print(f"  - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
    
    pg_cursor.close()
    pg_conn.close()

def main():
    """Main migration function"""
    print("=" * 60)
    print("MIGRATION: SQLite + NPY → PostgreSQL + pgvector")
    print("=" * 60)
    
    # Step 1: Check files
    if not check_files_exist():
        print("\n❌ Migration aborted: Required files not found")
        sys.exit(1)
    
    # Step 2: Test PostgreSQL connection
    if not test_postgres_connection():
        print("\n❌ Migration aborted: PostgreSQL connection failed")
        sys.exit(1)
    
    # Step 3: Confirm migration
    print("\n" + "=" * 60)
    print("⚠  WARNING: This will copy data to PostgreSQL")
    print("   Existing data with same IDs/emails will be skipped")
    print("=" * 60)
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled")
        sys.exit(0)
    
    # Step 4: Migrate data
    users_migrated = migrate_users()
    photos_migrated = migrate_photos()
    embeddings_migrated = migrate_embeddings()
    
    # Step 5: Verify
    verify_migration()
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print(f"✓ Users migrated: {users_migrated}")
    print(f"✓ Photos migrated: {photos_migrated}")
    print(f"✓ Embeddings migrated: {embeddings_migrated}")
    print("\n⚠  IMPORTANT NEXT STEPS:")
    print("1. Update your app config to use PostgreSQL")
    print("2. Test all endpoints (users, photos, auth, prediction)")
    print("3. If embeddings were skipped, rebuild with /api/training/start")
    print("4. Backup your old SQLite and NPY files")
    print("=" * 60)

if __name__ == '__main__':
    main()
