#!/bin/bash
# Photo API Testing Script

BASE_URL="http://localhost:5000/api"

echo "========================================"
echo "Photo API Testing Script"
echo "========================================"
echo ""

# 1. Create a test user
echo "1️⃣ Creating test user..."
USER_RESPONSE=$(curl -s -X POST $BASE_URL/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}')

USER_ID=$(echo $USER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "   ✓ User created with ID: $USER_ID"
echo "   Response: $USER_RESPONSE"
echo ""

# 2. Upload single photo (create a test image first)
echo "2️⃣ Creating test image..."
python3 << 'PYTHON_SCRIPT'
from PIL import Image

# Create a simple test image
img = Image.new('RGB', (500, 500), color='red')
img.save('/tmp/test_photo1.jpg')

img = Image.new('RGB', (500, 500), color='blue')
img.save('/tmp/test_photo2.png')

print("   ✓ Test images created at /tmp/test_photo1.jpg and /tmp/test_photo2.png")
PYTHON_SCRIPT

echo ""
echo "3️⃣ Uploading single photo..."
if [ -n "$USER_ID" ]; then
  UPLOAD_RESPONSE=$(curl -s -X POST $BASE_URL/photos/$USER_ID/upload \
    -F "file=@/tmp/test_photo1.jpg")
  echo "   Response: $UPLOAD_RESPONSE"
  echo ""
  
  # Extract photo ID
  PHOTO_ID=$(echo $UPLOAD_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
  
  echo "4️⃣ Uploading multiple photos..."
  MULTI_RESPONSE=$(curl -s -X POST $BASE_URL/photos/$USER_ID/upload/multiple \
    -F "files[]=@/tmp/test_photo1.jpg" \
    -F "files[]=@/tmp/test_photo2.png")
  echo "   Response: $MULTI_RESPONSE"
  echo ""
  
  echo "5️⃣ Getting all user photos..."
  GET_RESPONSE=$(curl -s -X GET $BASE_URL/photos/$USER_ID)
  echo "   Response: $GET_RESPONSE"
  echo ""
  
  if [ -n "$PHOTO_ID" ]; then
    echo "6️⃣ Deleting photo $PHOTO_ID..."
    DELETE_RESPONSE=$(curl -s -X DELETE $BASE_URL/photos/$USER_ID/$PHOTO_ID)
    echo "   Response: $DELETE_RESPONSE"
  fi
else
  echo "❌ Failed to create user"
fi

echo ""
echo "========================================"
echo "Testing Complete!"
echo "========================================"
