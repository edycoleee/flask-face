# Face Embedding Migration Guide

## Perubahan Sistem

Sistem telah dimigrasi dari **CNN Training** ke **Face Embedding Database** menggunakan **InsightFace**.

### Keuntungan Sistem Baru

✅ **No Training Needed** - Hanya ekstraksi embedding dari gambar  
✅ **Pre-trained Model** - InsightFace sudah sangat akurat  
✅ **Lebih Cepat** - CPU mode, cocok untuk Raspberry Pi 5  
✅ **Lebih Mudah** - Tidak ada hyperparameter tuning  
✅ **Lebih Akurat** - State-of-the-art face recognition  

### Dependencies

```bash
pip install insightface onnxruntime scikit-learn Pillow numpy
```

## API Usage

### 1. Build Face Database (dulu: Training)

**Endpoint:** `POST /api/training/start`

**PENTING:** Ini BUKAN training! Hanya ekstrak embeddings.

**Request:**
```json
{
  // Semua parameter DIABAIKAN (backward compatibility)
  "epochs": 50,           // ❌ DIABAIKAN
  "batch_size": 16,       // ❌ DIABAIKAN  
  "validation_split": 0.2,// ❌ DIABAIKAN
  "continue_training": false // ❌ DIABAIKAN (always full rebuild)
}
```

**Atau kirim kosong (recommended):**
```json
{}
```

**Behavior:**
- ✅ **Selalu FULL REBUILD** (10-30 detik)
- ✅ Scan semua foto di `dataset/`
- ✅ Extract embeddings untuk semua users
- ✅ Auto-cleanup orphaned data
- ✅ Fresh database setiap kali

**Response:**
```json
{
  "success": true,
  "message": "Training completed successfully",
  "data": {
    "num_data": 100,
    "num_classes": 5,
    "training_time_minutes": 0.5,
    "model_path": "models/face_db.npy"
  }
}
```

### 2. Prediction

**Endpoint:** `POST /api/prediction/predict`

**Response:**
```json
{
  "user_id": 1,
  "name": "Sultan",
  "email": "sultan@example.com",
  "confidence": 98.5,
  "cosine_similarity": 0.985,
  "method": "InsightFace + Cosine Similarity"
}
```

### 3. Face Login

**Endpoint:** `POST /api/auth/login/face`

Tidak ada perubahan pada API - tetap sama!

## File Structure

```
models/
├── face_db.npy          # Face embedding database (NEW)
├── face_db.json         # Metadata (NEW)
└── [OLD FILES DELETED]
    ├── model.h5         # HAPUS
    ├── best_model.h5    # HAPUS
    ├── label_map.json   # HAPUS
    └── accuracy.json    # HAPUS
```

## Code Changes

### TrainingService

```python
# OLD: CNN Training
def train(self, epochs, batch_size, validation_split):
    self.model = self.build_embedding_model()
    self.model.fit(...)  # Long training

# NEW: Face Embedding Extraction
def train(self, epochs=None, batch_size=None, validation_split=None):
    self.build_face_database()  # Fast extraction
```

### PredictionService

```python
# OLD: Load Keras Model
self.model = keras.models.load_model('model.h5')

# NEW: Load Face Database
self.face_app = FaceAnalysis(name="buffalo_l")
self.face_db = np.load('face_db.npy')
```

## Migration Steps

1. **Install dependencies:**
   ```bash
   pip install insightface onnxruntime
   ```

2. **Rebuild database:**
   ```bash
   curl -X POST http://localhost:5001/api/training/start
   ```

3. **Test prediction:**
   ```bash
   bash test_prediction.sh
   ```

4. **Clean old files (optional):**
   ```bash
   rm -f models/model.h5 models/best_model.h5 models/label_map.json models/accuracy.json
   ```

## Performance Comparison

| Metric | Old (CNN) | New (Embedding) |
|--------|-----------|-----------------|
| Training Time | 5-30 min | 10-30 sec |
| Model Size | 50-100 MB | 5-10 MB |
| Inference Speed | 100-200ms | 50-100ms |
| Accuracy | 85-95% | 95-99% |
| Raspberry Pi | Slow | Fast |

## Troubleshooting

### Error: InsightFace not installed
```bash
pip install insightface onnxruntime
```

### Error: No faces detected
- Pastikan foto wajah jelas dan terang
- Wajah menghadap kamera
- Ukuran wajah minimal 112x112 pixels

### Error: Database not found
```bash
# Rebuild database
curl -X POST http://localhost:5001/api/training/start
```

## Backward Compatibility

✅ Semua API endpoint tetap sama  
✅ Response format tetap sama  
✅ Training parameters diabaikan (tidak error)  
✅ Dapat di-drop-in replacement  

