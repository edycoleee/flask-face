# FLASK FACE RECOGNITION

### FLASK

```py
# Update sistem
sudo apt update && sudo apt upgrade -y

# Buat virtual environment
python3 -m venv venv  # Windows: python -m venv venv

# Aktifkan virtual environment
source venv/bin/activate # Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

pip install -r requirements.txt

python run.py

git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/edycoleee/flask-face.git
git push -u origin main

```
---
## CRUD USER

**User API** dan **Photo API** 

---

**User API Specs**

| Endpoint | Method | Deskripsi | Request Body | Response | Status |
|---------|--------|-----------|--------------|----------|--------|
| `/api/users` | **POST** | Membuat user baru + membuat folder dataset otomatis | `{ "name": "string", "email": "string" }` | `{ id, name, email }` | `201 Created` |
| `/api/users` | **GET** | Mengambil semua user | – | `[ { id, name, email } ]` | `200 OK` |
| `/api/users/<id>` | **GET** | Mengambil detail user berdasarkan ID | – | `{ id, name, email }` | `200 OK` / `404 Not Found` |
| `/api/users/<id>` | **PUT** | Update data user | `{ "name": "string", "email": "string" }` | `{ id, name, email }` | `200 OK` / `404 Not Found` |
| `/api/users/<id>` | **DELETE** | Menghapus user + menghapus folder dataset otomatis | – | `{ "message": "User deleted" }` | `200 OK` / `404 Not Found` |

---

**Photo API Specs**

| Endpoint | Method | Deskripsi | Request Body | Response | Status |
|---------|--------|-----------|--------------|----------|--------|
| `/api/photos/<user_id>/upload` | **POST** | Upload 1 foto JPG/PNG, auto‑resize (224×224), simpan metadata ke DB | `multipart/form-data` → `file: image` | `{ id, user_id, filename, filepath, width, height, created_at }` | `201 Created` / `400 Bad Request` |
| `/api/photos/<user_id>/upload/multiple` | **POST** | Upload banyak foto sekaligus (JPG/PNG), auto‑resize, simpan metadata per foto | `multipart/form-data` → `files[]: image[]` | `{ "files": [ metadata... ] }` | `201 Created` / `400 Bad Request` |

---

**Metadata Foto yang Disimpan**

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | integer | ID foto |
| `user_id` | integer | ID user pemilik foto |
| `filename` | string | Nama file asli |
| `filepath` | string | Lokasi file tersimpan |
| `width` | integer | Lebar hasil resize (default 224) |
| `height` | integer | Tinggi hasil resize (default 224) |
| `created_at` | datetime | Timestamp upload |

---

## X‑Fields

X‑Fields itu sebenarnya fitur **standar Flask‑RESTX** (bukan error, bukan header wajib). Banyak orang bingung karena muncul otomatis di Swagger UI.

Berikut penjelasan yang paling jelas dan ringkas.

---

**X‑Fields** di Swagger RESTX?

**X‑Fields** adalah *optional response field mask*.

Artinya:

- Kamu bisa meminta API hanya mengembalikan **field tertentu** dari response.
- Ini berguna kalau response besar, tapi kamu hanya butuh sebagian.
- Dipakai lewat **HTTP header**, bukan query param.

---

# 📌 Contoh Penggunaan

Misalnya endpoint `/users` mengembalikan:

```json
{
  "id": 1,
  "name": "Edy",
  "email": "edy@example.com",
  "created_at": "2024-01-01"
}
```

Kalau kamu hanya ingin `name` dan `email`, kamu bisa kirim header:

```
X-Fields: name,email
```

Maka response berubah menjadi:

```json
{
  "name": "Edy",
  "email": "edy@example.com"
}
```

---

# 📌 Kenapa muncul di Swagger?

Karena Flask‑RESTX otomatis menambahkan fitur ini untuk semua endpoint yang memakai:

- `@api.marshal_with`
- `@api.marshal_list_with`

Swagger menampilkan header itu supaya developer tahu bahwa API mendukung *field masking*.

---

# 📌 Apakah wajib dipakai?

Tidak.  
Kalau kamu tidak mengisi apa‑apa, API berjalan normal seperti biasa.

---

