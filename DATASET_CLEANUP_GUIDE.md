# Dataset Cleanup & Validation Guide

## Problem: Dataset Mismatch

### Symptom
- Database has **3 users** but training detects **4 users**
- Low accuracy because model trains on wrong number of classes
- Training fails or produces incorrect results

### Root Cause
**Orphaned folders** in `dataset/` directory that don't have corresponding users in database.

This happens when:
1. User is deleted from database but folder remains
2. Manual folder manipulation
3. Database reset without cleaning dataset

---

## Solution

### 1. Verify Dataset
Check if dataset matches database:
```bash
python verify_dataset.py
```

**Output Example:**
```
Database Users: 3
Dataset Folders: 3, 2, 1, 4
⚠️ Orphaned Folders: 4
❌ Dataset has issues. Please fix before training!
```

### 2. Clean Dataset
Remove orphaned folders:
```bash
python cleanup_dataset.py
```

**Output Example:**
```
✅ Valid User IDs in Database: 1, 2, 3
📁 Dataset Folders Found: 3, 2, 1, 4
⚠️ Orphaned Folders (no matching user): 4

🗑️ Removing folder: 4
   Path: dataset/4
   Files: 11
   ✅ Deleted successfully

✅ Cleanup completed!
   - Users in Database: 3
   - Folders in Dataset: 3
   - Match: ✅ YES
```

### 3. Verify Again
```bash
python verify_dataset.py
```

Should show:
```
✅ Dataset is clean and ready for training!
```

---

## Prevention

### Automatic Validation
Training service now **automatically validates** dataset before training:

```python
def train(...):
    # Validate dataset before training
    self._validate_dataset()  # ✅ Auto-check
    
    # If orphaned folders exist, training will fail with clear error:
    # "❌ ORPHANED FOLDERS DETECTED: 4
    #  Run: python cleanup_dataset.py to fix this issue."
```

### Manual Cleanup
Always use the API to delete users (not manual file deletion):
```bash
# ✅ CORRECT - Deletes user AND folder
DELETE /api/users/{id}

# ❌ WRONG - Only deletes folder
rm -rf dataset/4
```

---

## Scripts Reference

### verify_dataset.py
- ✅ Check dataset vs database
- ✅ Show statistics
- ✅ List issues
- ✅ Returns exit code 0 (clean) or 1 (issues)

### cleanup_dataset.py
- ✅ Remove orphaned folders
- ✅ Keep only valid user folders
- ✅ Show before/after state
- ✅ Safe - only removes unmatched folders

---

## Best Practices

1. **Before Training:**
   ```bash
   python verify_dataset.py
   ```

2. **If Issues Found:**
   ```bash
   python cleanup_dataset.py
   python verify_dataset.py  # verify again
   ```

3. **Then Train:**
   ```bash
   # Training will auto-validate
   POST /api/training/start
   ```

4. **Regular Maintenance:**
   - Run cleanup after bulk user deletions
   - Verify before important training sessions
   - Keep database and dataset in sync

---

## Troubleshooting

### Issue: "Training detects 4 users but database has 3"
**Solution:** Run `cleanup_dataset.py`

### Issue: "Missing folders for some users"
**Cause:** User exists in database but no folder in dataset
**Solution:** Upload photos for that user, folder will be auto-created

### Issue: "Low training accuracy"
**Possible causes:**
1. Dataset mismatch (run cleanup)
2. Not enough images per user (need ≥10)
3. Poor image quality
4. Similar-looking users

---

## Dataset Structure

### Correct Structure:
```
dataset/
├── 1/           # User ID 1 (exists in DB)
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── ...
├── 2/           # User ID 2 (exists in DB)
│   └── ...
└── 3/           # User ID 3 (exists in DB)
    └── ...
```

### Incorrect Structure (will fail training):
```
dataset/
├── 1/           # User ID 1 ✅
├── 2/           # User ID 2 ✅
├── 3/           # User ID 3 ✅
└── 4/           # ❌ ORPHANED! No user ID 4 in DB
```

---

## Summary

**Always keep dataset synchronized with database:**
- Database = source of truth
- Dataset folders = must match user IDs
- Cleanup = remove orphaned folders
- Validate = check before training

**Quick Fix:**
```bash
python cleanup_dataset.py && python verify_dataset.py
```

Done! 🎉
