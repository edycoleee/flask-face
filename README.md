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