# 📌 Apakah perlu dihapus?

Tidak perlu.  
Ini fitur bawaan yang aman dan tidak mengganggu.

Kalau kamu ingin menghilangkannya dari Swagger, itu juga bisa — tapi biasanya tidak perlu.

---

## 🧠 FASE 4: InsightFace

```
Image → InsightFace → Face Detection → Embedding Extraction → 
Cosine Similarity → Best Match
```

### Embedding Dimension
- **Size:** 512-D vector
- **Model:** MobileFaceNet (buffalo_l)
- **Normalized:** L2 normalized
- **Similarity:** Cosine similarity

---

## 📝 Common Request/Response Examples

### 1️⃣ Create User (First Step)
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@email.com", "password": "secure123"}'
```
**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@email.com",
  "password": "secure123"
}
```
**Note**: Folder `dataset/1/` otomatis dibuat saat user baru berhasil dibuat.

---

### 2️⃣ Upload Photos (Second Step)
Upload minimal 5-10 foto wajah untuk user tersebut:

**Single Photo:**
```bash
curl -X POST http://localhost:5000/api/photos/1/upload \
  -F "file=@photo1.jpg"
```

**Multiple Photos (Recommended):**
```bash
curl -X POST http://localhost:5000/api/photos/1/upload/multiple \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@photo3.jpg" \
  -F "files=@photo4.jpg" \
  -F "files=@photo5.jpg"
```
**Response:**
```json
{
  "uploaded": 5,
  "files": [
    {
      "id": 1,
      "user_id": 1,
      "filename": "photo1.jpg",
      "filepath": "dataset/1/photo1.jpg",
      "width": 224,
      "height": 224
    }
  ]
}
```

---

### 3️⃣ Build Face Embeddings

#### **Option A: Incremental Training (⚡ RECOMMENDED - 1-3 seconds)**
Untuk user yang baru dibuat atau retrain user dengan accuracy jelek:

```bash
curl -X POST http://localhost:5000/api/training/incremental \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

**Response:**
```json
{
  "success": true,
  "message": "Embeddings built for user 1",
  "data": {
    "user_id": 1,
    "faces_processed": 5,
    "embeddings_created": 5,
    "processing_time_seconds": 1.8,
    "timestamp": "2026-01-22T10:00:00"
  }
}
```

**✅ Use incremental training when:**
- Adding a new user
- User has poor verification accuracy (retrain)
- User uploaded new training photos
- Want fast update (1-3 seconds)

**📊 Performance:**
- **Very Fast**: 1-3 seconds per user
- **Database**: PostgreSQL with pgvector
- **Action**: Deletes old embeddings, creates new ones
- **Impact**: Only affects specified user

---

#### **Option B: Full Rebuild (10-30 seconds)**
Untuk maintenance atau rebuild seluruh database:

```bash
curl -X POST http://localhost:5000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "success": true,
  "message": "Face database built successfully",
  "data": {
    "num_data": 25,
    "num_classes": 5,
    "total_faces": 25,
    "training_time_seconds": 18.5,
    "training_time_minutes": 0.31,
    "model_path": "models/face_db.npy",
    "timestamp": "2026-01-22T10:00:00"
  }
}
```

**✅ Use full rebuild when:**
- Database maintenance
- Cleanup orphaned data
- First-time setup
- Want to rebuild ALL users

**⚠️ Note:** 
- Incremental training is **10x faster** for single user updates
- Use full rebuild only when necessary (maintenance, cleanup)

---

### 4️⃣ Face Prediction (1:N Recognition)
Test apakah wajah bisa dikenali (search all users):

```bash
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@test_face.jpg"
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "user_id": 1,
    "name": "John Doe",
    "email": "john@email.com",
    "confidence": 98.5,
    "similarity": 0.9850,
    "all_predictions": [
      {"user_id": 1, "name": "John Doe", "confidence": 98.5, "similarity": 0.9850},
      {"user_id": 2, "name": "Jane Smith", "confidence": 45.2, "similarity": 0.4520}
    ]
  }
}
```

**Use case:** "Who is this person?" (search all users)

---

### 5️⃣ Password Login
```bash
curl -X POST http://localhost:5000/api/auth/login-pass-verify \
  -H "Content-Type: application/json" \
  -d '{"email": "john@email.com", "password": "secure123"}'
