# 🐳 Docker Deployment Guide - Separated Services

## 📋 Table of Contents
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Daily Workflow](#daily-workflow)
- [HTTPS Setup](#https-setup)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🏗️ Architecture

### **Separated Services Design**

```
┌─────────────────────────────────────────────────────────┐
│  Docker Network: face_network                           │
│                                                           │
│  ┌──────────────────────┐    ┌──────────────────────┐   │
│  │  Database Service    │    │  App Service         │   │
│  │  (Rarely restart)    │    │  (Frequent rebuild)  │   │
│  │                      │    │                      │   │
│  │  - PostgreSQL:5432   │◄───┤  - Flask App:5000    │   │
│  │  - pgAdmin:5050      │    │  - HTTPS:443         │   │
│  │  - pgvector          │    │  - InsightFace       │   │
│  └──────────────────────┘    └──────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### **Files Structure**
```
flask-face/
├── docker-compose.db.yml      # Database service only
├── docker-compose.app.yml     # Flask app service only
├── Dockerfile                 # Flask app image build
├── .dockerignore              # Exclude files from build
├── init.sql                   # Database initialization
├── requirements.txt           # Python dependencies
├── run.py                     # Flask entrypoint
├── app/                       # Application code
├── dataset/                   # Training photos
├── models/                    # Face embeddings
└── certs/                     # SSL certificates (optional)
```

---

## ✅ Prerequisites

1. **Docker & Docker Compose installed**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Network connectivity**
   ```bash
   # Pastikan port tersedia
   sudo netstat -tuln | grep -E '5432|5000|5050|443'
   ```

3. **Files required**
   - `init.sql` - Database schema
   - `requirements.txt` - Python dependencies
   - `app/` folder - Flask application

---

## 🚀 Quick Start

### **Step 1: Create Docker Network**
```bash
# Create shared network untuk database dan app
docker network create face_network
```

### **Step 2: Start Database Service**
```bash
# Start PostgreSQL + pgAdmin
docker-compose -f docker-compose.db.yml up -d

# Check logs
docker-compose -f docker-compose.db.yml logs -f postgres

# Wait sampai muncul: "database system is ready to accept connections"
# Press Ctrl+C untuk exit logs
```

### **Step 3: Verify Database**
```bash
# Check database health
docker exec -it face-db-postgres psql -U sultan -d face_db -c "\dt"

# Should show tables: users, photos, auth_tokens, face_embeddings
```

### **Step 4: Start Flask Application**
```bash
# Build & start Flask app
docker-compose -f docker-compose.app.yml up -d --build

# Check logs
docker-compose -f docker-compose.app.yml logs -f flask-app

# Wait sampai muncul: "Running on http://0.0.0.0:5000"
```

### **Step 5: Test Application**
```bash
# Test health endpoint
curl http://192.168.171.184:5000/api/halo

# Access web interface
# Open browser: http://192.168.171.184:5000
```

---

## 📝 Detailed Setup

### **1. Database Service Setup**

**File: `docker-compose.db.yml`**
- PostgreSQL 16 with pgvector extension
- pgAdmin for GUI management
- Persistent volume for data safety
- Auto-initialization with `init.sql`

**Start Database:**
```bash
cd /home/sultan/flask-face
docker-compose -f docker-compose.db.yml up -d
```

**Access pgAdmin:**
- URL: `http://192.168.171.184:5050`
- Email: `admin@admin.com`
- Password: `admin`

**Add PostgreSQL Server in pgAdmin:**
- Host: `192.168.171.184` (atau `postgres` jika di network yang sama)
- Port: `5432`
- Database: `face_db`
- Username: `sultan`
- Password: `Sulfat123#!`

**Check Database Status:**
```bash
# Container status
docker ps | grep postgres

# Database logs
docker logs face-db-postgres

# Connect to database
docker exec -it face-db-postgres psql -U sultan -d face_db

# Inside psql:
\dt                    # List tables
\d users               # Describe users table
SELECT COUNT(*) FROM users;
\q                     # Quit
```

---

### **2. Flask App Service Setup**

**File: `docker-compose.app.yml`**
- Flask application with InsightFace
- PostgreSQL connection via network
- Volume mounts for data persistence
- Auto-restart on failure

**Build & Start App:**
```bash
cd /home/sultan/flask-face
docker-compose -f docker-compose.app.yml up -d --build
```

**Check App Status:**
```bash
# Container status
docker ps | grep face-app

# Application logs
docker logs -f face-app

# Health check
curl http://192.168.171.184:5000/api/halo
```

**Access Web UI:**
- URL: `http://192.168.171.184:5000`
- Test endpoints di Swagger UI

---

## 🔄 Daily Workflow

### **Development Cycle**

#### **Code Changes (Fast - 30s)**
```bash
# 1. Edit code di app/ folder
nano app/api/users.py

# 2. Rebuild app only (database tetap running)
docker-compose -f docker-compose.app.yml up -d --build

# 3. Check logs
docker-compose -f docker-compose.app.yml logs -f flask-app

# Database tidak terpengaruh ✅
```

#### **Database Changes (Rare)**
```bash
# 1. Edit init.sql atau schema
nano init.sql

# 2. Recreate database (WARNING: data loss!)
docker-compose -f docker-compose.db.yml down -v
docker-compose -f docker-compose.db.yml up -d

# 3. Migrate data (if needed)
python migrate_to_postgres.py
```

#### **View Logs**
```bash
# Database logs
docker-compose -f docker-compose.db.yml logs -f postgres

# App logs
docker-compose -f docker-compose.app.yml logs -f flask-app

# Both
docker-compose -f docker-compose.db.yml logs -f &
docker-compose -f docker-compose.app.yml logs -f
```

#### **Restart Services**
```bash
# Restart app only (code changes)
docker-compose -f docker-compose.app.yml restart

# Restart database (rare)
docker-compose -f docker-compose.db.yml restart postgres

# Rebuild app (dependency changes)
docker-compose -f docker-compose.app.yml up -d --build
```

#### **Stop Services**
```bash
# Stop app (database tetap running)
docker-compose -f docker-compose.app.yml down

# Stop database (WARNING: app akan error!)
docker-compose -f docker-compose.db.yml down

# Stop all
docker-compose -f docker-compose.app.yml down
docker-compose -f docker-compose.db.yml down
```

---

## 🔒 HTTPS Setup

### **Step 1: Generate SSL Certificates**

#### **Self-Signed Certificate (Development)**
```bash
# Create certs directory
mkdir -p certs

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/CN=192.168.171.184"

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
```

#### **Let's Encrypt Certificate (Production)**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate (requires domain)
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/key.pem
```

### **Step 2: Update Flask App for HTTPS**

**Edit `run.py`:**
```python
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Check if SSL certificates exist
    cert_file = 'certs/cert.pem'
    key_file = 'certs/key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # HTTPS mode
        app.run(
            host='0.0.0.0',
            port=443,
            ssl_context=(cert_file, key_file),
            debug=False
        )
    else:
        # HTTP mode
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False
        )
```

### **Step 3: Update docker-compose.app.yml**

Uncomment HTTPS port dan volume:
```yaml
ports:
  - "192.168.171.184:5000:5000"
  - "192.168.171.184:443:443"   # ✅ Uncomment this

volumes:
  - ./certs:/app/certs:ro       # ✅ Uncomment this
```

### **Step 4: Rebuild App**
```bash
# Rebuild dengan HTTPS support
docker-compose -f docker-compose.app.yml up -d --build

# Test HTTPS
curl -k https://192.168.171.184
```

**Database tidak terpengaruh sama sekali! ✅**

---

## 🔧 Troubleshooting

### **Problem: App tidak bisa connect ke database**

**Solution:**
```bash
# 1. Check network
docker network inspect face_network

# 2. Check database running
docker ps | grep postgres

# 3. Check database health
docker exec -it face-db-postgres pg_isready -U sultan -d face_db

# 4. Test connection dari app container
docker exec -it face-app curl postgres:5432
```

### **Problem: Port already in use**

**Solution:**
```bash
# Find process using port
sudo lsof -i :5432
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port di docker-compose files
```

### **Problem: Build failed - dependency error**

**Solution:**
```bash
# Clear Docker cache
docker-compose -f docker-compose.app.yml down
docker system prune -a

# Rebuild from scratch
docker-compose -f docker-compose.app.yml up -d --build --no-cache
```

### **Problem: Database data corrupted**

**Solution:**
```bash
# Backup data first
docker exec face-db-postgres pg_dump -U sultan face_db > backup.sql

# Remove volume dan recreate
docker-compose -f docker-compose.db.yml down -v
docker-compose -f docker-compose.db.yml up -d

# Restore data
cat backup.sql | docker exec -i face-db-postgres psql -U sultan -d face_db
```

---

## 🛠️ Maintenance

### **Daily Tasks**

#### **Check System Health**
```bash
# Check all containers
docker ps

# Check disk usage
docker system df

# Check logs for errors
docker-compose -f docker-compose.app.yml logs --tail=100 | grep ERROR
```

#### **Update Application**
```bash
# Pull latest code
git pull

# Rebuild app only (30s)
docker-compose -f docker-compose.app.yml up -d --build

# Database tetap running ✅
```

#### **Monitor Resources**
```bash
# Container stats
docker stats

# Database size
docker exec face-db-postgres psql -U sultan -d face_db -c "
SELECT pg_size_pretty(pg_database_size('face_db'));"

# Logs size
du -sh logs/
```

---

### **Weekly Tasks**

#### **Database Backup**
```bash
# Create backup directory
mkdir -p backups

# Backup database
docker exec face-db-postgres pg_dump -U sultan face_db > \
  backups/face_db_$(date +%Y%m%d).sql

# Backup face embeddings
docker exec face-db-postgres pg_dump -U sultan -t face_embeddings face_db > \
  backups/embeddings_$(date +%Y%m%d).sql

# Compress
gzip backups/face_db_$(date +%Y%m%d).sql
```

#### **Cleanup Logs**
```bash
# Rotate Docker logs
docker-compose -f docker-compose.app.yml logs --no-color > logs/app_$(date +%Y%m%d).log
docker-compose -f docker-compose.db.yml logs --no-color > logs/db_$(date +%Y%m%d).log

# Truncate old logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' face-app)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' face-db-postgres)
```

#### **Update Docker Images**
```bash
# Pull latest base images
docker pull pgvector/pgvector:pg16
docker pull dpage/pgadmin4:latest
docker pull python:3.11-slim

# Rebuild app dengan latest base
docker-compose -f docker-compose.app.yml up -d --build
```

---

### **Monthly Tasks**

#### **Database Maintenance**
```bash
# Vacuum database
docker exec face-db-postgres psql -U sultan -d face_db -c "VACUUM ANALYZE;"

# Reindex
docker exec face-db-postgres psql -U sultan -d face_db -c "REINDEX DATABASE face_db;"

# Check index health
docker exec face-db-postgres psql -U sultan -d face_db -c "
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan;"
```

#### **Security Updates**
```bash
# Update host system
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo apt install docker-ce docker-ce-cli containerd.io

# Rebuild all with latest security patches
docker-compose -f docker-compose.app.yml up -d --build --no-cache
```

---

## 📊 Performance Tuning

### **Database Optimization**
```bash
# Edit postgresql.conf (inside container)
docker exec -it face-db-postgres bash
nano /var/lib/postgresql/data/postgresql.conf

# Recommended settings:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 16MB
# maintenance_work_mem = 128MB
# max_connections = 100

# Restart database
docker-compose -f docker-compose.db.yml restart postgres
```

### **App Optimization**
```bash
# Use Gunicorn for production
# Add to requirements.txt:
# gunicorn==21.2.0

# Update Dockerfile CMD:
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]

