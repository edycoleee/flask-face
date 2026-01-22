# 🔒 HTTPS Setup for Local Network (LAN Only)

## 📋 Untuk Jaringan Lokal (192.168.171.184)

Karena jaringan lokal, Anda **tidak bisa** menggunakan Let's Encrypt (butuh domain publik). Ada 3 opsi:

---

## ✅ Option 1: Self-Signed Certificate (Recommended - Paling Mudah)

### **Kelebihan:**
- ✅ Gratis & instant
- ✅ Tidak butuh domain
- ✅ Works untuk LAN
- ✅ Perfect untuk development/internal use

### **Kekurangan:**
- ❌ Browser warning "Not Secure" (harus manual trust)
- ❌ Tidak valid untuk publik internet

---

### **Step-by-Step Setup:**

#### **1. Generate Self-Signed Certificate**

```bash
# Masuk ke project folder
cd /home/sultan/flask-face

# Buat folder certs
mkdir -p certs

# Generate certificate (valid 1 tahun)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/OU=IT/CN=192.168.171.184"

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# Verify certificate
openssl x509 -in certs/cert.pem -text -noout
```

**Output:**
```
certs/
├── cert.pem    # Public certificate
└── key.pem     # Private key
```

---

#### **2. Test HTTPS dengan Python (Tanpa Docker)**

```bash
# run.py akan otomatis detect certs/ dan enable HTTPS
python run.py
```

**Output:**
```
============================================================
🔒 HTTPS MODE ENABLED
============================================================
Certificate: certs/cert.pem
Key: certs/key.pem
Server running on https://0.0.0.0:443
============================================================
```

**Akses:**
```bash
# Dari server sendiri
curl -k https://192.168.171.184

# Dari browser (akan ada warning, klik "Advanced" → "Proceed")
https://192.168.171.184
```

---

#### **3. Setup HTTPS dengan Docker**

**Edit `docker-compose.app.yml`:**

Uncomment baris HTTPS:

```yaml
services:
  flask-app:
    # ... konfigurasi lain ...
    ports:
      - "192.168.171.184:5000:5000"
      - "192.168.171.184:443:443"   # ✅ Uncomment ini
    volumes:
      # ... volume lain ...
      - ./certs:/app/certs:ro        # ✅ Uncomment ini
```

**Rebuild app:**
```bash
docker-compose -f docker-compose.app.yml up -d --build
```

**Test HTTPS:**
```bash
# From server
curl -k https://192.168.171.184

# From browser
https://192.168.171.184
```

---

#### **4. Trust Certificate di Client Devices**

Supaya browser tidak warning "Not Secure", trust certificate:

**Windows:**
1. Copy `certs/cert.pem` ke PC Windows
2. Double-click → Install Certificate
3. Store Location: **Local Machine**
4. Place in: **Trusted Root Certification Authorities**
5. Restart browser

**Mac:**
1. Copy `certs/cert.pem` ke Mac
2. Double-click → Keychain Access
3. Select certificate → Get Info
4. Trust → **Always Trust**
5. Restart browser

**Linux:**
```bash
# Copy cert ke trusted store
sudo cp certs/cert.pem /usr/local/share/ca-certificates/flask-face.crt
sudo update-ca-certificates
sudo systemctl restart nginx  # jika pakai nginx
```

**Android:**
1. Copy `cert.pem` ke phone
2. Settings → Security → Install Certificate
3. Select file → Install

**iOS:**
1. Email `cert.pem` to yourself
2. Open attachment → Install Profile
3. Settings → General → About → Certificate Trust Settings
4. Enable certificate

---

## ✅ Option 2: Local CA (Certificate Authority) - Advanced

### **Kelebihan:**
- ✅ Lebih professional
- ✅ Bisa generate banyak certificate
- ✅ Centralized trust (trust CA sekali, semua cert valid)
- ✅ Good untuk banyak services

### **Kekurangan:**
- ❌ Setup lebih kompleks
- ❌ Butuh maintain CA private key

---

### **Setup Local CA:**

#### **1. Create Certificate Authority**

```bash
cd /home/sultan/flask-face
mkdir -p certs/ca

# Generate CA private key
openssl genrsa -out certs/ca/ca-key.pem 4096

# Generate CA certificate (valid 10 tahun)
openssl req -new -x509 -days 3650 \
  -key certs/ca/ca-key.pem \
  -out certs/ca/ca-cert.pem \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace CA/CN=FlaskFace Root CA"

# Protect CA key
chmod 600 certs/ca/ca-key.pem
chmod 644 certs/ca/ca-cert.pem
```

---

#### **2. Generate Server Certificate signed by CA**

```bash
# Generate server private key
openssl genrsa -out certs/key.pem 4096

# Create CSR (Certificate Signing Request)
openssl req -new -key certs/key.pem -out certs/server.csr \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/CN=192.168.171.184"

# Create config file untuk SAN (Subject Alternative Name)
cat > certs/server.ext <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
IP.1 = 192.168.171.184
DNS.1 = raspberrypi.local
DNS.2 = flask-face.local
EOF

# Sign certificate dengan CA (valid 1 tahun)
openssl x509 -req -in certs/server.csr \
  -CA certs/ca/ca-cert.pem \
  -CAkey certs/ca/ca-key.pem \
  -CAcreateserial \
  -out certs/cert.pem \
  -days 365 \
  -extfile certs/server.ext

# Cleanup
rm certs/server.csr certs/server.ext

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
```

