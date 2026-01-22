# 🚀 Docker Quick Reference - Cheat Sheet

## 📋 Daily Commands

### **Start Services**
```bash
# Quick start (all)
./docker-start.sh

# Manual start
docker network create face_network
docker-compose -f docker-compose.db.yml up -d
docker-compose -f docker-compose.app.yml up -d --build
```

### **Stop Services**
```bash
# Quick stop (all)
./docker-stop.sh

# Stop app only (keep database running)
docker-compose -f docker-compose.app.yml down

# Stop database (rare)
docker-compose -f docker-compose.db.yml down
```

### **Restart Services**
```bash
# Restart app only
docker-compose -f docker-compose.app.yml restart

# Rebuild app (code changes)
docker-compose -f docker-compose.app.yml up -d --build
```

### **View Logs**
```bash
# App logs (live)
docker-compose -f docker-compose.app.yml logs -f

# Database logs (live)
docker-compose -f docker-compose.db.yml logs -f

# Last 100 lines
docker-compose -f docker-compose.app.yml logs --tail=100
```

---

## 🔧 Maintenance Commands

### **Database**
```bash
# Backup
docker exec face-db-postgres pg_dump -U sultan face_db > backup.sql

# Restore
cat backup.sql | docker exec -i face-db-postgres psql -U sultan -d face_db

# Connect to database
docker exec -it face-db-postgres psql -U sultan -d face_db

# Check tables
docker exec -it face-db-postgres psql -U sultan -d face_db -c "\dt"

# Check data
docker exec -it face-db-postgres psql -U sultan -d face_db -c "SELECT COUNT(*) FROM users;"
```

### **Application**
```bash
# Shell into app container
docker exec -it face-app bash

# Check Python version
docker exec face-app python --version

# Check installed packages
docker exec face-app pip list

# Run migration
docker exec face-app python migrate_to_postgres.py
```

### **Cleanup**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (CAREFUL!)
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```

---

## 📊 Monitoring Commands

### **Status Check**
```bash
# All containers
docker ps

# Container stats (CPU, Memory)
docker stats

# Disk usage
docker system df

# Network info
docker network inspect face_network
```

### **Health Check**
```bash
# Database health
docker exec face-db-postgres pg_isready -U sultan -d face_db

# App health
curl http://192.168.171.184:5000/api/halo

# Container health
docker inspect --format='{{.State.Health.Status}}' face-app
```

---

## 🔒 HTTPS Setup

### **Generate SSL Certificate**
```bash
# Self-signed (development)
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/CN=192.168.171.184"
```

### **Enable HTTPS**
```bash
# 1. Generate certificates (above)

# 2. Edit docker-compose.app.yml
# Uncomment:
#   - "192.168.171.184:443:443"
#   - ./certs:/app/certs:ro

# 3. Rebuild app
docker-compose -f docker-compose.app.yml up -d --build

# 4. Test
curl -k https://192.168.171.184
```

---

## 🐛 Troubleshooting

### **App can't connect to database**
```bash
# Check database running
docker ps | grep postgres

# Check network
docker network inspect face_network

# Test connection
docker exec face-app ping face-db-postgres
```

### **Port already in use**
```bash
# Find process
sudo lsof -i :5432
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### **Build failed**
```bash
# Clear cache
docker system prune -a

# Rebuild from scratch
docker-compose -f docker-compose.app.yml up -d --build --no-cache
```

### **Database data corrupted**
```bash
# Backup first!
docker exec face-db-postgres pg_dump -U sultan face_db > emergency_backup.sql

# Recreate database
docker-compose -f docker-compose.db.yml down -v
docker-compose -f docker-compose.db.yml up -d

# Restore
cat emergency_backup.sql | docker exec -i face-db-postgres psql -U sultan -d face_db
```

---

## 📝 File Structure

```
flask-face/
├── docker-compose.db.yml      # Database service
├── docker-compose.app.yml     # App service
├── Dockerfile                 # App image
├── docker-start.sh            # Quick start
├── docker-stop.sh             # Quick stop
├── docker_live.md             # Full documentation
└── DOCKER_CHEATSHEET.md       # This file
```

---

## 🎯 Common Workflows

### **Development: Code Change**
```bash
# 1. Edit code
nano app/api/users.py

# 2. Rebuild app (30s)
docker-compose -f docker-compose.app.yml up -d --build

# 3. Check logs
docker-compose -f docker-compose.app.yml logs -f
```

### **Add New User**
```bash
# 1. Create user via API or web UI

# 2. Upload photos

# 3. Incremental training
curl -X POST http://192.168.171.184:5000/api/training/incremental \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'

# 4. Test verification
curl -X POST http://192.168.171.184:5000/api/auth/login-face-verify \
  -F "user_id=123" \
  -F "file=@test.jpg"
```

### **Database Backup (Weekly)**
```bash
# 1. Backup to file
docker exec face-db-postgres pg_dump -U sultan face_db > \
  backups/face_db_$(date +%Y%m%d).sql

# 2. Compress
gzip backups/face_db_$(date +%Y%m%d).sql

# 3. Verify backup
ls -lh backups/
```

### **Production Update**
```bash
# 1. Pull latest code
git pull

# 2. Rebuild app only
docker-compose -f docker-compose.app.yml up -d --build

# 3. Check logs for errors
docker-compose -f docker-compose.app.yml logs --tail=100

# 4. Test health
curl http://192.168.171.184:5000/api/halo

# Database tetap running tanpa downtime! ✅
```

---

## 🔗 Access URLs

- **Flask App**: http://192.168.171.184:5000
- **Flask HTTPS**: https://192.168.171.184:443
- **pgAdmin**: http://192.168.171.184:5050
- **PostgreSQL**: 192.168.171.184:5432

---

## 📞 Need Help?

Read full documentation: **docker_live.md**

---

**Keep this cheat sheet handy for daily operations! 🚀**
