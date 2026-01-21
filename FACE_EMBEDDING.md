
---

# 🧠 1️⃣ Cara berpikir CNN vs Face Embedding

## CNN classifier (yang biasa dipakai)

Arsitektur:

```
Image → CNN → Softmax(orang1, orang2, orang3, …)
```

Model menyimpan:

* Bobot CNN
* Bobot softmax untuk tiap orang

Makna:

> Model **menghafal siapa saja** yang ada di training.

Kalau punya:

```
15 orang → output = 15 neuron
```

---

## Face Embedding

Arsitektur:

```
Image → CNN → vektor 128 dimensi
```

Tidak ada softmax.

Model tidak tahu siapa pun.

Ia hanya tahu:

> “Ini koordinat wajah di ruang wajah manusia”

Contoh:

```
Pak Budi = (0.21, -1.7, 3.4, …)
Pak Andi = (0.22, -1.8, 3.5, …)
```

Orang yang sama → vektornya dekat
Orang berbeda → vektornya jauh

---

# 🧠 2️⃣ Analogi database

Bayangkan kamu menyimpan:

### CNN Softmax

```
model.h5 =
   bobot utk kelas Andi
   bobot utk kelas Budi
   bobot utk kelas Rina
```

Kalau Rina keluar:

> CNN tetap menyimpan neuron Rina
> Tidak bisa dihapus.

Kalau Siti masuk:

> Harus retrain ulang.

---

### Face Embedding

Kamu menyimpan:

```
face_db.npy =
[
   ("andi", [0.13, -1.2, 0.88, ...]),
   ("andi", [0.14, -1.1, 0.90, ...]),
   ("budi", [...]),
   ("rina", [...])
]
```

Kalau Siti datang:

```
append("siti", embedding)
```

Kalau Rina keluar:

```
delete semua embedding rina
```

Tidak ada retraining.
Seperti database SQL.

---

# 🔥 3️⃣ Ini sebab CNN gagal di Yale

Yale:

* 15 orang
* 11 foto per orang

CNN Softmax butuh:

> minimal 100–1000 foto per kelas

Face Embedding butuh:

> 3–8 foto

---

# 🧬 4️⃣ Apakah model perlu retrain jika user baru?

| Sistem         | Tambah user |
| -------------- | ----------- |
| CNN Softmax    | ❌ retrain   |
| Face Embedding | ✅ tidak     |

Face Embedding = **zero retraining system**

Ini kenapa:

* Windows Hello
* Apple FaceID
* Absensi kantor

tidak pernah retrain CNN saat user baru.

---

# 🧠 5️⃣ Kenapa embedding bisa generalisasi?

Karena CNN embedding dilatih di:

> jutaan wajah dari ribuan etnis, usia, lighting, pose

Ia belajar:

* struktur mata
* jarak hidung
* kontur rahang

Bukan menghafal orang.

---

# 6️⃣ Kalau pakai CNN, mengajarkan:

“Ini Andi, ini Budi”

Kalau pakai embedding:
“Ini koordinat wajah manusia”

Kamu hanya menyimpan koordinat user.

---

# 🧨 7️⃣ Keamanan

CNN Softmax:

* Tidak bisa threshold
* Impostor bisa lolos

Embedding:

* Punya jarak matematis
* Bisa deteksi “tidak dikenal”

Itu syarat sistem login & RS.

---

# 🎯 Kesimpulan

Kalau membangun:

* Login wajah
* Absensi
* RSUD Sultan Fatah
* Akses PC

> CNN classifier itu **salah paradigma**

Face Embedding itu:

> “database wajah”, bukan “model wajah”

---
