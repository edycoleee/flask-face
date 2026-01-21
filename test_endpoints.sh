#!/bin/bash

# Test API endpoints untuk memastikan response benar

echo "=================================================="
echo "Testing API Endpoints"
echo "=================================================="

API_URL="http://localhost:5001/api"

echo ""
echo "1. Testing Training Status Endpoint"
echo "   GET $API_URL/training/status"
echo ""

curl -s "$API_URL/training/status" | python3 -m json.tool

echo ""
echo "=================================================="
echo ""
echo "2. Testing Model Info Endpoint"
echo "   GET $API_URL/face/model-info"
echo ""

curl -s "$API_URL/face/model-info" | python3 -m json.tool

echo ""
echo "=================================================="
echo "Test Complete!"
echo "=================================================="
echo ""
echo "Check the output above:"
echo "- 'class_labels' or 'users' should be an array"
echo "- No undefined or null errors"
echo ""
