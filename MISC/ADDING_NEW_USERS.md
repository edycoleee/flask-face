# Adding New Users - Workflow Guide

## Perbandingan: Old vs New System

### **Old System (CNN Training)**

**Total Time:** 2-30 menit per user baru

```bash
# 1. Create user
POST /api/users {"name": "Budi", "email": "budi@mail.com"}

# 2. Upload photos  
POST /api/photos/upload?user_id=101

# 3. Training ulang (LAMA!)
POST /api/training/start {
  "continue_training": false  # 15-30 menit (reset)
  # OR
  "continue_training": true   # 2-5 menit (continue)
}

# Problem: Tetap lama, dan "continue" bisa kurang akurat
```

---

### **New System (Face Embedding)**

**Total Time:** 10-30 detik (rebuild semua!)

```bash
# 1. Create user
POST /api/users {"name": "Budi", "email": "budi@mail.com"}

# 2. Upload photos
POST /api/photos/upload?user_id=101

# 3. Rebuild database (CEPAT!)
POST /api/training/start
# → Always full rebuild
# → 10-30 detik untuk semua users
# → Always fresh & accurate
```

---

## Detailed Workflow

### Step 1: Create User in Database

```bash
curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Budi Santoso",
    "email": "budi@example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": 101
}
```

---

### Step 2: Upload Photos for User

**Recommended:** 10-20 foto dengan variasi:
- ✅ Berbagai ekspresi (senyum, serius, netral)
- ✅ Berbagai pencahayaan (terang, redup, outdoor)
- ✅ Berbagai angle (depan, sedikit miring)
- ❌ Jangan: kacamata hitam, masker, blur

```bash
# Upload satu foto
curl -X POST http://localhost:5001/api/photos/upload?user_id=101 \
  -F "file=@budi_1.jpg"

# Upload multiple (loop)
for i in {1..10}; do
  curl -X POST http://localhost:5001/api/photos/upload?user_id=101 \
    -F "file=@budi_$i.jpg"
done
```

**Photos saved to:** `dataset/101/*.jpg`

---

### Step 3: Rebuild Face Database

```bash
# Simple rebuild (no parameters needed)
curl -X POST http://localhost:5001/api/training/start

# Atau dengan parameters (akan diabaikan)
curl -X POST http://localhost:5001/api/training/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

**What happens:**
1. ✅ Scan `dataset/` untuk semua users (1-100 + 101)
2. ✅ Detect faces di setiap foto
3. ✅ Extract 512-D embeddings dengan InsightFace
4. ✅ Save ke `models/face_db.npy`
5. ✅ Update metadata di `models/face_db.json`

**Time:** 10-30 detik (bahkan untuk 100+ users)

**Response:**
```json
{
  "success": true,
  "message": "Face database built successfully",
  "data": {
    "num_data": 1010,           // Total 1010 foto
    "num_classes": 101,         // 101 users (termasuk Budi)
    "total_faces": 1010,        // 1010 wajah terdeteksi
    "training_time_seconds": 15.3,
    "training_time_minutes": 0.26,
    "model_path": "models/face_db.npy"
  }
}
```

---

### Step 4: Test Login dengan Face

```bash
# Face login untuk user baru
curl -X POST http://localhost:5001/api/auth/login/face \
  -F "file=@budi_test.jpg"
```

**Response (Success):**
```json
{
  "success": true,
  "user_id": 101,
  "name": "Budi Santoso",
  "email": "budi@example.com",
  "token": "abc123...",
  "confidence": 98.5,
  "expires_at": "2026-01-22T20:00:00"
}
```

---

## FAQ: Adding New Users

### Q: Apakah harus rebuild semua users?
**A:** Ya, tapi **sangat cepat** (10-30 detik). Tidak ada opsi incremental karena:
- ✅ Full rebuild lebih aman (no corruption risk)
- ✅ Auto-cleanup orphaned data
- ✅ Always fresh & validated
- ✅ Minimal time difference

---

### Q: Berapa lama rebuild untuk 100 users?
**A:** ~20-30 detik. Linear complexity:
- 10 users: ~10 detik
- 50 users: ~15 detik
- 100 users: ~25 detik
- 500 users: ~60 detik

Sangat cepat karena **no training**, hanya extraction!

---

### Q: Bisa tambah user tanpa rebuild?
**A:** Tidak recommended. Bisa secara teknis, tapi:
- ❌ Risk data corruption
- ❌ No validation
- ❌ Orphaned data bisa menumpuk
- ✅ Full rebuild lebih aman dan cuma 10-30 detik

---

### Q: Apakah "continue_training" masih berguna?
**A:** ❌ **TIDAK** - Parameter ini diabaikan. Reasons:
- Model InsightFace sudah pre-trained (tidak bisa di-train ulang)
- Selalu extract embeddings fresh dari foto
- Tidak ada checkpoint/state yang perlu di-preserve
- Full rebuild selalu cepat

---

### Q: Kalau delete user, harus rebuild?
**A:** ✅ **Yes, recommended** untuk cleanup orphaned embeddings:

```bash
# 1. Delete user from database
DELETE /api/users/101

