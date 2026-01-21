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

## 🧠 FASE 4: CNN Model Training

**Training API** untuk train model face recognition dengan MobileNetV2.

### Training Endpoint

| Endpoint | Method | Deskripsi | Request Body | Response | Status |
|---------|--------|-----------|--------------|----------|--------|
| `/api/training/start` | **POST** | Mulai training model CNN | `{ "epochs": 50, "batch_size": 16, "validation_split": 0.2, "continue_training": false }` | Training stats & model info | `200 OK` / `500 Error` |
| `/api/training/status` | **GET** | Check model status & accuracy | – | Model info & metrics | `200 OK` / `404 Not Found` |

**Model Architecture**: MobileNetV2 (pre-trained, transfer learning)  
**Input**: Images dari `dataset/<user_id>/` folder  
**Output**: `models/model.h5`, `models/label_map.json`, `models/accuracy.json`

---

## 🔮 FASE 5: Face Recognition Prediction

**Prediction API** untuk identifikasi wajah dari foto.

### Prediction Endpoints

| Endpoint | Method | Deskripsi | Request Body | Response | Status |
|---------|--------|-----------|--------------|----------|--------|
| `/api/face/predict` | **POST** | Predict user dari foto wajah | `multipart/form-data` → `file: image` | `{ user_id, name, email, confidence, all_predictions }` | `200 OK` / `404 Model Not Found` |
| `/api/face/model-info` | **GET** | Get model information & status | – | `{ loaded, num_classes, accuracy, ... }` | `200 OK` / `404 Not Found` |

**Prediction Response Example**:
```json
{
  "status": "success",
  "data": {
    "user_id": 2,
    "name": "John Doe",
    "email": "john@example.com",
    "confidence": 98.45,
    "all_predictions": [
      { "user_id": 2, "name": "John Doe", "confidence": 98.45 },
      { "user_id": 3, "name": "Jane Smith", "confidence": 1.23 },
      { "user_id": 4, "name": "Bob Wilson", "confidence": 0.32 }
    ]
  }
}
```

### Testing Prediction
```bash
# Test with image file
./test_prediction.sh path/to/photo.jpg

# Or using curl
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@photo.jpg"
```

---

## � FASE 6: Face Recognition Login

**Authentication API** menggunakan face recognition untuk login.

### Authentication Endpoints

| Endpoint | Method | Deskripsi | Request Body | Response | Status |
|---------|--------|-----------|--------------|----------|--------|
| `/api/auth/login-face` | **POST** | Login dengan face recognition (1:N) | `multipart/form-data` → `file: image` | `{ user_id, name, token, confidence, expires_at }` | `200 OK` / `401 Unauthorized` |
| `/api/auth/login-face-verify` | **POST** | Login dengan face verification (1:1) ⭐ **FASTER** | `user_id (form) + file: image` | `{ match, user_id, name, token, confidence }` | `200 OK` / `403 Forbidden` |
| `/api/auth/verify` | **POST** | Verify token validity | `{ "token": "uuid" }` | `{ user_id, name, email, ... }` | `200 OK` / `401 Invalid` |
| `/api/auth/logout` | **POST** | Logout (deactivate token) | `{ "token": "uuid" }` | `{ "message": "Logout successful" }` | `200 OK` |
| `/api/auth/tokens/<user_id>` | **GET** | Get user's active tokens | – | List of active tokens | `200 OK` |

**2 Login Methods Available:**

**1. Face Recognition (1:N)** - "Siapa kamu?"
```bash
# Input: Hanya foto wajah
# Process: Compare dengan SEMUA user
# Speed: Lambat (depends on jumlah user)
curl -X POST http://localhost:5000/api/auth/login-face \
  -F "file=@face.jpg"
```

**2. Face Verification (1:1)** - "Apakah kamu John?" ⭐ **RECOMMENDED**
```bash
# Input: user_id + foto wajah  
# Process: Verify 1 user specific saja
# Speed: Cepat (constant time)
curl -X POST http://localhost:5000/api/auth/login-face-verify \
  -F "user_id=2" \
  -F "file=@face.jpg"
```

**Why Face Verification (1:1) is Better:**
- ⚡ **Lebih cepat** - O(1) vs O(N)
- 🎯 **Lebih akurat** - Focused comparison
- 💡 **Real use case** - User input email/username dulu
- 🔒 **More secure** - Explicit identity claim