---

#### **3. Trust CA on Client Devices**

**PENTING:** Trust `certs/ca/ca-cert.pem` (bukan cert.pem)

Setelah trust CA, semua certificate yang di-sign oleh CA otomatis trusted!

**Windows:**
```bash
# Copy ca-cert.pem ke PC Windows
# Install ke "Trusted Root Certification Authorities"
```

**Linux:**
```bash
sudo cp certs/ca/ca-cert.pem /usr/local/share/ca-certificates/flask-face-ca.crt
sudo update-ca-certificates
```

**Mac:**
```bash
# Import CA ke Keychain → Always Trust
```

---

#### **4. Test HTTPS**

```bash
# Start app
python run.py

# Test dari client (no -k needed jika CA sudah trusted!)
curl https://192.168.171.184

# Browser tidak akan warning lagi ✅
```

---

## ✅ Option 3: mDNS with .local Domain

### **Setup Hostname .local**

```bash
# Edit hostname
sudo hostnamectl set-hostname flask-face

# Install Avahi (mDNS)
sudo apt-get update
sudo apt-get install avahi-daemon

# Start service
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon

# Test
ping flask-face.local
```

**Generate certificate untuk .local domain:**

```bash
# Self-signed dengan DNS name
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/CN=flask-face.local" \
  -addext "subjectAltName=DNS:flask-face.local,IP:192.168.171.184"
```

**Access via:**
```
https://flask-face.local
```

---

## 🎯 Recommendation untuk Raspberry Pi 5 di LAN

### **Best Practice:**

```bash
# 1. Generate self-signed cert (5 menit setup)
cd /home/sultan/flask-face
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/CN=192.168.171.184" \
  -addext "subjectAltName=IP:192.168.171.184,DNS:raspberrypi.local"

chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# 2. Edit docker-compose.app.yml (uncomment HTTPS lines)
nano docker-compose.app.yml

# 3. Rebuild app
docker-compose -f docker-compose.app.yml up -d --build

# 4. Test
curl -k https://192.168.171.184:443

# 5. Trust certificate di client devices (optional, untuk remove warning)
# Copy certs/cert.pem ke PC/Mac/Phone dan install
```

---

## 🔧 Troubleshooting

### **Problem: Port 443 already in use**
```bash
# Find process
sudo lsof -i :443

# Stop service
sudo systemctl stop apache2  # atau nginx

# Or use different port
# Edit docker-compose.app.yml: "8443:443"
# Access: https://192.168.171.184:8443
```

### **Problem: Permission denied on port 443**
```bash
# Linux butuh sudo untuk port < 1024
# Option 1: Use port 8443 instead
# Option 2: Use Docker (sudah bisa bind port 443)
```

### **Problem: Browser warning tidak hilang**
```bash
# Install certificate di device
# Pastikan trust "Trusted Root CA"
# Restart browser completely
# Clear browser cache
```

---

## 📊 Comparison

| Method | Setup Time | Security | Browser Warning | Best For |
|--------|-----------|----------|-----------------|----------|
| **Self-Signed** | 5 min | Medium | Yes (can bypass) | Internal LAN |
| **Local CA** | 30 min | High | No (after trust) | Multiple services |
| **mDNS .local** | 15 min | Medium | Yes | Development |

---

## ✅ Quick Command Summary

### **Generate Self-Signed (Fastest):**
```bash
cd /home/sultan/flask-face
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem -out certs/cert.pem -days 365 \
  -subj "/CN=192.168.171.184" \
  -addext "subjectAltName=IP:192.168.171.184"
chmod 600 certs/key.pem && chmod 644 certs/cert.pem
```

### **Enable HTTPS in Docker:**
```bash
# Edit docker-compose.app.yml (uncomment HTTPS lines)
nano docker-compose.app.yml

# Rebuild
docker-compose -f docker-compose.app.yml up -d --build

# Test
curl -k https://192.168.171.184
```

### **Access from Browser:**
```
https://192.168.171.184
# Click "Advanced" → "Proceed to 192.168.171.184 (unsafe)"
```

---

## 🎓 Production Best Practice

Untuk **internal company network**:
1. ✅ Setup **Local CA** (one-time trust)
2. ✅ Distribute CA certificate ke semua devices
3. ✅ Generate certificates untuk semua services
4. ✅ Setup automatic renewal (1 year validity)
5. ✅ Use **mDNS** untuk friendly DNS names

Untuk **home lab / personal use**:
1. ✅ Use **self-signed** (paling simple)
2. ✅ Trust certificate di devices yang sering dipakai
3. ✅ Atau terima browser warning (bypass setiap kali)

---

**Recommendation:** Start dengan **self-signed** (5 menit setup), bisa upgrade ke Local CA nanti jika butuh! 🚀
