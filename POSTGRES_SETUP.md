# PostgreSQL Migration Guide

## 🚀 Quick Start

Implementasi PostgreSQL dengan pgvector untuk Face Recognition system.

## 📋 Konfigurasi Database

```
Host: 192.168.171.184
Database: face_db
User: sultan
Password: Sulfat123#!
Port: 5432
```

## 🔧 Setup Instructions

### 1. Start PostgreSQL with Docker Compose

```bash
# Start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 2. Verify Database Initialization

```bash
# Connect to PostgreSQL
docker exec -it flask-face-postgres psql -U sultan -d face_db

# In psql prompt:
\dt              # List tables
\df              # List functions  
\di              # List indexes
SELECT * FROM pg_extension WHERE extname = 'vector';  # Check pgvector
\q               # Quit
```

Expected output:
- Tables: `users`, `photos`, `auth_tokens`, `face_embeddings`
- Functions: `find_similar_face`, `verify_face`, `get_user_embeddings_count`
- Extension: `vector`

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `psycopg2-binary` - PostgreSQL adapter
- `pgvector` - Vector extension support

### 4. Migrate Data (Optional)

If you have existing SQLite data:

```bash
python migrate_to_postgres.py
```

This will migrate:
- ✓ Users from `instance/app.db`
- ✓ Photos metadata
- ✓ Face embeddings from `models/face_db.npy`

### 5. Test Database Connection

```bash
python -c "from app.utils.db import init_db; init_db()"
```

Expected output:
```
✓ PostgreSQL connected: PostgreSQL 16...
✓ pgvector extension is installed
✓ Found 4 tables:
  - auth_tokens
  - face_embeddings
  - photos
  - users
```

### 6. Start Flask Application

```bash
python run.py
```

Or with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 🔍 Verification Checklist

- [ ] PostgreSQL container is running
- [ ] pgvector extension is installed
- [ ] All 4 tables are created
- [ ] All 3 functions are created
- [ ] IVFFLAT index on embeddings exists
- [ ] Python can connect to PostgreSQL
- [ ] Data migrated successfully (if applicable)
- [ ] Flask app starts without errors
- [ ] Test API endpoints work

## 🧪 Test API Endpoints

### Test User Creation
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123"
  }'
```

### Test Get All Users
```bash
curl http://localhost:5000/api/users
```

### Test Face Recognition (after training)
```bash
curl -X POST http://localhost:5000/api/face/predict \
  -F "file=@/path/to/photo.jpg"
```

## 📊 Database Management

### Access pgAdmin (Optional)

1. Open browser: http://192.168.171.184:5050
2. Login: admin@admin.com / admin
3. Add server:
   - Name: Flask Face DB
   - Host: postgres (container name)
   - Port: 5432
   - Username: sultan
   - Password: Sulfat123#!

### Backup Database

```bash
# Full backup
docker exec flask-face-postgres pg_dump -U sultan face_db > backup.sql

# Backup only embeddings
docker exec flask-face-postgres pg_dump -U sultan -t face_embeddings face_db > embeddings.sql

# Backup with compression
docker exec flask-face-postgres pg_dump -U sultan face_db | gzip > backup.sql.gz
```

### Restore Database

```bash
# Restore from backup
docker exec -i flask-face-postgres psql -U sultan face_db < backup.sql

# Restore from compressed
gunzip -c backup.sql.gz | docker exec -i flask-face-postgres psql -U sultan face_db
```

### Monitor Database

```bash
# Check table sizes
docker exec flask-face-postgres psql -U sultan -d face_db -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Check number of embeddings
docker exec flask-face-postgres psql -U sultan -d face_db -c "
SELECT 
    user_id,
    COUNT(*) as embedding_count
FROM face_embeddings
GROUP BY user_id;
"
```

## 🐛 Troubleshooting

### Connection Refused
```bash
# Check if container is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs flask-face-postgres

# Restart container
docker-compose restart postgres
```

### pgvector Not Found
```bash
# Check extension
docker exec flask-face-postgres psql -U sultan -d face_db -c "SELECT * FROM pg_extension;"

# Recreate container (will re-run init.sql)
docker-compose down
docker volume rm flask-face_postgres_data
docker-compose up -d
```

### Slow Similarity Search
```sql
-- Check if index is being used
EXPLAIN ANALYZE 
SELECT * FROM face_embeddings 
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector 
LIMIT 10;

-- Rebuild index with more lists (after many embeddings added)
DROP INDEX idx_embeddings_vector;
CREATE INDEX idx_embeddings_vector 
ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 316);
```

### Migration Issues
```bash
# Check SQLite database
sqlite3 instance/app.db ".tables"
sqlite3 instance/app.db "SELECT COUNT(*) FROM users;"

# Check PostgreSQL
docker exec flask-face-postgres psql -U sultan -d face_db -c "SELECT COUNT(*) FROM users;"

# Re-run migration (skips existing data)
python migrate_to_postgres.py
```

## 🔐 Security Recommendations

### Production Setup

1. **Change Default Password**
   ```bash
   # In docker-compose.yml
   POSTGRES_PASSWORD: <strong-random-password>
   ```

2. **Use Environment Variables**
   ```bash
   # Create .env file
   POSTGRES_DB=face_db
   POSTGRES_USER=sultan
   POSTGRES_PASSWORD=<your-password>
   POSTGRES_HOST=192.168.171.184
   POSTGRES_PORT=5432
   ```

3. **Enable SSL/TLS**
   - Configure PostgreSQL to use SSL certificates
   - Update connection string to use `sslmode=require`

4. **Firewall Rules**
   ```bash
   # Only allow specific IPs
   sudo ufw allow from <your-app-server-ip> to any port 5432
   ```

5. **Regular Backups**
   ```bash
   # Add to crontab
   0 2 * * * docker exec flask-face-postgres pg_dump -U sultan face_db > /backup/face_db_$(date +\%Y\%m\%d).sql
   ```

## 📈 Performance Tuning

### PostgreSQL Configuration

Edit `docker-compose.yml` to add environment variables:

```yaml
environment:
  # ... existing vars ...
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
  POSTGRES_MAINTENANCE_WORK_MEM: 128MB
  POSTGRES_CHECKPOINT_COMPLETION_TARGET: 0.9
  POSTGRES_WAL_BUFFERS: 16MB
  POSTGRES_DEFAULT_STATISTICS_TARGET: 100
  POSTGRES_RANDOM_PAGE_COST: 1.1
  POSTGRES_EFFECTIVE_IO_CONCURRENCY: 200
  POSTGRES_WORK_MEM: 4MB
  POSTGRES_MIN_WAL_SIZE: 1GB
  POSTGRES_MAX_WAL_SIZE: 4GB
```

### Connection Pooling

For production, use pgbouncer or SQLAlchemy connection pool:

```python
# In app/utils/db.py
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    1,  # minconn
    20,  # maxconn
    **DB_CONFIG
)

def get_db_connection():
    return connection_pool.getconn()
```

## 🎯 Next Steps

1. ✅ Test all API endpoints
2. ✅ Upload photos for users
3. ✅ Run training to build embeddings: `POST /api/training/start`
4. ✅ Test face recognition: `POST /api/face/predict`
5. ✅ Test face login: `POST /api/auth/login-face`
6. ✅ Monitor database performance
7. ✅ Setup automated backups
8. ✅ Configure production environment

---

**Database Status:** 🟢 Ready  
**Migration Tool:** ✅ Available  
**Backup Strategy:** 📋 Documented  
**Production Ready:** 🚀 Yes (after password change)