```
**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user_id": 1,
    "name": "John Doe",
    "email": "john@email.com",
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "expires_at": "2026-01-22T10:00:00"
  }
}
```

---

### 6️⃣ Face Verification Login (⚡ OPTIMIZED - 1:1 Verification)
**10x-100x faster** dengan pgvector (constant O(1) time):

```bash
curl -X POST http://localhost:5000/api/auth/login-face-verify \
  -F "user_id=1" \
  -F "file=@face.jpg"
```
**Response:**
```json
{
  "status": "success",
  "message": "Face verification successful",
  "data": {
    "match": true,
    "user_id": 1,
    "name": "John Doe",
    "email": "john@email.com",
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "confidence": 98.5,
    "similarity": 0.9850,
    "method": "PostgreSQL pgvector (1:1)",
    "expires_at": "2026-01-22T10:00:00"
  }
}
```

**🚀 Performance Comparison:**

| Database Size | 1:N Prediction | 1:1 Verification (pgvector) |
|---------------|----------------|----------------------------|
| 10 users      | 0.5s           | **0.2s** (2.5x faster)     |
| 100 users     | 5.0s           | **0.2s** (25x faster)      |
| 1000 users    | 50.0s          | **0.2s** (250x faster)     |

**Use case:** "Is this person John Doe?" (verify specific user)

---

### 7️⃣ Retrain User with Poor Accuracy

Jika user mengalami verification failure atau accuracy rendah:

```bash
# Step 1: Upload foto baru yang lebih baik
curl -X POST http://localhost:5000/api/photos/1/upload/multiple \
  -F "files=@better_photo1.jpg" \
  -F "files=@better_photo2.jpg" \
  -F "files=@better_photo3.jpg"

# Step 2: Retrain user tersebut (1-3 detik)
curl -X POST http://localhost:5000/api/training/incremental \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Step 3: Test verification lagi
curl -X POST http://localhost:5000/api/auth/login-face-verify \
  -F "user_id=1" \
  -F "file=@test_face.jpg"
```

**💡 Tips for better accuracy:**
- Upload 10-20 photos per user
- Vary angles (frontal, slight left, slight right)
- Good lighting (not too dark/bright)
- Multiple expressions (neutral, smile)
- With/without glasses (if user wears glasses)
- High resolution (min 640x480)

---

## 🚀 Quick Start: Menambah User Baru

Berikut langkah lengkap untuk menambah user baru dari awal:

### **Opsi A: Incremental Training (⚡ FAST - Recommended)**

```bash
# Step 1: Buat user baru
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@email.com", "password": "pass123"}'

# Response akan berisi ID user (misalnya: {"id": 3, ...})

# Step 2: Upload foto-foto wajah (minimal 5-10 foto)
curl -X POST http://localhost:5000/api/photos/3/upload/multiple \
  -F "files=@alice1.jpg" \
  -F "files=@alice2.jpg" \
  -F "files=@alice3.jpg" \
  -F "files=@alice4.jpg" \
  -F "files=@alice5.jpg"

# Step 3: Build embeddings untuk user ini saja (FAST: 1-3 detik!)
curl -X POST http://localhost:5000/api/training/incremental \
  -H "Content-Type: application/json" \
  -d '{"user_id": 3}'

# Step 4: Test verification
curl -X POST http://localhost:5000/api/auth/login-face-verify \
  -F "user_id=3" \
  -F "file=@alice_test.jpg"
```

**⚡ Performance:** 1-3 seconds (only builds embeddings for user 3)

---

### **Opsi B: Full Rebuild (Slower - 10-30 detik)**

Gunakan ini jika:
- First-time setup
- Database maintenance
- Multiple users added at once

```bash
# Step 1: Buat user baru
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@email.com", "password": "pass123"}'

# Step 2: Upload foto-foto wajah
curl -X POST http://localhost:5000/api/photos/3/upload/multiple \
  -F "files=@alice1.jpg" \
  -F "files=@alice2.jpg" \
  -F "files=@alice3.jpg" \
  -F "files=@alice4.jpg" \
  -F "files=@alice5.jpg"

# Step 3: Rebuild seluruh database (SLOW: 10-30 detik)
curl -X POST http://localhost:5000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{}'

# Step 4: Test prediction
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@alice_test.jpg"
```