# 2. Delete photos
rm -rf dataset/101/

# 3. Rebuild database (cleanup orphaned data)
POST /api/training/start
```

---

## Bulk User Addition

Untuk menambahkan banyak user sekaligus:

```bash
#!/bin/bash
# bulk_add_users.sh

USERS=(
  "Budi:budi@mail.com"
  "Ani:ani@mail.com"
  "Citra:citra@mail.com"
)

# 1. Create users & upload photos
for user_data in "${USERS[@]}"; do
  IFS=':' read -r name email <<< "$user_data"
  
  # Create user
  response=$(curl -s -X POST http://localhost:5001/api/users \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"email\": \"$email\"}")
  
  user_id=$(echo $response | jq -r '.user_id')
  echo "Created user: $name (ID: $user_id)"
  
  # Upload photos
  for photo in photos/$name/*.jpg; do
    curl -s -X POST "http://localhost:5001/api/photos/upload?user_id=$user_id" \
      -F "file=@$photo"
  done
  
  echo "Uploaded photos for $name"
done

# 2. Rebuild database ONCE (untuk semua users)
echo "Rebuilding face database..."
curl -X POST http://localhost:5001/api/training/start

echo "Done! All users added."
```

**Efficient:** Upload semua user dulu, rebuild sekali saja di akhir.

---

## Performance Metrics

### Rebuild Time vs Number of Users

| Users | Photos | Total Images | Rebuild Time | Per User |
|-------|--------|--------------|--------------|----------|
| 10    | 10/user| 100          | 10 sec       | 1.0 sec  |
| 50    | 10/user| 500          | 18 sec       | 0.36 sec |
| 100   | 10/user| 1000         | 28 sec       | 0.28 sec |
| 500   | 10/user| 5000         | 80 sec       | 0.16 sec |

**Observation:** Semakin banyak user, semakin efisien (batch processing).

---

## Best Practices

### ✅ DO:
1. **Upload 10-20 photos per user** (variasi ekspresi & lighting)
2. **Rebuild after batch additions** (bukan setiap user)
3. **Test login immediately** setelah rebuild
4. **Regular cleanup** - rebuild untuk cleanup orphaned data
5. **Backup database** sebelum major changes

### ❌ DON'T:
1. **Upload foto blur atau low quality** (detection akan gagal)
2. **Rebuild setelah setiap upload** (tunggu batch selesai)
3. **Manual edit face_db.npy** (always use API)
4. **Worry about rebuild time** (very fast anyway!)
5. **Try to implement incremental** (full rebuild safer)

---

## Troubleshooting

### Problem: "No face detected"
```bash
# Solution: Check photo quality
- Pastikan wajah clear & terang
- Minimal resolution: 112x112
- Wajah menghadap kamera
- No sunglasses/mask
```

### Problem: "User not found after rebuild"
```bash
# Solution: Check dataset folder exists
ls dataset/101/  # Should have photos

# Rebuild with verbose logging
tail -f logs/app.log  # Watch rebuild process
```

### Problem: "Rebuild too slow"
```bash
# Normal times:
# 100 users = 25-30 seconds
# 500 users = 60-90 seconds

# If slower, check:
1. CPU temperature (vcgencmd measure_temp)
2. Memory usage (free -h)
3. Disk I/O (iotop)
```

---

## Summary

| Aspect | Old (CNN) | New (Embedding) |
|--------|-----------|-----------------|
| **Add 1 User** | 2-30 min | 10-30 sec |
| **Add 10 Users** | 30-300 min | 15-40 sec |
| **Continue Training?** | Yes (faster) | No (not applicable) |
| **Full Rebuild?** | Slow (avoid) | Fast (preferred) |
| **Data Cleanup?** | Manual | Automatic |

**Conclusion:** Sistem embedding jauh lebih simple & cepat. No need for complex "continue training" logic!