See [FACE_RECOGNITION_VS_VERIFICATION.md](FACE_RECOGNITION_VS_VERIFICATION.md) for detailed comparison.

**Login Process (Recommended):**
1. Upload foto wajah
2. Face recognition (confidence check ≥ 70%)
3. Generate UUID token (24h expiry)
4. Save to database
5. Return token untuk authentication

**Login Response Example:**
```json
{
  "status": "success",
  "data": {
    "user_id": 2,
    "name": "John Doe",
    "email": "john@example.com",
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "confidence": 98.5,
    "expires_at": "2026-01-19T15:30:00"
  }
}
```

### Testing Face Login
```bash
# Complete test workflow
./test_face_login.sh user_face.jpg

# Manual login
curl -X POST http://localhost:5000/api/auth/login-face \
  -F "file=@face.jpg"

# Verify token
curl -X POST http://localhost:5000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN"}'
```

---

## 🖥️ Web Interface

Akses UI lengkap di: `http://localhost:5000`

**4 Tabs Tersedia**:
1. **👥 Users** - Manage users (create, list, edit, delete)
2. **📸 Photos** - Upload photos (single, multiple, camera capture)
3. **🧠 Training** - Train CNN model with config
4. **🔮 Prediction** - Face recognition (upload or camera)

---

## 📚 Documentation

- **PHOTO_API_QUICK_REFERENCE.md** - Quick photo upload reference
- **PHOTO_API_IMPLEMENTATION.md** - Detailed photo API docs
- **UI_DOCUMENTATION.md** - Web interface guide
- **RPI5_MODEL_ANALYSIS.md** - Raspberry Pi 5 performance analysis
- **PREDICTION_DOCUMENTATION.md** - Prediction API & usage guide
- **FACE_LOGIN_DOCUMENTATION.md** - Face login authentication guide
- **COMPLETE_WORKFLOW_GUIDE.md** - Full workflow dari A-Z

---
 
DATASET

https://www.kaggle.com/datasets/olgabelitskaya/yale-face-database

rename file karena butuh gif

```
for f in *.*; do mv "$f" "$f.gif"; done

for %f in (*.*) do ren "%f" "%f.gif"


```

### API SPECIFICATION

Berikut adalah **tabel lengkap semua API endpoints** dengan method, request, dan response:

---

## 📋 Complete API Reference

### 👥 **Users API**

| Endpoint | Method | Request Body | Request Type | Response | Status Code |
|---------|--------|--------------|--------------|----------|-------------|
| `/api/users` | **POST** | `{ "name": "string", "email": "string", "password": "string" }` | `application/json` | `{ "id": 1, "name": "John", "email": "john@email.com", "password": "pass123" }` | `201 Created` |
| `/api/users` | **GET** | – | – | `[ { "id": 1, "name": "John", "email": "john@email.com", "password": "pass123" } ]` | `200 OK` |
| `/api/users/<id>` | **GET** | – | – | `{ "id": 1, "name": "John", "email": "john@email.com", "password": "pass123" }` | `200 OK` / `404 Not Found` |
| `/api/users/<id>` | **PUT** | `{ "name": "string", "email": "string", "password": "string" }` | `application/json` | `{ "id": 1, "name": "John Updated", "email": "new@email.com", "password": "newpass" }` | `200 OK` / `404 Not Found` |
| `/api/users/<id>` | **DELETE** | – | – | `{ "message": "User deleted successfully" }` | `200 OK` / `404 Not Found` |
| `/api/users/email/<email>` | **GET** | – | – | `{ "id": 1, "name": "John", "email": "john@email.com" }` | `200 OK` / `404 Not Found` |

---

### 📸 **Photos API**

