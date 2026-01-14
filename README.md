## FLASK


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

# 📘 **API SPEC — HALO ENDPOINT**

## 📌 **Base URL**
```
/api/halo
```

---

# 🟦 **1. GET /api/halo**

### **Deskripsi**
Mengembalikan pesan sederhana untuk memastikan API berjalan.

### **Method**
```
GET
```

### **Request**
Tidak membutuhkan parameter.

### **Response 200**
```json
{
  "status": "success",
  "message": "Halo from flask",
  "data": "Empty Result"
}
```

### **Catatan**
- Endpoint ini cocok untuk health check.
- Dicatat di log melalui `logger.info()`.

---

# 🟩 **2. POST /api/halo**

### **Deskripsi**
Menerima data form (bukan JSON) dan mengembalikan payload yang dikirim.

### **Method**
```
POST
```

### **Content-Type**
```
multipart/form-data
```
atau  
```
application/x-www-form-urlencoded
```

### **Request Parameters (form-data)**

| Field       | Type   | Required | Description |
|-------------|--------|----------|-------------|
| nama        | string | yes      | Nama pengirim |
| handphone   | string | yes      | Nomor HP pengirim |

### **Contoh Request (form-data)**

```
nama = Edy
handphone = 08111111
```

### **Response 200**
```json
{
  "status": "success",
  "message": "Edy",
  "data": {
    "nama": "Edy",
    "handphone": "08111111"
  }
}
```

### **Catatan**
- Data dibaca menggunakan `api.parser()` → `parse_args()`.
- Payload dikirim ke service layer `post_halo()`.
- Logger menyimpan payload ke file log.

---

# 🧩 **Rangkuman Singkat**

| Endpoint        | Method | Input Type          | Output |
|-----------------|--------|---------------------|--------|
| `/api/halo`     | GET    | none                | JSON status |
| `/api/halo`     | POST   | form-data / urlencoded | JSON payload |

---
