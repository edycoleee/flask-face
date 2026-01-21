# Photo API Implementation - Summary

## ✓ Implementasi Selesai

Photo API namespace telah berhasil ditambahkan dengan semua endpoint sesuai spesifikasi.

### File yang Dibuat/Dimodifikasi:

1. **[app/models/photo_model.py](app/models/photo_model.py)** ✓
   - Model dataclass untuk Photo
   - Field: id, user_id, filename, filepath, width, height, created_at

2. **[app/services/photo_service.py](app/services/photo_service.py)** ✓
   - `upload_photo()` - Upload dan resize single photo
   - `upload_multiple_photos()` - Upload multiple photos sekaligus
   - `resize_image()` - Auto-resize gambar ke 224×224
   - `allowed_file()` - Validasi format (JPG/PNG)
   - `get_user_photos()` - Ambil semua foto user
   - `delete_photo()` - Hapus foto

3. **[app/api/photos.py](app/api/photos.py)** ✓
   - Endpoint: `POST /api/photos/<user_id>/upload` - Upload single photo
   - Endpoint: `POST /api/photos/<user_id>/upload/multiple` - Upload multiple photos
   - Endpoint: `GET /api/photos/<user_id>` - Get all user photos
   - Endpoint: `DELETE /api/photos/<user_id>/<photo_id>` - Delete photo

4. **[app/utils/db.py](app/utils/db.py)** ✓
   - Tambahan: `photos` table dengan schema:
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
     )
     ```

5. **[run.py](run.py)** ✓
   - Registrasi photos namespace ke API

6. **[requirements.txt](requirements.txt)** ✓
   - Tambahan: `Pillow` untuk image processing

---

## API Endpoints

### 1. Upload Single Photo
```
POST /api/photos/<user_id>/upload
Content-Type: multipart/form-data

Form Data:
  - file: <image file JPG/PNG>

Response (201):
{
  "id": 1,
  "user_id": 1,
  "filename": "20260118_120530_photo.jpg",
  "filepath": "dataset/1/20260118_120530_photo.jpg",
  "width": 224,
  "height": 224,
  "created_at": "2026-01-18T12:05:30.123456"
}

Error (400):
{
  "message": "Format file hanya boleh JPG/PNG"
}
```

### 2. Upload Multiple Photos
```
POST /api/photos/<user_id>/upload/multiple
Content-Type: multipart/form-data

Form Data:
  - files[]: <image 1>
  - files[]: <image 2>
  - ...

Response (201):
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
    ...
  ],
  "total": 2,
  "errors": null
}
```

### 3. Get User Photos
```
GET /api/photos/<user_id>

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "20260118_120530_photo.jpg",
    "filepath": "dataset/1/20260118_120530_photo.jpg",
    "width": 224,
    "height": 224,
    "created_at": "2026-01-18T12:05:30.123456"
  },
  ...
]
```

### 4. Delete Photo
```
DELETE /api/photos/<user_id>/<photo_id>

Response (200):
{
  "message": "Foto 1 berhasil dihapus"
}
```

---

## Fitur Utama

✓ **Auto-Resize**: Gambar otomatis di-resize ke 224×224 pixel
✓ **Format Support**: JPG dan PNG dengan validasi
✓ **File Size Limit**: Maksimal 10MB per file
✓ **Metadata Storage**: Semua info foto tersimpan di database
✓ **Folder Organization**: Foto terorganisir per user di `dataset/<user_id>/`
✓ **Error Handling**: Validasi lengkap dengan pesan error yang jelas
✓ **Logging**: Semua aktivitas tercatat di log
✓ **Cascade Delete**: Hapus user otomatis hapus semua fotonya

---

## Testing

Untuk test API, gunakan curl atau Postman:

```bash
# 1. Create user dulu
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Sultan", "email": "sultan@example.com"}'

# 2. Upload single photo
curl -X POST http://localhost:5000/api/photos/1/upload \
  -F "file=@photo.jpg"

# 3. Upload multiple photos
curl -X POST http://localhost:5000/api/photos/1/upload/multiple \
  -F "files[]=@photo1.jpg" \
  -F "files[]=@photo2.jpg"

# 4. Get all user photos
curl http://localhost:5000/api/photos/1

# 5. Delete photo
curl -X DELETE http://localhost:5000/api/photos/1/1
```

API documentation juga tersedia di: `http://localhost:5000/api/docs`
