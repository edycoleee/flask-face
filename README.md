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
# LAYANAN HTTP

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
# Pengetahuan HTTP 


### 1. HTTPS (Versi Aman)

Kamu pasti sering melihat ikon **gembok** di bar alamat browser. Itu artinya kamu menggunakan **HTTPS** (*S untuk Secure*).

* **HTTP biasa:** Seperti mengirim kartu pos. Pak Pos (dan siapa pun di tengah jalan) bisa membaca isi suratmu, termasuk password dan data bank.
* **HTTPS:** Seperti mengirim surat di dalam **kotak besi gembok**. Hanya kamu dan server yang punya kuncinya. Meskipun paketnya dicuri di tengah jalan, si pencuri tidak bisa membacanya karena isinya teracak (enkripsi).
* **Kenapa penting?** Tanpa HTTPS, "Gelang Konser" (Token Auth) kamu bisa dicuri orang lain (serangan ini disebut *Man-in-the-Middle Attack*).

---

### 2. Statelessness (Sifat "Lupa Ingatan")

HTTP itu bersifat **Stateless**. Artinya, server itu punya penyakit "lupa ingatan". Setiap kali kamu mengirim request, server menganggap kamu adalah orang asing yang baru pertama kali datang.

* **Masalahnya:** Bayangkan kalau kamu belanja online. Kamu masukkan barang ke keranjang (Request 1). Pas mau bayar (Request 2), server lupa kalau tadi kamu sudah masukkan barang.
* **Solusinya:** Itulah fungsi **Cookie** dan **Token**. Di setiap request, browser kamu harus "mengingatkan" server siapa kamu dengan mengirimkan token tersebut di Header.

---

### 3. Caching (Menyimpan Memori)

Pernah merasa buka website yang sama kedua kalinya jauh lebih cepat? Itu berkat **Caching**.

Server bisa mengirim header khusus yang bilang: *"Hey Browser, gambar logo ini jangan minta-minta lagi ya selama 1 tahun ke depan, simpan saja di memorimu!"*

* **Keuntungannya:** Menghemat kuota internetmu dan mengurangi beban kerja server.

---

### 4. Query Parameters vs Path Parameters

Saat melakukan **GET**, ada dua cara mengirim info tambahan di URL:

1. **Path Parameter:** Digunakan untuk menunjuk benda spesifik.
* Contoh: `facebook.com/users/budi` (Langsung ke profil Budi).


2. **Query Parameter:** Digunakan untuk menyaring atau mencari (biasanya pakai tanda tanya `?`).
* Contoh: `shopee.co.id/search?warna=biru&ukuran=XL` (Mencari barang dengan kriteria tertentu).
---

### Kesimpulan Besar: Mind Map HTTP

Jika kita rangkum semua pelajaran kita, urutannya seperti ini:

1. **Client** (Browser/HP) ingin sesuatu.
2. Siapkan **URL** (Alamat) dan **Method** (Mau ngapain?).
3. Tempelkan **Header** (Identitas/Auth/Content-Type).
4. Isi **Body** (Data JSON/File jika perlu).
5. Kirim lewat jalur **HTTPS** yang aman.
6. **Server** memproses dan mengirim **Status Code** (200, 404, dll).
7. **Client** menampilkan hasilnya ke kamu.

---

Setelah tahu cara "membungkus" paketnya (Content-Type), sekarang kamu harus tahu **"label instruksi"** untuk si kurir. Dalam dunia HTTP, instruksi ini disebut **HTTP Methods** atau sering juga disebut **HTTP Verbs**.

Bayangkan kamu sedang mengelola database siswa di sekolah. Berikut adalah cara kerja masing-masing *method*:

---

### 1. GET (Ambil Data)

**Filosofinya: "Tolong lihatkan dong..."**

GET digunakan hanya untuk **meminta atau mengambil data** dari server. Method ini tidak boleh mengubah apa pun di server, sifatnya hanya membaca.

* **Analogi:** Seperti kamu pergi ke mading sekolah untuk membaca pengumuman. Kamu tidak mengubah isi mading, kamu cuma melihatnya.
* **Ciri khas:** Data yang dicari biasanya muncul di alamat URL (misal: `google.com/search?q=kucing`).

