# FASE 5 - Testing & Prediction Documentation

## 📋 Overview
FASE 5 mengimplementasikan face recognition prediction menggunakan trained CNN model (MobileNetV2).

## 🚀 Features

### 1. Face Recognition API
- **Endpoint**: `POST /api/face/predict`
- **Input**: Image file (JPG/PNG)
- **Output**: 
  - `user_id`: ID user yang diprediksi
  - `name`: Nama user
  - `email`: Email user  
  - `confidence`: Confidence score (0-100%)
  - `all_predictions`: Top 3 predictions dengan confidence

### 2. Model Information API
- **Endpoint**: `GET /api/face/model-info`
- **Output**: Status model, jumlah classes, accuracy, dll

### 3. Web UI - Prediction Tab
- Upload photo untuk prediction
- Camera capture untuk real-time prediction
- Display hasil prediction dengan:
  - Identified user (nama, email, user ID)
  - Confidence score
  - Top 3 predictions dengan confidence bar

## 📡 API Usage

### Predict Face (cURL)
```bash
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@path/to/photo.jpg"
```

### Response Example
```json
{
  "status": "success",
  "message": "Prediction successful",
  "data": {
    "user_id": 2,
    "name": "John Doe",
    "email": "john@example.com",
    "confidence": 98.45,
    "all_predictions": [
      {
        "user_id": 2,
        "name": "John Doe",
        "confidence": 98.45
      },
      {
        "user_id": 3,
        "name": "Jane Smith",
        "confidence": 1.23
      },
      {
        "user_id": 4,
        "name": "Bob Wilson",
        "confidence": 0.32
      }
    ]
  }
}
```

### Get Model Info
```bash
curl http://localhost:5000/api/face/model-info
```

### Response Example
```json
{
  "status": "success",
  "message": "Model is loaded and ready",
  "data": {
    "loaded": true,
    "model_path": "models/model.h5",
    "num_classes": 3,
    "classes": ["2", "3", "4"],
    "accuracy": 0.9845,
    "training_date": "2026-01-18T10:30:00"
  }
}
```

## 🖥️ Web UI Usage

### 1. Access Prediction Tab
- Buka browser: `http://localhost:5000`
- Klik tab **🔮 Prediction**

### 2. Check Model Status
- Klik **🔄 Refresh Status**
- Pastikan model sudah di-load dan ready

### 3. Upload Photo Method
1. Pilih tab **📤 Upload Photo**
2. Click **Select Photo** dan pilih gambar wajah
3. Preview akan muncul
4. Klik **🔍 Predict Face**
5. Hasil prediction akan ditampilkan

### 4. Camera Capture Method
1. Pilih tab **📷 Capture from Camera**
2. Klik **🎥 Start Camera**
3. Posisikan wajah di depan kamera
4. Klik **📸 Capture Photo**
5. Klik **🔍 Predict Face**
6. Hasil prediction akan ditampilkan

## 🎯 Prediction Results Display

### Main Result
- **User Avatar**: Inisial nama user
- **User Name**: Nama lengkap
- **Email**: Email address
- **User ID**: Database ID
- **Confidence**: Score prediksi (0-100%)

### Alternative Predictions
- Table dengan top 3 predictions
- Confidence bar visual untuk setiap prediction
- Highlighting untuk top prediction (hijau)

## 🔧 Technical Implementation

### Backend Architecture

#### 1. PredictionService (`app/services/prediction_service.py`)
```python
class PredictionService:
    - load_model(): Load trained model & label map
    - preprocess_image(): Resize & normalize image
    - predict(): Run prediction & return results
    - get_model_info(): Get model status & info
```

**Key Features:**
- Lazy loading: Model di-load hanya saat dibutuhkan
- Error handling untuk missing dependencies
- Batch normalization & preprocessing
- Top-N predictions support

#### 2. API Endpoint (`app/api/prediction.py`)
```python
@api.route("/predict")
class FacePrediction:
    - POST: Upload image & get prediction
    
@api.route("/model-info")  
class ModelInfo:
    - GET: Get model information
```

**Features:**
- File validation (JPG/PNG only)
- Temporary file handling
- Automatic cleanup
- Comprehensive error handling

### Frontend Implementation