# Rebuild
docker-compose -f docker-compose.app.yml up -d --build
```

---

## 🎯 Best Practices

### **✅ DO:**
- Keep database running 24/7
- Rebuild app frequently for updates
- Backup database weekly
- Monitor disk usage daily
- Use incremental training for new users
- Test changes in development first
- Use separate networks for security
- Enable HTTPS in production

### **❌ DON'T:**
- Restart database unless necessary
- Store large files in Docker images
- Use `down -v` on production database
- Run without backups
- Expose database port to internet
- Use default passwords in production
- Mix development and production data

---

## 📞 Support & References

### **Documentation:**
- PostgreSQL: https://www.postgresql.org/docs/
- pgvector: https://github.com/pgvector/pgvector
- Docker: https://docs.docker.com/
- Flask: https://flask.palletsprojects.com/

### **Common Commands Reference:**
```bash
# Start services
docker-compose -f docker-compose.db.yml up -d
docker-compose -f docker-compose.app.yml up -d --build

# Stop services
docker-compose -f docker-compose.app.yml down
docker-compose -f docker-compose.db.yml down

# View logs
docker-compose -f docker-compose.app.yml logs -f
docker-compose -f docker-compose.db.yml logs -f

# Rebuild app
docker-compose -f docker-compose.app.yml up -d --build

# Backup database
docker exec face-db-postgres pg_dump -U sultan face_db > backup.sql

# Restore database
cat backup.sql | docker exec -i face-db-postgres psql -U sultan -d face_db

# Clean up
docker system prune -a
docker volume prune
```

---

## 🚀 Summary

**Separated services memberikan:**
- ✅ **Fast iteration**: 30s rebuild (app only) vs 2-5min (full stack)
- ✅ **Data safety**: Database running 24/7, tidak terpengaruh app updates
- ✅ **Easy HTTPS setup**: Update app config tanpa touching database
- ✅ **Production ready**: Independent scaling dan maintenance
- ✅ **Development friendly**: Quick testing dan debugging

**Perfect untuk:**
- Production deployment dengan CI/CD
- Development dengan frequent code changes
- HTTPS/SSL configuration
- Multi-developer teams
- Long-running database stability

---

**Happy Deploying! 🐳🚀**
