# 🚀 Cara Deploy Flask Face ke Production (Raspberry Pi)

## 📋 Overview

Guide lengkap deploy aplikasi Flask Face Recognition ke Raspberry Pi sebagai **production service** dengan:
- ✅ Gunicorn WSGI Server
- ✅ Nginx Reverse Proxy
- ✅ Systemd Auto-Start Service
- ✅ SSL/HTTPS (Let's Encrypt)
- ✅ Production-ready setup

---

## ⚠️ IMPORTANT

**JANGAN pakai `python run.py` untuk production!**

Flask development server:
- ❌ Single-threaded (1 request at a time)
- ❌ Tidak secure
- ❌ Crashes mudah
- ❌ Slow untuk concurrent users

**Solusi:** Gunakan **Gunicorn** (production WSGI server) + **Nginx** (reverse proxy)

---

## 🎯 Architecture

```
Internet/LAN Users
       ↓
   Nginx (Port 80/443)
       ↓
   Gunicorn (Port 5000 internal)
       ↓
   Flask Application
       ↓
   SQLite Database + TensorFlow Model
```

---

## 📝 Prerequisites

- Raspberry Pi 3/4/5 (minimum 2GB RAM recommended)
- Raspberry Pi OS (Debian/Ubuntu)
- Internet connection
- Basic Linux knowledge

---

## 1️⃣ Clone GitHub Repository

```bash
# Login ke Raspberry Pi via SSH
ssh pi@raspberry-pi-ip

# Update sistem dulu
sudo apt update && sudo apt upgrade -y

# Install git jika belum ada
sudo apt install git -y

# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/flask-face.git
cd flask-face

# Atau jika private repository
git clone https://<token>@github.com/YOUR_USERNAME/flask-face.git
```

**Alternatif - Transfer via SCP (jika tidak pakai Git):**
```bash
# Dari komputer lokal
scp -r /path/to/flask-face pi@raspberry-pi-ip:~/
```

---

## 2️⃣ Persiapan Raspberry Pi

### Install System Dependencies

```bash
# Python & pip
sudo apt install python3 python3-pip python3-venv -y

# Dependencies untuk TensorFlow
sudo apt install libatlas-base-dev libopenblas-dev -y

# Dependencies untuk Pillow (image processing)
sudo apt install libjpeg-dev zlib1g-dev libpng-dev -y

# SQLite (biasanya sudah terinstall)
sudo apt install sqlite3 -y

# (Optional) Install untuk monitoring
sudo apt install htop net-tools -y
```

### Cek Versi Python

```bash
python3 --version
# Harus Python 3.8+ (recommended 3.9+)

# Jika versi terlalu lama, upgrade dulu
```

### Buat Folder Structure

```bash
cd ~/flask-face

# Pastikan folder-folder ini ada
mkdir -p dataset
mkdir -p models
mkdir -p instance
mkdir -p logs
mkdir -p data
```

---

## 3️⃣ Setup Virtual Environment

```bash
# Masuk ke project directory
cd ~/flask-face

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies dari requirements.txt
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn

# Verify installations
pip list
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)"
```

**Catatan untuk Raspberry Pi:**
- TensorFlow install bisa lama (10-30 menit)
- Jika memory error, buat swap file (lihat section Troubleshooting)

---

## 4️⃣ Test Run Dulu

### Test dengan Development Server

```bash
# Pastikan masih di venv
source venv/bin/activate

# Test run
python run.py
```

Akses dari browser: `http://raspberry-pi-ip:5000`

**Cek:**
- ✅ Homepage loaded
- ✅ Create user berhasil
- ✅ Upload photo berhasil
- ✅ No errors di terminal

**Ctrl+C untuk stop**

---

### Test dengan Gunicorn

```bash
# Test Gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 run:app

# Atau dengan lebih verbose
gunicorn -w 2 -b 0.0.0.0:5000 --log-level debug run:app
```

Akses lagi dari browser: `http://raspberry-pi-ip:5000`

**Jika berhasil, lanjut ke systemd service!**

**Ctrl+C untuk stop**

---

## 5️⃣ Buat Systemd Service (Auto-Start)

### Create Service File

```bash
sudo nano /etc/systemd/system/flask-face.service
```

### Paste Configuration Ini:

```ini
[Unit]
Description=Flask Face Recognition Service
After=network.target

[Service]
Type=notify
User=pi
Group=pi
WorkingDirectory=/home/pi/flask-face
Environment="PATH=/home/pi/flask-face/venv/bin"

# Gunicorn command
ExecStart=/home/pi/flask-face/venv/bin/gunicorn \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --bind 0.0.0.0:5000 \
    --access-logfile /home/pi/flask-face/logs/access.log \
    --error-logfile /home/pi/flask-face/logs/error.log \
    --log-level info \
    run:app

# Restart policy
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Penjelasan Parameters:

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `--workers` | 2 | Jumlah worker processes (sesuaikan dengan CPU cores) |
| `--worker-class` | sync | Synchronous workers (untuk CPU-bound tasks) |
| `--timeout` | 120 | Timeout 120 detik (untuk training model) |
| `--bind` | 0.0.0.0:5000 | Listen di semua network interfaces port 5000 |
| `--log-level` | info | Level logging (debug/info/warning/error) |

**Workers Recommendation:**
- Raspberry Pi 3: `--workers 2`
- Raspberry Pi 4: `--workers 3-4`
- Raspberry Pi 5: `--workers 4-6`
- Formula: `(2 x CPU cores) + 1`

---

## 6️⃣ Buat Log Directory

```bash
# Buat folder logs jika belum ada
mkdir -p /home/pi/flask-face/logs

# Set permissions
chmod 755 /home/pi/flask-face/logs

# Verify
ls -la /home/pi/flask-face/logs
```

---

## 7️⃣ Enable & Start Service

### Reload Systemd

```bash
sudo systemctl daemon-reload
```

### Enable Auto-Start on Boot

```bash
sudo systemctl enable flask-face.service
```

### Start Service

```bash
sudo systemctl start flask-face.service
```

### Check Status

```bash
sudo systemctl status flask-face.service
```

**Expected Output:**
```
● flask-face.service - Flask Face Recognition Service
   Loaded: loaded (/etc/systemd/system/flask-face.service; enabled)
   Active: active (running) since Mon 2026-01-20 10:00:00 UTC; 5s ago
```

**Jika ada error, cek logs:**
```bash
sudo journalctl -u flask-face.service -n 50
```

---

### Test Service

```bash
# Akses dari browser
http://raspberry-pi-ip:5000

# Atau test via curl
curl http://localhost:5000
```

**Jika sukses, service sudah running!** ✅

---

## 8️⃣ Service Management Commands

### Basic Commands

```bash
# Start service
sudo systemctl start flask-face

# Stop service
sudo systemctl stop flask-face

# Restart service
sudo systemctl restart flask-face

# Reload configuration (tanpa restart)
sudo systemctl reload flask-face

# Check status
sudo systemctl status flask-face

# Enable auto-start on boot
sudo systemctl enable flask-face

# Disable auto-start
sudo systemctl disable flask-face
```

---

### View Logs

```bash
# Real-time logs (follow mode)
sudo journalctl -u flask-face -f

# Last 100 lines
sudo journalctl -u flask-face -n 100

# Logs from today
sudo journalctl -u flask-face --since today

# Logs from specific time
sudo journalctl -u flask-face --since "2026-01-20 10:00:00"

# Gunicorn access logs
tail -f /home/pi/flask-face/logs/access.log

# Gunicorn error logs
tail -f /home/pi/flask-face/logs/error.log
```

---

### Log Rotation (Prevent Large Log Files)

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/flask-face
```

**Paste:**
```
/home/pi/flask-face/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload flask-face > /dev/null 2>&1 || true
    endscript
}
```

---

## 9️⃣ Tambahkan Nginx (Recommended untuk Production)

### Kenapa Perlu Nginx?

✅ **Benefits:**
- Reverse proxy (hide internal port)
- SSL/HTTPS support
- Static file serving (faster)
- Load balancing
- Security (DDoS protection, rate limiting)
- Gzip compression
- Caching

---

### Install Nginx

```bash
sudo apt install nginx -y
```

### Verify Installation

```bash
# Check status
sudo systemctl status nginx

# Test
curl http://localhost
# Should see "Welcome to nginx!"
```

---

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/flask-face
```

### Paste Configuration:

```nginx
# Upstream untuk Gunicorn
upstream flask_app {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;  # Ganti dengan IP atau domain Anda

    # Max upload size (untuk photo upload)
    client_max_body_size 10M;

    # Logs
    access_log /var/log/nginx/flask-face-access.log;
    error_log /var/log/nginx/flask-face-error.log;

    # Static files (CSS, JS)
    location /static {
        alias /home/pi/flask-face/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Dataset images (internal only)
    location /dataset {
        alias /home/pi/flask-face/dataset;
        internal;
    }

    # Models folder (internal only)
    location /models {
        alias /home/pi/flask-face/models;
        internal;
    }

    # Main application (proxy to Gunicorn)
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts untuk face recognition/training
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # WebSocket support (jika nanti pakai)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🔟 Enable Site

### Create Symlink

```bash
# Link ke sites-enabled
sudo ln -s /etc/nginx/sites-available/flask-face /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### Test Nginx Configuration

```bash
sudo nginx -t
```

**Expected Output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Restart Nginx

```bash
sudo systemctl restart nginx

# Enable auto-start
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

## 1️⃣1️⃣ Update Gunicorn Bind (Hanya Internal)

Setelah pakai Nginx, Gunicorn tidak perlu exposed ke public. Update ke internal only:

### Edit Service File

```bash
sudo nano /etc/systemd/system/flask-face.service
```

### Ubah Bind Address

**Dari:**
```
--bind 0.0.0.0:5000 \
```

**Menjadi:**
```
--bind 127.0.0.1:5000 \
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Reload & Restart

```bash
# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart flask-face

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status flask-face
sudo systemctl status nginx
```

---

### Test Access

Sekarang akses via:
- ✅ `http://raspberry-pi-ip` (port 80, via Nginx)
- ❌ `http://raspberry-pi-ip:5000` (tidak bisa, karena internal only)

```bash
# Test dari Raspberry Pi
curl http://localhost

# Test dari komputer lain di LAN
curl http://raspberry-pi-ip
```

---

## 1️⃣2️⃣ Setup HTTPS dengan Let's Encrypt

### Prerequisites

- Domain name pointing ke Raspberry Pi IP
- Port 80 dan 443 terbuka di router (port forwarding)
- Dynamic DNS jika pakai IP dynamic (DuckDNS, No-IP)

---

### Install Certbot

```bash
# Install certbot dan nginx plugin
sudo apt install certbot python3-certbot-nginx -y
```

---

### Get SSL Certificate

**Jika punya domain:**
```bash
# Ganti domain.com dengan domain Anda
sudo certbot --nginx -d domain.com -d www.domain.com
```

**Jika pakai Dynamic DNS (contoh: DuckDNS):**
```bash
sudo certbot --nginx -d yourname.duckdns.org
```

**Follow prompts:**
1. Enter email address
2. Agree to Terms of Service (Y)
3. Share email with EFF (optional)
4. Choose redirect HTTP to HTTPS (option 2 recommended)

---

### Verify HTTPS

```bash
# Test HTTPS
curl https://domain.com

# Browser
https://domain.com
```

---

### Auto-Renewal Setup

Certbot auto-install timer untuk renewal:

```bash
# Check timer status
sudo systemctl status certbot.timer

# Test renewal (dry-run)
sudo certbot renew --dry-run

# Manual renewal (jika perlu)
sudo certbot renew
```

Certificates akan auto-renew setiap 60 hari.

---

### Update Nginx Config (Jika Manual Setup)

Certbot biasanya auto-update config, tapi jika manual:

```bash
sudo nano /etc/nginx/sites-available/flask-face
```

Add SSL config:
```nginx
server {
    listen 443 ssl http2;
    server_name domain.com;

    ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
    
    # SSL config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name domain.com;
    return 301 https://$server_name$request_uri;
}
```

Test & reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 1️⃣3️⃣ Common Issues

### Issue 1: Service Won't Start

**Symptoms:**
```
flask-face.service - failed
```

**Diagnosis:**
```bash
# Check detailed logs
sudo journalctl -u flask-face -n 100 --no-pager

# Check if port already used
sudo netstat -tlnp | grep 5000

# Test manual run
cd /home/pi/flask-face
source venv/bin/activate
gunicorn -w 2 -b 127.0.0.1:5000 run:app
```

**Solutions:**
- Cek typo di service file
- Cek permissions folder/files
- Cek dependencies terinstall semua
- Cek Python path di service file

---

### Issue 2: Connection Refused

**Symptoms:**
```
curl: (7) Failed to connect to localhost port 5000: Connection refused
```

**Diagnosis:**
```bash
# Check if service running
sudo systemctl status flask-face

# Check listening ports
sudo netstat -tlnp | grep gunicorn

# Check firewall
sudo ufw status
```

**Solutions:**
```bash
# Start service if not running
sudo systemctl start flask-face

# If firewall blocking
sudo ufw allow 5000  # For direct access
sudo ufw allow 80    # For nginx
sudo ufw allow 443   # For HTTPS
```

---

### Issue 3: Nginx 502 Bad Gateway

**Symptoms:**
```
Browser: 502 Bad Gateway
```

**Diagnosis:**
```bash
# Check nginx error log
sudo tail -f /var/log/nginx/flask-face-error.log

# Check gunicorn running
sudo systemctl status flask-face

# Check upstream connection
curl http://127.0.0.1:5000
```

**Solutions:**
- Restart flask-face service
- Cek bind address di service file (127.0.0.1:5000)
- Cek upstream di nginx config

---

### Issue 4: Memory Error (TensorFlow)

**Symptoms:**
```
MemoryError or Killed during training
```

**Solutions:**

**Create Swap File (2GB):**
```bash
# Create swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
```

**Reduce Workers:**
```bash
# Edit service file
sudo nano /etc/systemd/system/flask-face.service

# Change workers to 1
--workers 1

# Reload & restart
sudo systemctl daemon-reload
sudo systemctl restart flask-face
```

---

### Issue 5: Permission Denied

**Symptoms:**
```
Permission denied: '/home/pi/flask-face/...'
```

**Solutions:**
```bash
# Fix ownership
sudo chown -R pi:pi /home/pi/flask-face

# Fix permissions
chmod -R 755 /home/pi/flask-face

# Specific folders
chmod 755 /home/pi/flask-face/dataset
chmod 755 /home/pi/flask-face/models
chmod 755 /home/pi/flask-face/logs
chmod 644 /home/pi/flask-face/instance/*.db
```

---

### Issue 6: Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
```bash
# Stop service
sudo systemctl stop flask-face

# Check processes using DB
lsof /home/pi/flask-face/instance/*.db

# Kill hanging processes
sudo killall gunicorn

# Restart
sudo systemctl start flask-face
```

---

## 1️⃣4️⃣ Monitoring All Services

### Real-Time Monitoring

```bash
# Monitor CPU, Memory, Processes
htop

# Monitor all services
watch -n 2 'systemctl status flask-face nginx'

# Monitor network
sudo netstat -tlnp

# Monitor disk usage
df -h

# Monitor logs (all in one screen)
multitail /var/log/nginx/flask-face-access.log \
          /home/pi/flask-face/logs/access.log \
          /home/pi/flask-face/logs/error.log
```

---

### Service Status Check Script

Create monitoring script:

```bash
nano ~/check-services.sh
```

Paste:
```bash
#!/bin/bash

echo "=== Flask Face Services Status ==="
echo ""

# Flask service
echo "Flask-Face Service:"
sudo systemctl is-active flask-face && echo "✅ Running" || echo "❌ Stopped"
echo ""

# Nginx
echo "Nginx Service:"
sudo systemctl is-active nginx && echo "✅ Running" || echo "❌ Stopped"
echo ""

# Port check
echo "Listening Ports:"
sudo netstat -tlnp | grep -E ':(80|443|5000)' || echo "No ports listening"
echo ""

# Memory
echo "Memory Usage:"
free -h | grep Mem
echo ""

# Disk
echo "Disk Usage:"
df -h / | tail -1
echo ""

# Recent errors (last 10 lines)
echo "Recent Errors (Flask):"
sudo journalctl -u flask-face -n 10 --no-pager | grep -i error || echo "No errors"
```

Make executable:
```bash
chmod +x ~/check-services.sh

# Run
./check-services.sh
```

---

### Performance Monitoring

```bash
# CPU & Memory per process
ps aux | grep -E 'gunicorn|nginx'

# Gunicorn worker status
ps aux | grep gunicorn

# Connection count
sudo netstat -an | grep :80 | wc -l

# Active connections to Gunicorn
sudo netstat -an | grep :5000 | wc -l
```

---

### Log Monitoring Dashboard

```bash
# Install lnav (log navigator)
sudo apt install lnav -y

# Use lnav for logs
lnav /home/pi/flask-face/logs/*.log /var/log/nginx/*.log
```

---

## 1️⃣5️⃣ Restart All Services

### Individual Restart

```bash
# Restart Flask service
sudo systemctl restart flask-face

# Restart Nginx
sudo systemctl restart nginx

# Restart both (one by one)
sudo systemctl restart flask-face && sudo systemctl restart nginx
```

---

### Complete System Restart Script

Create restart script:

```bash
nano ~/restart-all.sh
```

Paste:
```bash
#!/bin/bash

echo "🔄 Restarting All Flask-Face Services..."
echo ""

# Stop services in order
echo "1. Stopping Nginx..."
sudo systemctl stop nginx

echo "2. Stopping Flask-Face..."
sudo systemctl stop flask-face

# Wait a bit
sleep 2

# Start services in order
echo "3. Starting Flask-Face..."
sudo systemctl start flask-face

# Wait for Flask to initialize
sleep 3

echo "4. Starting Nginx..."
sudo systemctl start nginx

# Wait
sleep 2

echo ""
echo "✅ Restart Complete!"
echo ""

# Check status
echo "=== Services Status ==="
echo ""

echo "Flask-Face:"
sudo systemctl is-active flask-face && echo "✅ Running" || echo "❌ Failed"

echo ""
echo "Nginx:"
sudo systemctl is-active nginx && echo "✅ Running" || echo "❌ Failed"

echo ""
echo "=== Testing Access ==="
curl -s http://localhost > /dev/null && echo "✅ HTTP working" || echo "❌ HTTP failed"

echo ""
echo "Done! Check logs if any issues:"
echo "  sudo journalctl -u flask-face -n 20"
echo "  sudo journalctl -u nginx -n 20"
```

Make executable:
```bash
chmod +x ~/restart-all.sh

# Run
./restart-all.sh
```

---

### Graceful Reload (No Downtime)

```bash
# Reload Flask-Face (graceful)
sudo systemctl reload flask-face

# Reload Nginx (no downtime)
sudo systemctl reload nginx

# Or via nginx directly
sudo nginx -s reload
```

---

### Full System Reboot

```bash
# Reboot Raspberry Pi
sudo reboot

# Services will auto-start on boot (if enabled)
# Wait 30-60 seconds, then check:

# SSH back in
ssh pi@raspberry-pi-ip

# Check services
sudo systemctl status flask-face
sudo systemctl status nginx

# Test access
curl http://localhost
```

---

## 📊 Performance Optimization

### Gunicorn Workers Tuning

```bash
# Check CPU cores
nproc

# Formula: (2 x cores) + 1
# Pi 3 (4 cores) → 4 workers
# Pi 4 (4 cores) → 4-6 workers
# Pi 5 (4 cores) → 4-8 workers

# Edit service
sudo nano /etc/systemd/system/flask-face.service

# Change workers
--workers 4

# Reload
sudo systemctl daemon-reload
sudo systemctl restart flask-face
```

---

### Nginx Caching

Add to nginx config:
```nginx
# Proxy cache
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=100m inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 5m;
    # ... rest of proxy config
}
```

---

## 🔐 Security Hardening

### Firewall Setup

```bash
# Install UFW
sudo apt install ufw -y

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT!)
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

### Fail2Ban (Prevent Brute Force)

```bash
# Install
sudo apt install fail2ban -y

# Create config
sudo nano /etc/fail2ban/jail.local
```

Paste:
```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/flask-face-error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/flask-face-access.log
```

```bash
# Restart fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

---

## 📚 Summary

### ✅ Checklist Setelah Deploy

- [ ] Services running (flask-face, nginx)
- [ ] Auto-start enabled
- [ ] Logs rotating properly
- [ ] Can access via IP/domain
- [ ] HTTPS working (if setup)
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup script created

---

### 🎯 Quick Command Reference

| Task | Command |
|------|---------|
| **Check service** | `sudo systemctl status flask-face` |
| **Restart service** | `sudo systemctl restart flask-face` |
| **View logs** | `sudo journalctl -u flask-face -f` |
| **Restart nginx** | `sudo systemctl restart nginx` |
| **Test nginx config** | `sudo nginx -t` |
| **Reload nginx** | `sudo systemctl reload nginx` |
| **Check ports** | `sudo netstat -tlnp` |
| **Monitor resources** | `htop` |
| **Reboot system** | `sudo reboot` |

---

### 📞 Troubleshooting Flow

```
Service not responding?
  ↓
Check service status
  ↓
Check logs (journalctl)
  ↓
Check network (netstat)
  ↓
Check permissions
  ↓
Restart services
  ↓
Still issues? Check full system logs
```

---

## 🎉 Selesai!

Aplikasi Flask Face sudah running sebagai **production service** di Raspberry Pi dengan:

✅ Auto-start on boot  
✅ Gunicorn WSGI server  
✅ Nginx reverse proxy  
✅ SSL/HTTPS (optional)  
✅ Logging & monitoring  
✅ Production-ready setup  

**Access URL:**
- Local: `http://raspberry-pi-ip`
- HTTPS: `https://domain.com` (if configured)

**Next Steps:**
- Setup monitoring/alerting
- Regular backups
- Performance tuning
- Security hardening

---

**Version:** 1.0  
**Last Updated:** Jan 20, 2026  
**Status:** ✅ Production Ready
