# Clean Output Guide - Suppress Warnings

## Warnings yang Muncul (Normal untuk Raspberry Pi)

### 1. CUDA Provider Warning
```
UserWarning: Specified provider 'CUDAExecutionProvider' is not in available provider names.
Available providers: 'AzureExecutionProvider, CPUExecutionProvider'
```
**Penjelasan:** InsightFace mencoba gunakan GPU CUDA, tapi RPI tidak punya NVIDIA GPU.  
**Solusi:** ✅ Sudah di-suppress otomatis

---

### 2. ONNX Runtime Verbose Logging
```
Applied providers: ['CPUExecutionProvider'], with options: {'CPUExecutionProvider': {}}
find model: /home/sultan/.insightface/models/buffalo_l/...
```
**Penjelasan:** InsightFace load semua model components (detection, recognition, landmarks).  
**Solusi:** ✅ Sudah di-suppress otomatis

---

### 3. FutureWarning - estimate deprecated
```
FutureWarning: `estimate` is deprecated since version 0.26 and will be removed in version 2.2.
Please use `SimilarityTransform.from_estimate` class constructor instead.
```
**Penjelasan:** Warning dari library scikit-image yang digunakan InsightFace.  
**Solusi:** ✅ Sudah di-suppress otomatis

---

## Clean Output Sudah Aktif!

Semua file sudah diupdate untuk output yang lebih bersih:

### ✅ File yang Diubah:

1. **`run.py`**
   - Suppress all Python warnings
   - Set ONNX logging level
   - Disable verbose TensorFlow/ONNX logs

2. **`app/services/training_service.py`**
   - Suppress warnings import
   - Set InsightFace logger ke ERROR only

3. **`app/services/prediction_service.py`**
   - Suppress warnings import
   - Set InsightFace logger ke ERROR only

4. **`start_server.sh`**
   - Set environment variables untuk suppress semua warnings

---

## Cara Menggunakan

### Development Mode (Clean Output)
```bash
bash start_server.sh
```

Output yang muncul:
```
==================================================
Starting Flask Face Recognition Server
==================================================
Raspberry Pi 5 - CPU Mode (No GPU)

Activating virtual environment...
Starting server on http://0.0.0.0:5001
Press CTRL+C to stop

 * Serving Flask app 'run'
 * Debug mode: on
 * Running on http://0.0.0.0:5001
```

### Production Mode (Super Clean)
```bash
bash start_production.sh
```

Output minimal - hanya request logs.

---

## Yang Masih Muncul (Normal)

### 1. Flask Request Logs
```
127.0.0.1 - - [21/Jan/2026 20:12:30] "POST /api/training/start HTTP/1.1" 200 -
```
**Normal** - Ini log HTTP request yang berguna untuk monitoring.

### 2. Application Logs (INFO level)
```
Loading InsightFace model (buffalo_l)...
✓ InsightFace model loaded successfully
```
**Normal** - Ini log aplikasi kita sendiri untuk tracking progress.

---

## Customize Logging Level

### Untuk Development (Verbose)
Edit `run.py`:
```python
logging.basicConfig(
    level=logging.INFO,  # INFO = verbose
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Untuk Production (Minimal)
Edit `run.py`:
```python
logging.basicConfig(
    level=logging.WARNING,  # WARNING = minimal
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Untuk Silent (Hampir Tidak Ada Log)
Edit `run.py`:
```python
logging.basicConfig(
    level=logging.ERROR,  # ERROR = silent
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Troubleshooting

### Warning Masih Muncul?

Restart server dengan clean environment:
```bash
# Stop server (CTRL+C)
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Restart
bash start_server.sh
```

### Download Model Log Masih Muncul?

Normal untuk **first run only**. Model di-download sekali saja:
```
download_path: /home/sultan/.insightface/models/buffalo_l
Downloading buffalo_l.zip...
100%|████████████| 281857/281857 [04:43<00:00, 993.99KB/s]
```

Setelah download selesai, tidak akan muncul lagi di run berikutnya.

---

## Environment Variables Summary

```bash
# Set di ~/.bashrc untuk permanent:
export PYTHONWARNINGS=ignore          # Suppress Python warnings
export ORT_LOGGING_LEVEL=3            # ONNX Runtime quiet
export TF_CPP_MIN_LOG_LEVEL=3         # TensorFlow quiet
export GLOG_minloglevel=3             # Google logging quiet
```

Atau gunakan script `start_server.sh` yang sudah set semua otomatis.

---

## Result

### Before (Verbose):
```
[W:onnxruntime:Default, device_discovery.cc:164] GPU device discovery failed...
UserWarning: Specified provider 'CUDAExecutionProvider' is not in available...
Applied providers: ['CPUExecutionProvider'], with options: {'CPUExecutionProvider': {}}
find model: /home/sultan/.insightface/models/buffalo_l/1k3d68.onnx...
find model: /home/sultan/.insightface/models/buffalo_l/2d106det.onnx...
find model: /home/sultan/.insightface/models/buffalo_l/det_10g.onnx...
FutureWarning: `estimate` is deprecated...
```

### After (Clean):
```
Loading InsightFace model (buffalo_l)...
✓ InsightFace model loaded successfully
✓ Face database loaded: 20 embeddings
127.0.0.1 - - [21/Jan/2026 20:18:12] "POST /api/training/start HTTP/1.1" 200 -
```

**Much cleaner!** 🎉

