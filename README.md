# FLASK & BELAJAR HTTP

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