### 2. POST (Tambah Data Baru)

**Filosofinya: "Ini ada setoran data baru!"**

POST digunakan untuk **mengirim data baru** ke server untuk diproses atau disimpan. Biasanya ini akan membuat entitas baru di database.

* **Analogi:** Seperti mengisi formulir pendaftaran siswa baru dan menyerahkannya ke TU. Nama kamu yang tadinya tidak ada di buku induk, sekarang jadi ada.
* **Ciri khas:** Sering digunakan bareng `multipart/form-data` atau `JSON`.

### 3. PUT (Ganti Total)

**Filosofinya: "Ganti semua data lama dengan yang baru."**

PUT digunakan untuk **memperbarui data secara keseluruhan**. Kamu harus mengirimkan seluruh data objeknya. Jika ada bagian yang tidak kamu kirim, bagian itu bisa dianggap hilang atau kosong.

* **Analogi:** Seperti mengganti seluruh set seragam sekolah. Kamu tidak cuma ganti baju, tapi dari topi sampai kaos kaki diganti semua dengan yang baru.

### 4. PATCH (Update Sebagian)

**Filosofinya: "Ada sedikit revisi nih."**

PATCH mirip dengan PUT, tapi lebih efisien. Digunakan untuk **mengubah sebagian kecil** saja dari data yang sudah ada tanpa harus mengirim ulang semua datanya.

* **Analogi:** Seperti menambal ban sepeda yang bocor atau mengganti tali sepatu yang putus. Kamu tidak beli sepeda baru, cuma memperbaiki bagian yang rusak saja.

### 5. DELETE (Hapus Data)

**Filosofinya: "Buang data ini!"**

Sudah sangat jelas dari namanya, method ini digunakan untuk **menghapus data** di server.

* **Analogi:** Seperti menghapus namamu dari daftar giliran piket kelas karena kamu sudah pindah sekolah.

---

### Tabel Perbedaan Singkat

| Method | Aksi CRUD* | Analogi di Sekolah |
| --- | --- | --- |
| **GET** | Read (Baca) | Baca buku di perpustakaan. |
| **POST** | Create (Buat) | Daftar jadi anggota baru perpus. |
| **PUT** | Update (Ganti Semua) | Ganti kartu perpus yang rusak dengan kartu baru (semua data ditulis ulang). |
| **PATCH** | Update (Edit Dikit) | Ganti foto di kartu perpus saja. |
| **DELETE** | Delete (Hapus) | Mengundurkan diri dari anggota perpus. |

> ***CRUD** adalah singkatan dari *Create, Read, Update, Delete*—operasi dasar dalam mengelola data.

---

### Hubungannya dengan Content-Type

* **GET** biasanya tidak pakai `Content-Type` karena dia tidak kirim "paket" (body), cuma kirim instruksi lewat URL.
* **POST, PUT, PATCH** wajib pakai `Content-Type` karena mereka membawa "isi paket" (JSON atau Form-data) yang mau diproses server.



# Cara kerja HTTP

### 1. Fondasi Pengiriman (Content-Type)

* **JSON**: Format teks rapi (pakai `{ }`) untuk komunikasi antar aplikasi/mesin. Ringan dan paling standar saat ini.
* **Form-Data**: Format teks sederhana (seperti baris alamat) untuk formulir dasar.
* **Multipart/Form-Data**: Format khusus untuk mengirim **file** (gambar/dokumen) bersamaan dengan teks.

### 2. Instruksi Aksi (HTTP Methods)

* **GET**: Meminta/melihat data (tidak mengubah apa pun).
* **POST**: Menambah/setor data baru.
* **PUT**: Mengganti seluruh data lama dengan yang baru.
* **PATCH**: Memperbaiki sebagian kecil data.
* **DELETE**: Menghapus data.

### 3. Informasi Tambahan (Headers & Auth)