| Endpoint | Method | Request Body | Request Type | Response | Status Code |
|---------|--------|--------------|--------------|----------|-------------|
| `/api/photos/<user_id>/upload` | **POST** | `file: image` | `multipart/form-data` | `{ "id": 1, "user_id": 1, "filename": "photo.jpg", "filepath": "dataset/1/photo.jpg", "width": 224, "height": 224, "created_at": "2026-01-20T10:00:00" }` | `201 Created` / `400 Bad Request` |
| `/api/photos/<user_id>/upload/multiple` | **POST** | `files[]: image[]` | `multipart/form-data` | `{ "uploaded": 5, "files": [ {...}, {...} ] }` | `201 Created` / `400 Bad Request` |
| `/api/photos/<user_id>` | **GET** | – | – | `[ { "id": 1, "filename": "photo.jpg", "width": 224, "height": 224, "created_at": "..." } ]` | `200 OK` |
| `/api/photos/<user_id>/<photo_id>` | **DELETE** | – | – | `{ "message": "Photo deleted successfully" }` | `200 OK` / `404 Not Found` |
| `/api/photos/<user_id>/<photo_id>/view` | **GET** | – | – | Image file (binary) | `200 OK` / `404 Not Found` |

---

### 🎓 **Training API**

| Endpoint | Method | Request Body | Request Type | Response | Status Code |
|---------|--------|--------------|--------------|----------|-------------|
| `/api/training/start` | **POST** | `{ "epochs": 50, "batch_size": 16, "validation_split": 0.2, "continue_training": false }` | `application/json` | `{ "status": "success", "message": "Training completed", "accuracy": 0.95, "epochs": 50, "num_classes": 3, "training_time": 45.2 }` | `200 OK` / `500 Error` |
| `/api/training/status` | **GET** | – | – | `{ "training_active": false, "model_exists": true }` | `200 OK` |
| `/api/training/info` | **GET** | – | – | `{ "test_accuracy": 0.95, "epochs": 50, "num_classes": 3, "timestamp": "2026-01-20T10:00:00" }` | `200 OK` / `404 Not Found` |

---

### 🔮 **Prediction API**

| Endpoint | Method | Request Body | Request Type | Response | Status Code |
|---------|--------|--------------|--------------|----------|-------------|
| `/api/face/predict` | **POST** | `file: image` | `multipart/form-data` | `{ "status": "success", "data": { "user_id": 2, "name": "John", "email": "john@email.com", "confidence": 98.5, "all_predictions": [ {...} ] } }` | `200 OK` / `404 Model Not Found` |
| `/api/face/model-info` | **GET** | – | – | `{ "loaded": true, "num_classes": 3, "accuracy": 0.95, "model_path": "models/model.h5" }` | `200 OK` / `404 Not Found` |

---

### 🔐 **Authentication API**

| Endpoint | Method | Request Body | Request Type | Response | Status Code |
|---------|--------|--------------|--------------|----------|-------------|
| `/api/auth/login-face` | **POST** | `file: image` | `multipart/form-data` | `{ "status": "success", "message": "Login successful", "data": { "user_id": 2, "name": "John", "email": "john@email.com", "token": "550e8400-e29b-41d4...", "confidence": 98.5, "expires_at": "2026-01-21T10:00:00" } }` | `200 OK` / `401 Unauthorized` |
| `/api/auth/login-face-verify` | **POST** | `user_id: integer` + `file: image` | `multipart/form-data` | `{ "status": "success", "message": "Face verification successful", "data": { "match": true, "user_id": 2, "name": "John", "token": "550e8400...", "confidence": 98.5 } }` | `200 OK` / `403 Forbidden` |
| `/api/auth/login-pass-verify` | **POST** | `{ "email": "string", "password": "string" }` | `application/json` | `{ "status": "success", "message": "Login successful", "data": { "user_id": 2, "name": "John", "email": "john@email.com", "token": "550e8400...", "expires_at": "2026-01-21T10:00:00" } }` | `200 OK` / `401 Unauthorized` |
| `/api/auth/verify` | **POST** | `{ "token": "uuid-string" }` | `application/json` | `{ "status": "success", "message": "Token is valid", "data": { "user_id": 2, "name": "John", "email": "john@email.com", "confidence": 98.5, "created_at": "...", "expires_at": "..." } }` | `200 OK` / `401 Invalid` |
| `/api/auth/logout` | **POST** | `{ "token": "uuid-string" }` | `application/json` | `{ "status": "success", "message": "Logout successful" }` | `200 OK` / `500 Error` |
| `/api/auth/tokens/<user_id>` | **GET** | – | – | `{ "status": "success", "message": "Found 2 active tokens", "data": [ { "token": "...", "confidence": 98.5, "created_at": "...", "expires_at": "..." } ] }` | `200 OK` |

---

## 📊 API Categories Summary

