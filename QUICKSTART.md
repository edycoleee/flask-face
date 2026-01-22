# Quick Start - PostgreSQL Migration

## 🚀 Langkah-langkah Setup

### 1. Start PostgreSQL dengan Docker Compose

```bash
# Pastikan Docker sudah running
docker --version

# Start PostgreSQL container
cd /home/sultan/flask-face
docker-compose up -d

# Check container status
docker-compose ps

# Lihat logs (pastikan init.sql berhasil dijalankan)
docker-compose logs postgres
```

Output yang diharapkan:
```
✓ PostgreSQL Database cluster initialized
✓ Running init.sql
✓ CREATE EXTENSION vector
✓ CREATE TABLE users
✓ CREATE TABLE photos
✓ CREATE TABLE auth_tokens
✓ CREATE TABLE face_embeddings
```

### 2. Install Dependencies

```bash
# Activate virtual environment (jika ada)
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

Ini akan menginstall:
- `psycopg2-binary` - PostgreSQL driver
- `pgvector` - Vector extension support

### 3. Test Koneksi Database

```bash
# Test koneksi Python ke PostgreSQL
python3 << EOF
from app.utils.db import init_db
init_db()
EOF
```

Output yang diharapkan:
```
✓ PostgreSQL connected: PostgreSQL 16.x...
✓ pgvector extension is installed
✓ Found 4 tables:
  - auth_tokens
  - face_embeddings
  - photos
  - users
```

### 4. Migrate Data (Opsional)

Jika Anda punya data lama di SQLite:

```bash
# Jalankan migration script
python migrate_to_postgres.py
```

Jika belum ada data, skip langkah ini.

### 5. Jalankan Aplikasi

```bash
# Development mode
python run.py

# Atau dengan gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 🧪 Test API

### Test 1: Create User

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

### Test 2: Get All Users

```bash
curl http://localhost:5000/api/users
```

### Test 3: Upload Photo

```bash
# Upload photo untuk user ID 1
curl -X POST http://localhost:5000/api/photos/1/upload \
  -F "file=@/path/to/photo.jpg"
```

### Test 4: Build Face Database

```bash
curl -X POST http://localhost:5000/api/training/start \
  -H "Content-Type: application/json"
```

### Test 5: Face Recognition

```bash
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@/path/to/test-photo.jpg"
```

## 🔍 Verify Database

### Via psql (Command Line)

```bash
# Connect ke PostgreSQL
docker exec -it flask-face-postgres psql -U sultan -d face_db

# Di dalam psql:
\dt                    # List tables
\d users               # Show users table structure
\d face_embeddings     # Show embeddings table structure

SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM photos;
SELECT COUNT(*) FROM face_embeddings;

\q  # Exit
```

### Via pgAdmin (Web GUI)

1. Open: http://192.168.171.184:5050
2. Login: `admin@admin.com` / `admin`
3. Add Server:
   - Name: `Flask Face DB`
   - Host: `postgres` (atau `192.168.171.184` jika dari luar Docker)
   - Port: `5432`
   - Username: `sultan`
   - Password: `Sulfat123#!`
   - Database: `face_db`

## 🛑 Troubleshooting

### Error: Connection refused

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# View logs
docker-compose logs -f postgres
```

### Error: psycopg2 not installed

```bash
pip install psycopg2-binary
```

### Error: pgvector extension not found

```bash
# Recreate database (will re-run init.sql)
docker-compose down
docker volume rm flask-face_postgres_data
docker-compose up -d
```

### Error: Tables not found

```bash
# Check if init.sql was executed
docker exec -it flask-face-postgres psql -U sultan -d face_db -c "\dt"

# If no tables, manually run init.sql
docker exec -i flask-face-postgres psql -U sultan -d face_db < init.sql
```

## 📝 Common Commands

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart postgres

# Execute SQL command
docker exec -it flask-face-postgres psql -U sultan -d face_db -c "SELECT COUNT(*) FROM users;"

# Backup database
docker exec flask-face-postgres pg_dump -U sultan face_db > backup.sql

# Restore database
docker exec -i flask-face-postgres psql -U sultan face_db < backup.sql
```

## ✅ Verification Checklist

- [ ] Docker containers running (`docker-compose ps`)
- [ ] PostgreSQL accessible (`psql` connection works)
- [ ] pgvector extension installed
- [ ] All 4 tables created
- [ ] Python can connect (`init_db()` works)
- [ ] API endpoints responding
- [ ] Can create users
- [ ] Can upload photos
- [ ] Can train model (build embeddings)
- [ ] Face recognition works

## 🎯 Next Steps

1. **Create test users** via API
2. **Upload training photos** for each user (minimal 5 photos per user)
3. **Build embeddings** dengan `POST /api/training/start`
4. **Test face recognition** dengan `POST /api/face/predict`
5. **Test face login** dengan `POST /api/auth/login-face`

---

**Status:** 🟢 Ready to use  
**Database:** PostgreSQL 16 + pgvector  
**Host:** 192.168.171.184:5432  
**Web UI:** http://192.168.171.184:5050 (pgAdmin)
