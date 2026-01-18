#!/bin/bash

# Test Face Prediction API
# Usage: ./test_prediction.sh [image_file]

API_BASE="http://localhost:5000/api"
IMAGE_FILE="${1:-}"

echo "=================================="
echo "Face Prediction API Test"
echo "=================================="
echo ""

# Check if image file is provided
if [ -z "$IMAGE_FILE" ]; then
    echo "❌ Error: No image file provided"
    echo ""
    echo "Usage: $0 <image_file>"
    echo "Example: $0 test_face.jpg"
    exit 1
fi

# Check if file exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Error: File not found: $IMAGE_FILE"
    exit 1
fi

echo "📸 Image: $IMAGE_FILE"
echo ""

# Test 1: Check Model Status
echo "🔍 Test 1: Checking Model Status..."
echo "GET $API_BASE/face/model-info"
echo ""

MODEL_INFO=$(curl -s "$API_BASE/face/model-info")
echo "$MODEL_INFO" | python3 -m json.tool
echo ""

# Check if model is loaded
MODEL_STATUS=$(echo "$MODEL_INFO" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$MODEL_STATUS" != "success" ]; then
    echo "❌ Model not loaded! Please train the model first."
    echo "Run: curl -X POST $API_BASE/training/start -H 'Content-Type: application/json' -d '{\"epochs\": 50}'"
    exit 1
fi

echo "✅ Model is loaded and ready!"
echo ""

# Test 2: Predict Face
echo "🔮 Test 2: Predicting Face..."
echo "POST $API_BASE/face/predict"
echo ""

PREDICTION=$(curl -s -X POST "$API_BASE/face/predict" \
    -F "file=@$IMAGE_FILE")

echo "$PREDICTION" | python3 -m json.tool
echo ""

# Parse results
PRED_STATUS=$(echo "$PREDICTION" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$PRED_STATUS" = "success" ]; then
    echo "✅ Prediction successful!"
    echo ""
    
    # Extract key information
    USER_ID=$(echo "$PREDICTION" | grep -o '"user_id":[0-9]*' | head -1 | cut -d':' -f2)
    NAME=$(echo "$PREDICTION" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    CONFIDENCE=$(echo "$PREDICTION" | grep -o '"confidence":[0-9.]*' | head -1 | cut -d':' -f2)
    
    echo "=================================="
    echo "🎯 PREDICTION RESULT"
    echo "=================================="
    echo "User ID    : $USER_ID"
    echo "Name       : $NAME"
    echo "Confidence : $CONFIDENCE%"
    echo "=================================="
else
    echo "❌ Prediction failed!"
    ERROR_MSG=$(echo "$PREDICTION" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    echo "Error: $ERROR_MSG"
fi

echo ""
echo "Test completed!"