* **Request Headers**: Label luar paket berisi info tambahan (Jenis perangkat, bahasa, dll).
* **Authentication (Auth)**: Cara membuktikan identitas.
* **Bearer Token**: Menggunakan "gelang akses" (Token) agar tidak perlu kirim password berulang kali.


* **Authorization**: Izin akses (Boleh atau tidaknya kamu melakukan sesuatu).

### 4. Laporan Hasil (Status Codes)

* **2xx (Success)**: Berhasil (Contoh: **200 OK**, **201 Created**).
* **3xx (Redirection)**: Alamat dipindah.
* **4xx (Client Error)**: Kesalahan pengguna (Contoh: **401** Belum Login, **404** Data Tidak Ada).
* **5xx (Server Error)**: Kesalahan pusat (Server sedang rusak/error).

### 5. Keamanan & Karakteristik

* **HTTPS**: Versi aman dengan enkripsi (isi paket digembok agar tidak bisa diintip).
* **Stateless**: Server tidak punya ingatan; setiap permintaan harus membawa identitas (Token/Cookie) kembali.

---
# CURL

Praktik langsung! `curl` adalah alat di terminal (Command Line) yang berfungsi sebagai "browser tanpa gambar". Dengan `curl`, kita bisa melihat apa yang sebenarnya terjadi di balik layar saat pengiriman data.

Kamu bisa mencoba perintah-perintah ini di **Terminal** (Mac/Linux) atau **Command Prompt/PowerShell** (Windows).

---

### 1. Simulasi GET (Mengambil Data & Melihat Header)

Kita akan mencoba mengambil data dari API publik (JSONPlaceholder) dan menambahkan flag `-v` (*verbose*) untuk mengintip headernya.

**Ketik ini di terminal:**

```bash
curl -v https://jsonplaceholder.typicode.com/posts/1

```

**Apa yang terjadi?**
Di bagian atas yang ada tanda `>`, itu adalah **Request Header** yang dikirim komputermu. Kamu akan melihat:

* `> GET /posts/1 HTTP/1.1` (Method)
* `> Host: jsonplaceholder.typicode.com` (Header Host)
* `> User-Agent: curl/8.4.0` (Identitas aplikasi)

---

### 2. Simulasi POST dengan JSON & Auth

Bayangkan kita mau mengirim artikel baru. Kita akan mengirim paket berisi **JSON** dan menyertakan **Token (Auth)** di headernya.

**Ketik ini di terminal:**

```bash
curl -X POST https://jsonplaceholder.typicode.com/posts \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer INI_TOKEN_RAHASIA_SAYA" \
     -d '{"title": "Belajar HTTP", "body": "Seru banget!", "userId": 1}'

```

**Penjelasan Perintah:**

* `-X POST`: Memberitahu kurir bahwa kita ingin **menambah data**.
* `-H "Content-Type: ..."`: Label bahwa isi paket kita adalah **JSON**.
* `-H "Authorization: ..."`: Menunjukkan **"Gelang Konser" (Token)** kita ke server.
* `-d`: (*Data*) Isi paket yang kita kirim.

---

### 3. Simulasi Multipart/Form-Data (Upload)

Misalnya kita ingin mensimulasikan upload file gambar beserta teks.

**Ketik ini di terminal:**

```bash
curl -X POST https://httpbin.org/post \
     -F "username=budi" \
     -F "foto=@foto_profil.jpg"

```

**Penjelasan Perintah:**

* `-F`: (*Form*) Secara otomatis membuat Header menjadi `multipart/form-data`.
* Simbol `@`: Memberitahu `curl` untuk mengambil file asli dari folder komputermu.

---

### Bagaimana Cara Membaca Hasilnya?

Saat kamu menjalankan perintah di atas, perhatikan simbol-simbol ini:

* **Tanda `>**`: Artinya data yang **KELUAR** dari laptopmu ke server (Request).
* **Tanda `<**`: Artinya data yang **MASUK/DITERIMA** dari server (Response).

---

### Isu Keamanan: Kenapa Auth Itu Penting?

Coba bayangkan kalau kamu tidak pakai Header `Authorization`. Siapa saja bisa mengirim `curl -X DELETE` ke postingan Instagram kamu.

