#!/usr/bin/env python3
"""
Script to cleanup and sync dataset folder with database
Removes folders that don't have corresponding users in database
"""

import os
import shutil
import sqlite3

DB_PATH = os.path.join("instance", "app.db")
DATASET_DIR = "dataset"

def get_valid_user_ids():
    """Get all valid user IDs from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users ORDER BY id")
    user_ids = [str(row[0]) for row in cursor.fetchall()]
    conn.close()
    return user_ids

def get_dataset_folders():
    """Get all folder names in dataset directory"""
    if not os.path.exists(DATASET_DIR):
        return []
    folders = []
    for item in os.listdir(DATASET_DIR):
        item_path = os.path.join(DATASET_DIR, item)
        if os.path.isdir(item_path) and item.isdigit():
            folders.append(item)
    return folders

def cleanup_orphaned_folders():
    """Remove dataset folders that don't have corresponding users in database"""
    print("=" * 60)
    print("Dataset Cleanup Script")
    print("=" * 60)
    
    # Get valid user IDs from database
    valid_ids = get_valid_user_ids()
    print(f"\n✅ Valid User IDs in Database: {', '.join(valid_ids)}")
    
    # Get existing dataset folders
    dataset_folders = get_dataset_folders()
    print(f"📁 Dataset Folders Found: {', '.join(dataset_folders)}")
    
    # Find orphaned folders
    orphaned = [f for f in dataset_folders if f not in valid_ids]
    
    if not orphaned:
        print("\n✅ No orphaned folders found. Dataset is clean!")
        print("=" * 60)
        return
    
    print(f"\n⚠️  Orphaned Folders (no matching user): {', '.join(orphaned)}")
    
    # Remove orphaned folders
    for folder in orphaned:
        folder_path = os.path.join(DATASET_DIR, folder)
        
        # Count files
        file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        
        print(f"\n🗑️  Removing folder: {folder}")
        print(f"   Path: {folder_path}")
        print(f"   Files: {file_count}")
        
        try:
            shutil.rmtree(folder_path)
            print(f"   ✅ Deleted successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Cleanup completed!")
    print("=" * 60)
    
    # Show final state
    remaining_folders = get_dataset_folders()
    print(f"\n📊 Final State:")
    print(f"   - Users in Database: {len(valid_ids)}")
    print(f"   - Folders in Dataset: {len(remaining_folders)}")
    print(f"   - Match: {'✅ YES' if set(valid_ids) == set(remaining_folders) else '❌ NO'}")

if __name__ == "__main__":
    cleanup_orphaned_folders()