#### 1. HTML Structure (`templates/page.html`)
- Prediction tab dengan upload/camera options
- Model status display
- Results display card

#### 2. JavaScript Functions (`static/page.js`)
```javascript
// Core Functions
- checkPredictionModelStatus(): Check model availability
- handlePredictUpload(): Handle file upload prediction
- handlePredictCamera(): Handle camera capture prediction
- displayPredictionResults(): Display formatted results

// Camera Functions
- startPredictCamera(): Initialize camera stream
- stopPredictCamera(): Stop camera stream
- capturePredictPhoto(): Capture photo from video stream
```

#### 3. CSS Styling (`static/page.css`)
- Gradient background untuk main result
- Confidence badge dengan highlighting
- Animated confidence bars
- Responsive table layout

## 🧪 Testing Workflow

### Complete Testing Steps:

1. **Prepare Data**
   - Ensure users created di database
   - Upload minimal 5-10 photos per user
   
2. **Train Model**
   - Go to Training tab
   - Configure parameters
   - Start training
   - Wait for completion
   
3. **Test Prediction**
   - Go to Prediction tab
   - Check model status (should be ready)
   - Upload test photo atau capture dari camera
   - Verify prediction results

### Expected Results:
- ✅ High confidence (>80%) untuk trained users
- ✅ Top prediction matches actual user
- ✅ Low confidence untuk unknown faces
- ✅ Real-time response (<2 seconds)

## 📊 Model Performance

### MobileNetV2 Advantages:
- **Lightweight**: ~3.5M parameters
- **Fast inference**: <1s pada Raspberry Pi 5
- **Pre-trained**: Transfer learning dari ImageNet
- **Accurate**: 90-95% accuracy dengan minimal training data

### Typical Performance:
- **Training time**: 5-10 minutes (50 epochs, 3 users, 30 photos)
- **Prediction time**: 0.5-1.5 seconds
- **Memory usage**: ~500MB RAM
- **Accuracy**: 85-95% (depends on data quality)

## 🔍 Troubleshooting

### Model Not Found
```
Error: Model not found. Please train the model first.
```
**Solution**: Go to Training tab dan train model dulu

### Low Confidence Score
```
Confidence: 45%
```
**Possible causes:**
- Poor image quality
- Different lighting conditions
- Face not clearly visible
- Need more training data

**Solutions:**
- Retrain dengan lebih banyak photos
- Ensure good lighting saat capture
- Use high-quality images

### Wrong Prediction
```
Predicted: User A (should be User B)
```
**Solutions:**
- Add more diverse training photos
- Increase training epochs
- Check data quality
- Continue training untuk improvement

## 🎨 UI Features

### Visual Enhancements:
- 🎨 Gradient backgrounds
- 📊 Animated confidence bars
- ✨ Smooth transitions
- 🖼️ Image preview
- 📱 Responsive design

### User Experience:
- Clear status indicators
- Real-time feedback
- Error messages dengan suggestions
- Loading states
- Success confirmations

## 🚀 Next Steps / Improvements

### Potential Enhancements:
1. **Batch Prediction**: Upload multiple photos sekaligus
2. **History Log**: Save prediction history
3. **Real-time Video**: Continuous face recognition dari video stream
4. **Threshold Setting**: Configure minimum confidence threshold
5. **Face Detection**: Auto-crop faces dari larger images
6. **Multi-face Support**: Detect multiple faces dalam satu foto
7. **Export Results**: Download prediction results as CSV/JSON

## 📖 API Documentation

Full API documentation tersedia di:
- Swagger UI: `http://localhost:5000/api/docs`
- Namespace: `/face`

## ✅ Completion Checklist

- [x] Prediction service implementation
- [x] API endpoints (predict, model-info)
- [x] Web UI integration
- [x] Upload photo method
- [x] Camera capture method
- [x] Results display
- [x] Error handling
- [x] Documentation

---

## 🎉 FASE 5 COMPLETE!

Face recognition prediction sudah fully functional dengan:
- ✅ MobileNetV2 pre-trained model
- ✅ REST API endpoints
- ✅ Interactive web UI
- ✅ Upload & camera capture
- ✅ Real-time prediction
- ✅ Confidence scoring
- ✅ Top-N predictions

**Ready for production testing!** 🚀
