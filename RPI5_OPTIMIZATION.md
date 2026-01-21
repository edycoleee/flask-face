# Raspberry Pi 5 Optimization Guide

## Sistem Requirements

- **Hardware:** Raspberry Pi 5 (8GB/16GB RAM)
- **OS:** Raspberry Pi OS (64-bit recommended)
- **Python:** 3.9+

## ONNX Runtime GPU Warning

### Warning yang Muncul:
```
[W:onnxruntime:Default, device_discovery.cc:164 DiscoverDevicesForPlatform] 
GPU device discovery failed: device_discovery.cc:89 ReadFileContents 
Failed to open file: "/sys/class/drm/card1/device/vendor"
```

### Penjelasan:
- ✅ **Normal dan tidak berbahaya**
- ONNX Runtime mencoba detect GPU (NVIDIA/AMD)
- Raspberry Pi tidak punya GPU yang didukung
- System otomatis fallback ke **CPU mode**
- Performance tetap baik di CPU mode

### Cara Menghilangkan Warning:

#### Opsi 1: Set Environment Variable (Recommended)
```bash
export ORT_LOGGING_LEVEL=3
python run.py
```

#### Opsi 2: Gunakan Start Script
```bash
bash start_server.sh
```

Script ini otomatis set environment variable.

#### Opsi 3: Edit ~/.bashrc (Permanent)
```bash
echo 'export ORT_LOGGING_LEVEL=3' >> ~/.bashrc
source ~/.bashrc
```

## Performance Tips untuk Raspberry Pi 5

### 1. CPU Mode (Default)
InsightFace sudah diset ke CPU mode:
```python
self.face_app.prepare(ctx_id=-1)  # -1 = CPU mode
```

### 2. Optimize Model Loading
Model buffalo_l sudah optimal untuk CPU:
- **Size:** ~50MB
- **Speed:** 50-100ms per prediction
- **Accuracy:** 95-99%

### 3. Memory Management
Raspberry Pi 16GB cukup untuk:
- Face database: ~5-10MB
- InsightFace model: ~50MB
- Flask app: ~100-200MB
- **Total:** ~200-300MB

### 4. Swap Memory (Optional)
Jika RAM 8GB:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Benchmark di Raspberry Pi 5

### Training (Build Database)
- **10 users, 10 photos each:** ~15-20 seconds
- **50 users, 10 photos each:** ~1-2 minutes
- **100 users, 10 photos each:** ~2-4 minutes

### Prediction Speed
- **Face detection:** 30-50ms
- **Embedding extraction:** 20-40ms
- **Similarity matching:** 5-10ms
- **Total:** 50-100ms per image

### Comparison with CNN Training
| Metric | CNN (Old) | Embedding (New) |
|--------|-----------|-----------------|
| Training Time | 15-60 min | 15-120 sec |
| Memory Usage | 1-2 GB | 200-300 MB |
| Model Size | 100 MB | 50 MB |
| Prediction Speed | 200-500ms | 50-100ms |

## Troubleshooting

### 1. Out of Memory
```bash
# Check memory
free -h

# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 2. Slow Performance
```bash
# Check CPU temperature
vcgencmd measure_temp

# If > 80°C, add cooling or reduce workload
```

### 3. Model Loading Failed
```bash
# Clear cache and re-download
rm -rf ~/.insightface/models/buffalo_l
python -c "from insightface.app import FaceAnalysis; app = FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=-1)"
```

## Production Deployment

### 1. Systemd Service
```bash
sudo nano /etc/systemd/system/flask-face.service
```

```ini
[Unit]
Description=Flask Face Recognition
After=network.target

[Service]
User=sultan
WorkingDirectory=/home/sultan/flask/flask-face
Environment="ORT_LOGGING_LEVEL=3"
ExecStart=/home/sultan/flask/flask-face/venv/bin/python /home/sultan/flask/flask-face/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-face
sudo systemctl start flask-face
sudo systemctl status flask-face
```

### 2. Nginx Reverse Proxy
```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/flask-face
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/flask-face /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Auto-start on Boot
```bash
# Add to crontab
crontab -e

# Add line:
@reboot cd /home/sultan/flask/flask-face && bash start_server.sh
```

## Monitoring

### CPU & Memory
```bash
# Real-time monitoring
htop

# Or
top
```

### Temperature
```bash
# Check temperature
vcgencmd measure_temp

# Continuous monitoring
watch -n 1 vcgencmd measure_temp
```

### Logs
```bash
# Flask logs
tail -f /var/log/flask-face.log

# System logs
journalctl -u flask-face -f
```

## Network Configuration

### Access from Other Devices
```bash
# Find Raspberry Pi IP
hostname -I

# Example: 192.168.1.100
# Access from browser: http://192.168.1.100:5001/api/docs
```

### Firewall (Optional)
```bash
sudo ufw allow 5001/tcp
sudo ufw enable
```

## Best Practices

1. ✅ **Use CPU mode** - GPU tidak perlu untuk Raspberry Pi
2. ✅ **Suppress ONNX warnings** - Set ORT_LOGGING_LEVEL=3
3. ✅ **Monitor temperature** - Jaga < 80°C
4. ✅ **Use swap memory** - Minimal 2GB untuk safety
5. ✅ **Regular backups** - Backup database dan models
6. ✅ **Update system** - `sudo apt update && sudo apt upgrade`

## Quick Commands

```bash
# Start server (tanpa warning)
bash start_server.sh

# Build face database
curl -X POST http://localhost:5001/api/training/start

# Test prediction
bash test_prediction.sh

# Check status
curl http://localhost:5001/api/halo

# Monitor resources
htop

# Check temperature
vcgencmd measure_temp
```

