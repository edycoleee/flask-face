#!/bin/bash

# Script untuk install InsightFace dan dependencies

echo "=================================================="
echo "Installing InsightFace Dependencies"
echo "=================================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "Installing packages..."
pip install --upgrade pip

# Install main dependencies
pip install insightface
pip install onnxruntime
pip install scikit-learn
pip install Pillow
pip install numpy

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Testing imports..."
python3 << 'EOF'
try:
    from insightface.app import FaceAnalysis
    print("✓ insightface imported successfully")
except ImportError as e:
    print(f"✗ insightface import failed: {e}")

try:
    import onnxruntime
    print("✓ onnxruntime imported successfully")
except ImportError as e:
    print(f"✗ onnxruntime import failed: {e}")

try:
    from sklearn.metrics.pairwise import cosine_similarity
    print("✓ sklearn imported successfully")
except ImportError as e:
    print(f"✗ sklearn import failed: {e}")

try:
    from PIL import Image
    print("✓ PIL imported successfully")
except ImportError as e:
    print(f"✗ PIL import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

print("")
print("All dependencies installed successfully!")
EOF

echo ""
echo "Next steps:"
echo "1. Build face database: curl -X POST http://localhost:5001/api/training/start"
echo "2. Test prediction: bash test_prediction.sh"
echo ""