**Contoh bahaya (Jangan ditiru tanpa izin):**
`curl -X DELETE https://api.sosmed.com/post/123`

Tanpa pemeriksaan "Gelang Konser" (Auth) di header, server akan langsung menghapus data tersebut. Itulah kenapa setiap kali kamu melakukan aksi (POST/PUT/PATCH/DELETE), server selalu mengecek header Authorization-mu terlebih dahulu.

---
# Status Code

Setelah kamu mengirim paket (Request) dengan metode, header, dan data yang benar, server akan mengirim balik **Status Code**. Ini adalah cara server memberikan "laporan singkat" tentang apa yang terjadi pada paketmu.

Kode ini selalu terdiri dari **3 angka**. Cara termudah menghafalnya adalah dengan melihat angka depannya:

---

### 1. Kelompok 2xx (Berhasil!)

Artinya: "Oke, paket diterima dan diproses tanpa masalah."

* **200 OK:** Paling umum. Artinya "Ini data yang kamu minta" (biasanya hasil dari GET).
* **201 Created:** Sering muncul setelah kamu **POST**. Artinya "Data baru berhasil dibuat/disimpan!"

### 2. Kelompok 3xx (Pindah Alamat)

Artinya: "Paket harus dikirim ke tempat lain (Redirect)."

* **301 Moved Permanently:** Alamat web yang kamu tuju sudah pindah selamanya ke alamat baru.
* **304 Not Modified:** Browser kamu masih punya salinan datanya, jadi server bilang "Pakai yang lama saja, isinya masih sama kok." (Ini yang bikin buka web jadi cepat).

### 3. Kelompok 4xx (Kesalahan Kamu/Client)

Artinya: "Ada yang salah dengan paketmu, silakan diperbaiki."

* **400 Bad Request:** Server tidak paham permintaanmu (mungkin format JSON-nya salah ketik).
* **401 Unauthorized:** Kamu lupa pakai "Gelang Konser" (**Auth**) atau tokenmu salah.
* **403 Forbidden:** Kamu punya ID Card, tapi kamu tidak punya izin masuk ke ruangan itu (misal: siswa mencoba masuk ke menu Admin).
* **404 Not Found:** Alamat atau data yang kamu cari tidak ada.
* **429 Too Many Requests:** Kamu terlalu sering mengirim perintah dalam waktu singkat (spam).

### 4. Kelompok 5xx (Kesalahan Server)

Artinya: "Bukan salahmu, tapi komputernya server lagi error/meledak."

* **500 Internal Server Error:** Servernya bingung atau ada *bug* di codingan back-endnya.
* **503 Service Unavailable:** Servernya lagi kepenuhan atau sedang dalam perbaikan (maintenance).

---

### Tabel Ringkasan "Bahasa Gaul" Status Code

| Kode | Nama Resmi | Artinya dalam Bahasa Kita |
| --- | --- | --- |
| **200** | OK | "Sip, ini datanya!" |
| **201** | Created | "Oke, data baru sudah disimpan!" |
| **401** | Unauthorized | "Siapa kamu? Login dulu sana!" |
| **403** | Forbidden | "Kamu dilarang masuk ke sini!" |
| **404** | Not Found | "Barangnya nggak ada, bro." |
| **500** | Server Error | "Aduh, servernya lagi pusing/error." |

---

### Contoh Nyata dalam Kehidupan Sosmed:

1. Kamu **Login** (POST)  Server kirim **200 OK** (Beserta Token).
2. Kamu **Buka Profil Teman** (GET)  Server kirim **200 OK** (Data profil muncul).
3. Kamu coba **Hapus Foto Teman** (DELETE)  Server kirim **403 Forbidden** (Karena itu bukan fotomu).
4. Kamu salah ketik **Alamat Web**  Server kirim **404 Not Found**.

Sekarang kamu sudah paham dari awal sampai akhir alur HTTP: cara bungkusnya (Content-Type), cara kirimnya (Method), surat pengantarnya (Header), keamanannya (Auth), sampai laporan hasilnya (Status Code).



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