| Category | Endpoints | Description |
|---------|-----------|-------------|
| **Users** | 6 endpoints | User CRUD + email lookup |
| **Photos** | 5 endpoints | Photo upload & management |
| **Training** | 3 endpoints | Model training & status |
| **Prediction** | 2 endpoints | Face recognition |
| **Authentication** | 6 endpoints | Face login + token management |
| **TOTAL** | **22 endpoints** | Complete face recognition system |

---

## 🔑 Authentication Methods

| Method | Type | Speed | Use Case | Endpoint |
|--------|------|-------|----------|----------|
| **Face Recognition** | 1:N | Slow (O(N)) | "Siapa kamu?" | `/api/auth/login-face` |
| **Face Verification** | 1:1 | Fast (O(1)) ⚡ | "Apakah kamu John?" | `/api/auth/login-face-verify` |
| **Password Login** | Credential | Instant | Traditional login | `/api/auth/login-pass-verify` |

**Recommended**: Use **Face Verification (1:1)** for best performance and accuracy.

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

### 3️⃣ Build Face Database (Third Step)
Setelah semua user punya foto, rebuild database embedding:

```bash
curl -X POST http://localhost:5000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{}'
```
**Note**: Tidak perlu parameter epochs/batch_size lagi (sistem embedding tidak ada training).

**Response:**
```json
{
  "success": true,
  "message": "Face database built successfully",
  "data": {
    "num_data": 25,
    "num_classes": 3,
    "total_faces": 25,
    "training_time_minutes": 0.5,
    "model_path": "models/face_db.npy"
  }
}
```

---

### 4️⃣ Face Prediction
Test apakah wajah bisa dikenali:

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
    "all_predictions": [
      {"user_id": 1, "name": "John Doe", "confidence": 98.5},
      {"user_id": 2, "name": "Jane Smith", "confidence": 1.2}
    ]
  }
}
```

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

### 6️⃣ Face Verification Login (Recommended ⚡)
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
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "confidence": 98.5,
    "expires_at": "2026-01-22T10:00:00"
  }
}
```

---

## 🚀 Quick Start: Menambah User Baru

Berikut langkah lengkap untuk menambah user baru dari awal:

### **Opsi A: Via API (Command Line)**

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

# Step 3: Rebuild face database
curl -X POST http://localhost:5000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{}'

# Step 4: Test prediction
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@alice_test.jpg"
```

### **Opsi B: Via Web Interface (Lebih Mudah)**

1. **Buka browser**: `http://localhost:5000`
2. **Tab "Users"**: 
   - Klik "Create User"
   - Isi: Name, Email, Password
   - Klik "Submit"
3. **Tab "Photos"**:
   - Pilih user yang baru dibuat
   - Klik "Choose Files" atau "Open Camera"
   - Upload minimal 5-10 foto berbeda (berbagai sudut, ekspresi)
4. **Tab "Database Build"**:
   - Klik "Build Database Now"
   - Tunggu proses selesai (~10-30 detik)
5. **Tab "Prediction"**:
   - Upload foto test
   - Sistem akan mengenali wajah Alice

### **📋 Checklist Menambah User Baru**

- ✅ Buat user baru dengan name, email, password
- ✅ Folder `dataset/<user_id>/` otomatis dibuat
- ✅ Upload minimal **5-10 foto** wajah yang jelas
- ✅ Foto dari **berbagai sudut** (depan, samping, berbagai ekspresi)
- ✅ Kualitas foto baik (pencahayaan cukup, fokus jelas)
- ✅ Rebuild database setelah upload foto
- ✅ Test prediction untuk verifikasi

### **⚠️ Tips Penting**

- **Minimal 5 foto** per user untuk akurasi baik
- **Lebih banyak foto = lebih akurat** (10-20 foto ideal)
- **Variasi penting**: foto dengan kacamata/tanpa, tersenyum/serius, sudut berbeda
- **Pencahayaan**: Hindari foto terlalu gelap atau overexposed
- **Rebuild wajib**: Setiap kali ada perubahan foto, rebuild database
- **Format**: JPG atau PNG, sistem auto-resize ke 224×224

---

### **🔄 Workflow Lengkap**

```
1. CREATE USER
   ↓
2. UPLOAD PHOTOS (5-10 foto minimum)
   ↓
3. BUILD DATABASE (10-30 detik)
   ↓
4. READY FOR PREDICTION/LOGIN
```

---