**🐢 Performance:** 10-30 seconds (rebuilds ALL users)

---

### **Opsi C: Via Web Interface (Easiest)**

1. **Buka browser**: `http://localhost:5000`
2. **Tab "Users"**: 
   - Klik "Create User"
   - Isi: Name, Email, Password
   - Klik "Submit"
   - Note: ID user yang baru dibuat
3. **Tab "Photos"**:
   - Pilih user yang baru dibuat
   - Klik "Choose Files" atau "Open Camera"
   - Upload minimal 5-10 foto berbeda (berbagai sudut, ekspresi)
4. **Tab "Database Build"**:
   - **Pilih mode "⚡ Incremental (1-3s)"** ← RECOMMENDED
   - Masukkan user ID yang baru dibuat
   - Klik "Build Embeddings for This User"
   - Tunggu 1-3 detik ✅
   
   ATAU
   
   - Pilih mode "🔄 Full Rebuild (10-30s)"
   - Klik "Rebuild All Users Now"
   - Tunggu 10-30 detik
5. **Tab "Face Verification"**:
   - Masukkan email user
   - Upload foto test
   - Klik "Verify Face"
   - Login berhasil! 🎉

---

### **📋 Checklist Menambah User Baru**

- ✅ Buat user baru dengan name, email, password
- ✅ Folder `dataset/<user_id>/` otomatis dibuat
- ✅ Upload minimal **5-10 foto** wajah yang jelas
- ✅ Foto dari **berbagai sudut** (depan, samping, berbagai ekspresi)
- ✅ Kualitas foto baik (pencahayaan cukup, fokus jelas)
- ✅ **Build embeddings** menggunakan **incremental training** (1-3s) ⚡
- ✅ Test verification untuk validasi

---

### **⚠️ Tips Penting**

**Training Mode Selection:**
- ✅ **Use Incremental Training (1-3s)** untuk:
  - Menambah user baru
  - Retrain user dengan accuracy jelek
  - Update foto user
  - Perubahan satu user saja
- ✅ **Use Full Rebuild (10-30s)** untuk:
  - First-time setup
  - Database maintenance
  - Cleanup orphaned data
  - Multiple users added at once

**Photo Quality:**
- **Minimal 5 foto** per user untuk akurasi baik
- **Lebih banyak foto = lebih akurat** (10-20 foto ideal)
- **Variasi penting**: foto dengan kacamata/tanpa, tersenyum/serius, sudut berbeda
- **Pencahayaan**: Hindari foto terlalu gelap atau overexposed
- **Format**: JPG atau PNG, sistem auto-resize ke 224×224
- **Resolusi minimal**: 640×480 pixels

**Retrain User:**
- Upload foto baru yang lebih baik
- Jalankan incremental training untuk user tersebut
- Old embeddings otomatis dihapus
- New embeddings dibuat dari semua foto (lama + baru)

---

### **🔄 Workflow Lengkap**

#### **Fast Workflow (Incremental - 1-3 seconds per user):**
```
1. CREATE USER
   ↓
2. UPLOAD PHOTOS (5-10 foto minimum)
   ↓
3. INCREMENTAL TRAINING (1-3 detik) ⚡
   ↓
4. READY FOR VERIFICATION (1:1 - 0.2s)
```

#### **Complete Workflow (Full Rebuild - 10-30 seconds):**
```
1. CREATE MULTIPLE USERS
   ↓
2. UPLOAD PHOTOS FOR ALL USERS
   ↓
3. FULL REBUILD (10-30 detik)
   ↓
4. READY FOR PREDICTION (1:N) & VERIFICATION (1:1)
```

---

### **🎯 Best Practices**

1. **For new users:** Use **incremental training** (10x faster)
2. **For verification:** Use **face verification** endpoint (1:1, constant time)
3. **For recognition:** Use **prediction** endpoint (1:N, linear time)
4. **For poor accuracy:** Upload better photos + retrain incremental
5. **For maintenance:** Use full rebuild occasionally (cleanup)

---
