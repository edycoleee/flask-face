# Photo API - Quick Reference

## Endpoint Summary

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/photos/<user_id>/upload` | POST | Upload 1 foto JPG/PNG, auto-resize (224×224) |
| `/api/photos/<user_id>/upload/multiple` | POST | Upload banyak foto, auto-resize (224×224) |
| `/api/photos/<user_id>` | GET | Ambil semua foto user |
| `/api/photos/<user_id>/<photo_id>` | DELETE | Hapus foto |

## Request Examples

### 1️⃣ Upload Single Photo
```bash
curl -X POST http://localhost:5000/api/photos/1/upload \
  -F "file=@path/to/photo.jpg"
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "filename": "20260118_120530_photo.jpg",
  "filepath": "dataset/1/20260118_120530_photo.jpg",
  "width": 224,
  "height": 224,
  "created_at": "2026-01-18T12:05:30.123456"
}
```

---

### 2️⃣ Upload Multiple Photos
```bash
curl -X POST http://localhost:5000/api/photos/1/upload/multiple \
  -F "files[]=@photo1.jpg" \
  -F "files[]=@photo2.jpg" \
  -F "files[]=@photo3.png"
```

**Response (201):**
```json
{
  "files": [
    {
      "id": 1,
      "user_id": 1,
      "filename": "20260118_120530_photo1.jpg",
      "filepath": "dataset/1/20260118_120530_photo1.jpg",
      "width": 224,
      "height": 224,
      "created_at": "2026-01-18T12:05:30.123456"
    },
    {
      "id": 2,
      "user_id": 1,
      "filename": "20260118_120531_photo2.jpg",
      "filepath": "dataset/1/20260118_120531_photo2.jpg",
      "width": 224,
      "height": 224,
      "created_at": "2026-01-18T12:05:31.654321"
    },
    {
      "id": 3,
      "user_id": 1,
      "filename": "20260118_120532_photo3.png",
      "filepath": "dataset/1/20260118_120532_photo3.png",
      "width": 224,
      "height": 224,
      "created_at": "2026-01-18T12:05:32.987654"
    }
  ],
  "total": 3,
  "errors": null
}
```

---

### 3️⃣ Get User Photos
```bash
curl http://localhost:5000/api/photos/1
```

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "20260118_120530_photo.jpg",
    "filepath": "dataset/1/20260118_120530_photo.jpg",
    "width": 224,
    "height": 224,
    "created_at": "2026-01-18T12:05:30.123456"
  }
]
```

---

### 4️⃣ Delete Photo
```bash
curl -X DELETE http://localhost:5000/api/photos/1/1
```

**Response (200):**
```json
{
  "message": "Foto 1 berhasil dihapus"
}
```

---

## Database Schema

### photos table
```sql
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    width INTEGER DEFAULT 224,
    height INTEGER DEFAULT 224,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## File Structure
```
app/
├── api/
│   └── photos.py              # API endpoints
├── models/
│   └── photo_model.py         # Photo dataclass
├── services/
│   └── photo_service.py       # Business logic
└── utils/
    └── db.py                  # Database + photos table
```

---

## Features ✓

- ✅ Auto-resize ke 224×224 pixel
- ✅ Support JPG dan PNG
- ✅ Validasi format file
- ✅ Max file size 10MB
- ✅ Metadata storage di database
- ✅ Folder terorganisir per user
- ✅ Error handling lengkap
- ✅ Request logging
- ✅ Cascade delete

---

## Error Responses

**400 Bad Request:**
```json
{
  "message": "Format file hanya boleh JPG/PNG"
}
```

**404 Not Found:**
```json
{
  "message": "User tidak ditemukan"
}
```

**500 Internal Server Error:**
```json
{
  "message": "Error message here"
}
```
