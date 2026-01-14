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

# Terdapat 2 bentuk input >> from-data dan json, bisa di pilih menyesuaikan api yang akan digunakan 

Bayangkan HTTP itu seperti **layanan kurir paket**. Saat kamu mengirim paket (data) lewat internet, kamu perlu memberi tahu si penerima apa isi di dalam paket tersebut supaya mereka tahu cara membukanya.

**Content-Type** adalah "label" yang ditempel di luar kotak paket tersebut. Tanpa label ini, komputer penerima bakal bingung apakah isinya surat, foto, atau tumpukan berkas.

Berikut adalah penjelasan tiga jenis "label" yang paling sering dipakai:

---

### 1. Application/JSON

**Filosofinya: Kirim Catatan Rapi**

JSON (*JavaScript Object Notation*) itu seperti mengirim **surat dengan format daftar yang sangat rapi**. Isinya hanya teks, tapi diatur dengan aturan tertentu (pakai kurung kurawal `{ }` dan tanda kutip).

* **Kapan dipakai?** Saat aplikasi HP kamu (Instagram/TikTok) minta data ke server, atau saat kamu *login*.
* **Bentuknya:**
```json
{
  "nama": "Budi",
  "kelas": "12-IPA",
  "pesan": "Halo dunia!"
}

```


* **Analogi:** Seperti mengirim formulir pendaftaran yang diketik rapi di selembar kertas tipis. Ringan dan cepat dibaca oleh mesin.

---

### 2. Application/X-WWW-Form-Urlencoded

**Filosofinya: Kirim Pesan Singkat Lewat Link**

Ini adalah cara jadul tapi masih sangat sering dipakai. Data dikirim dalam satu baris panjang yang disambung-sambung dengan tanda `&` dan `=`.

* **Kapan dipakai?** Biasanya digunakan oleh formulir HTML sederhana, seperti kolom pencarian di Google atau form "Hubungi Kami" yang isinya cuma teks pendek.
* **Bentuknya:** `nama=Budi&kelas=12-IPA&pesan=Halo+dunia`
* **Analogi:** Seperti menulis pesan singkat di balik kartu pos. Ruangnya terbatas dan tidak bisa dipakai kirim barang aneh-aneh.

---

### 3. Multipart/Form-Data

**Filosofinya: Kirim Paket Komplit (Teks + File)**

Nah, kalau yang ini adalah "raja"-nya pengiriman. Sesuai namanya (*multipart*), paket ini bisa dibagi-bagi menjadi beberapa bagian dalam satu pengiriman. Ada bagian untuk teks, ada bagian khusus untuk file gambar, video, atau dokumen.

* **Kapan dipakai?** Saat kamu posting foto di Instagram lengkap dengan *caption*-nya, atau saat *upload* tugas PDF di Google Classroom.
* **Kenapa harus ini?** Karena file (seperti `.jpg` atau `.pdf`) itu datanya "berat" dan bukan teks biasa. `multipart` memungkinkan server membedakan mana yang tulisan dan mana yang data gambar.
* **Analogi:** Seperti mengirim kardus besar yang di dalamnya ada sekat-sekatnya. Satu sekat berisi surat (teks), sekat lainnya berisi flashdisk (file).

---

### Ringkasan Perbandingan

| Jenis Content-Type | Cocok Untuk Apa? | Ibaratnya... |
| --- | --- | --- |
| **JSON** | Komunikasi antar aplikasi modern (API). | Surat daftar belanja yang rapi. |
| **Form-Data** | Form teks sederhana (pencarian/login). | Tulisan di kartu pos. |
| **Multipart** | Upload file + Teks (Post foto/dokumen). | Kardus paket berisi berbagai barang. |

---

