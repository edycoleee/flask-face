#!/bin/bash

# Test Face Login API
# Usage: ./test_face_login.sh [image_file]

API_BASE="http://localhost:5000/api"
IMAGE_FILE="${1:-}"

echo "=================================="
echo "Face Login API Test"
echo "=================================="
echo ""

# Check if image file is provided
if [ -z "$IMAGE_FILE" ]; then
    echo "❌ Error: No image file provided"
    echo ""
    echo "Usage: $0 <image_file>"
    echo "Example: $0 user_face.jpg"
    exit 1
fi

# Check if file exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Error: File not found: $IMAGE_FILE"
    exit 1
fi

echo "📸 Image: $IMAGE_FILE"
echo ""

# Test: Face Login
echo "🔐 Test: Login with Face Recognition"
echo "POST $API_BASE/auth/login-face"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login-face" \
    -F "file=@$IMAGE_FILE")

echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# Parse results
LOGIN_STATUS=$(echo "$LOGIN_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$LOGIN_STATUS" = "success" ]; then
    echo "✅ Login successful!"
    echo ""
    
    # Extract token and user info
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    USER_ID=$(echo "$LOGIN_RESPONSE" | grep -o '"user_id":[0-9]*' | cut -d':' -f2)
    NAME=$(echo "$LOGIN_RESPONSE" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    CONFIDENCE=$(echo "$LOGIN_RESPONSE" | grep -o '"confidence":[0-9.]*' | head -1 | cut -d':' -f2)
    
    echo "=================================="
    echo "🎯 LOGIN SUCCESS"
    echo "=================================="
    echo "User ID    : $USER_ID"
    echo "Name       : $NAME"
    echo "Confidence : $CONFIDENCE%"
    echo "Token      : $TOKEN"
    echo "=================================="
    echo ""
    
    # Save token for next tests
    echo "$TOKEN" > /tmp/face_login_token.txt
    
    # Test: Verify Token
    echo "🔍 Test: Verify Token"
    echo "POST $API_BASE/auth/verify"
    echo ""
    
    VERIFY_RESPONSE=$(curl -s -X POST "$API_BASE/auth/verify" \
        -H "Content-Type: application/json" \
        -d "{\"token\": \"$TOKEN\"}")
    
    echo "$VERIFY_RESPONSE" | python3 -m json.tool
    echo ""
    
    VERIFY_STATUS=$(echo "$VERIFY_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$VERIFY_STATUS" = "success" ]; then
        echo "✅ Token is valid!"
    else
        echo "❌ Token verification failed!"
    fi
    echo ""
    
    # Test: Get User Tokens
    echo "📋 Test: Get User Active Tokens"
    echo "GET $API_BASE/auth/tokens/$USER_ID"
    echo ""
    
    TOKENS_RESPONSE=$(curl -s "$API_BASE/auth/tokens/$USER_ID")
    echo "$TOKENS_RESPONSE" | python3 -m json.tool
    echo ""
    
    # Test: Logout
    echo "🚪 Test: Logout (Deactivate Token)"
    echo "POST $API_BASE/auth/logout"
    echo ""
    
    read -p "Press Enter to logout (deactivate token)..."
    
    LOGOUT_RESPONSE=$(curl -s -X POST "$API_BASE/auth/logout" \
        -H "Content-Type: application/json" \
        -d "{\"token\": \"$TOKEN\"}")
    
    echo "$LOGOUT_RESPONSE" | python3 -m json.tool
    echo ""
    
    LOGOUT_STATUS=$(echo "$LOGOUT_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$LOGOUT_STATUS" = "success" ]; then
        echo "✅ Logout successful!"
    else
        echo "❌ Logout failed!"
    fi
    
else
    echo "❌ Login failed!"
    ERROR_MSG=$(echo "$LOGIN_RESPONSE" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    echo "Error: $ERROR_MSG"
fi

echo ""
echo "Test completed!"
