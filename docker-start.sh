#!/bin/bash
# ============================================================
# QUICK START SCRIPT - Docker Separated Services
# ============================================================

set -e

echo "============================================================"
echo "🐳 Flask Face Recognition - Docker Setup"
echo "============================================================"

# Step 1: Create network
echo ""
echo "📡 Step 1: Creating Docker network..."
docker network create face_network 2>/dev/null || echo "Network already exists ✓"

# Step 2: Start database
echo ""
echo "🗄️  Step 2: Starting database service..."
docker-compose -f docker-compose.db.yml up -d

# Wait for database
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check database
docker exec face-db-postgres pg_isready -U sultan -d face_db
if [ $? -eq 0 ]; then
    echo "✅ Database is ready!"
else
    echo "❌ Database failed to start!"
    exit 1
fi

# Step 3: Start app
echo ""
echo "🚀 Step 3: Starting Flask application..."
docker-compose -f docker-compose.app.yml up -d --build

# Wait for app
echo ""
echo "⏳ Waiting for application to be ready..."
sleep 10

# Test app
curl -s http://192.168.171.184:5000/api/halo >/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Application is ready!"
else
    echo "⚠️  Application might still be starting..."
fi

# Summary
echo ""
echo "============================================================"
echo "✅ Deployment Complete!"
echo "============================================================"
echo ""
echo "📊 Services:"
echo "  - PostgreSQL: http://192.168.171.184:5432"
echo "  - pgAdmin:    http://192.168.171.184:5050"
echo "  - Flask App:  http://192.168.171.184:5000"
echo ""
echo "📝 Next steps:"
echo "  1. Access web UI: http://192.168.171.184:5000"
echo "  2. Access pgAdmin: http://192.168.171.184:5050"
echo "  3. Check logs: docker-compose -f docker-compose.app.yml logs -f"
echo ""
echo "For detailed documentation, see: docker_live.md"
echo "============================================================"
