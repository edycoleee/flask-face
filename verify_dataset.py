#!/usr/bin/env python3
"""
Script to verify dataset before training
Checks if dataset matches database and shows statistics
"""

import os
import sqlite3

DB_PATH = os.path.join("instance", "app.db")
DATASET_DIR = "dataset"

def verify_dataset():
    print("=" * 70)
    print("Dataset Verification for Training")
    print("=" * 70)
    
    # Get users from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 Database Users: {len(users)}")
    print("-" * 70)
    
    total_images = 0
    issues = []
    
    for user_id, name, email in users:
        folder_path = os.path.join(DATASET_DIR, str(user_id))
        
        if not os.path.exists(folder_path):
            print(f"❌ User {user_id} ({name})")
            print(f"   Folder: {folder_path} - NOT FOUND")
            issues.append(f"Missing folder for user {user_id}")
            continue
        
        # Count images
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        image_count = len(files)
        total_images += image_count
        
        status = "✅" if image_count >= 10 else "⚠️ "
        print(f"{status} User {user_id}: {name}")
        print(f"   Email: {email}")
        print(f"   Folder: {folder_path}")
        print(f"   Images: {image_count}")
        
        if image_count < 10:
            issues.append(f"User {user_id} has only {image_count} images (recommended: ≥10)")
        
        print()
    
    # Check for orphaned folders
    if os.path.exists(DATASET_DIR):
        valid_ids = [str(u[0]) for u in users]
        dataset_folders = [f for f in os.listdir(DATASET_DIR) 
                          if os.path.isdir(os.path.join(DATASET_DIR, f)) and f.isdigit()]
        orphaned = [f for f in dataset_folders if f not in valid_ids]
        
        if orphaned:
            print("⚠️  Orphaned Folders (no matching user in database):")
            for folder in orphaned:
                folder_path = os.path.join(DATASET_DIR, folder)
                file_count = len([f for f in os.listdir(folder_path) 
                                if os.path.isfile(os.path.join(folder_path, f))])
                print(f"   - Folder {folder}: {file_count} files")
                issues.append(f"Orphaned folder {folder} found")
            print()
    
    # Summary
    print("=" * 70)
    print("📈 Summary")
    print("=" * 70)
    print(f"Total Users: {len(users)}")
    print(f"Total Images: {total_images}")
    print(f"Average Images per User: {total_images / len(users) if users else 0:.1f}")
    print()
    
    if issues:
        print("⚠️  Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        print("❌ Dataset has issues. Please fix before training!")
        print("   Run: python cleanup_dataset.py")
    else:
        print("✅ Dataset is clean and ready for training!")
    
    print("=" * 70)
    
    return len(issues) == 0

if __name__ == "__main__":
    is_valid = verify_dataset()
    exit(0 if is_valid else 1)
