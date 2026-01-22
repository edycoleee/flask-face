#!/bin/bash
# ============================================================
# STOP SCRIPT - Docker Separated Services
# ============================================================

echo "============================================================"
echo "🛑 Stopping Flask Face Recognition Services"
echo "============================================================"

# Stop app
echo ""
echo "🛑 Stopping Flask application..."
docker-compose -f docker-compose.app.yml down

# Stop database (optional - comment out to keep running)
echo ""
echo "🛑 Stopping database service..."
docker-compose -f docker-compose.db.yml down

# Summary
echo ""
echo "============================================================"
echo "✅ All services stopped!"
echo "============================================================"
echo ""
echo "To keep database running (recommended):"
echo "  Comment out database stop in this script"
echo ""
echo "To start again:"
echo "  ./docker-start.sh"
echo "============================================================"
