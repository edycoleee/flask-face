# PostgreSQL Initialization for Face Recognition with pgvector

## 📋 Overview

SQL script untuk inisialisasi PostgreSQL database dengan pgvector extension untuk face recognition system. Script ini akan otomatis dijalankan saat Docker container pertama kali dibuat.

---

## 📄 init.sql (untuk docker-compose)

Simpan file berikut sebagai `init.sql` di folder yang akan di-mount ke container PostgreSQL:

```sql
-- ================================================
-- FACE RECOGNITION DATABASE INITIALIZATION
-- PostgreSQL + pgvector
-- ================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ================================================
-- TABLE: users
-- ================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk email lookup (sering dipakai untuk login)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ================================================
-- TABLE: photos
-- ================================================
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    width INTEGER DEFAULT 224,
    height INTEGER DEFAULT 224,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index untuk query photos berdasarkan user_id
CREATE INDEX IF NOT EXISTS idx_photos_user_id ON photos(user_id);

-- ================================================
-- TABLE: auth_tokens
-- ================================================
CREATE TABLE IF NOT EXISTS auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index untuk token lookup (primary authentication)
CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_active ON auth_tokens(is_active) WHERE is_active = TRUE;

-- ================================================
-- TABLE: face_embeddings
-- ================================================
-- Menggantikan face_db.npy
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    photo_id INTEGER,  -- Optional: link ke specific photo
    embedding vector(512) NOT NULL,  -- InsightFace menghasilkan 512-D embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE SET NULL
);

-- Index untuk query embeddings berdasarkan user_id
CREATE INDEX IF NOT EXISTS idx_embeddings_user_id ON face_embeddings(user_id);

-- ⚡ CRITICAL: IVFFLAT index untuk fast similarity search
-- lists parameter: sqrt(total_rows) adalah rule of thumb
-- Mulai dengan 100, bisa di-tune setelah data bertambah
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- ================================================
-- FUNCTION: find_similar_face (Face Recognition 1:N)
-- ================================================
-- Mencari wajah paling mirip dari seluruh database
CREATE OR REPLACE FUNCTION find_similar_face(
    query_embedding vector(512), 
    similarity_threshold float DEFAULT 0.7
)
RETURNS TABLE(
    user_id INTEGER,
    user_name VARCHAR,
    user_email VARCHAR,
    similarity float,
    embedding_id INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id as user_id,
        u.name as user_name,
        u.email as user_email,
        1 - (fe.embedding <=> query_embedding) as similarity,
        fe.id as embedding_id
    FROM face_embeddings fe
    JOIN users u ON fe.user_id = u.id
    WHERE 1 - (fe.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY fe.embedding <=> query_embedding  -- Ascending order (smaller distance = more similar)
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- FUNCTION: verify_face (Face Verification 1:1)
-- ================================================
-- Verify apakah embedding cocok dengan specific user
CREATE OR REPLACE FUNCTION verify_face(
    query_embedding vector(512),
    target_user_id INTEGER,
    similarity_threshold float DEFAULT 0.7
)
RETURNS TABLE(
    match BOOLEAN,
    similarity float,
    user_name VARCHAR,
    user_email VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            WHEN MAX(1 - (fe.embedding <=> query_embedding)) >= similarity_threshold 
            THEN TRUE 
            ELSE FALSE 
        END as match,
        COALESCE(MAX(1 - (fe.embedding <=> query_embedding)), 0.0) as similarity,
        MAX(u.name) as user_name,
        MAX(u.email) as user_email
    FROM face_embeddings fe
    JOIN users u ON fe.user_id = u.id
    WHERE fe.user_id = target_user_id
    GROUP BY u.id;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- FUNCTION: get_user_embeddings_count
-- ================================================
-- Helper function untuk cek berapa embeddings yang dimiliki user
CREATE OR REPLACE FUNCTION get_user_embeddings_count(target_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    count INTEGER;
BEGIN
    SELECT COUNT(*) INTO count
    FROM face_embeddings
    WHERE user_id = target_user_id;
    RETURN count;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- TRIGGER: Update updated_at timestamp
-- ================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_face_embeddings_updated_at
BEFORE UPDATE ON face_embeddings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- SAMPLE DATA (Optional - untuk testing)
-- ================================================
-- Uncomment untuk insert sample users
/*
INSERT INTO users (name, email, password) VALUES
    ('Admin User', 'admin@example.com', 'hashed_password_here'),
    ('Test User', 'test@example.com', 'hashed_password_here')
ON CONFLICT (email) DO NOTHING;
*/

-- ================================================
-- VERIFICATION QUERIES
-- ================================================
-- Jalankan queries ini setelah initialization untuk verify
/*
-- Check extensions
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check indexes
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check functions
SELECT routine_name FROM information_schema.routines 
WHERE routine_type = 'FUNCTION' 
AND routine_schema = 'public';
*/
```

---

## 🐳 docker-compose.yml Example

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: flask-face-postgres
    environment:
      POSTGRES_DB: facedb
      POSTGRES_USER: faceuser
      POSTGRES_PASSWORD: facepass123
      POSTGRES_INITDB_ARGS: "-E UTF8"
    ports:
      - "5432:5432"
    volumes:
      # Mount init.sql untuk auto-run saat pertama kali create container
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
      # Persistent storage
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faceuser -d facedb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - face_network

  # Optional: pgAdmin untuk GUI management
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: flask-face-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres
    networks:
      - face_network

volumes:
  postgres_data:

networks:
  face_network:
    driver: bridge
```

---

## 📝 Notes & Best Practices

### 1. **IVFFLAT Index Tuning**
```sql
-- Default: lists = 100 (good for < 100K rows)
-- Untuk dataset lebih besar:
-- - 10K rows  → lists = 100
-- - 100K rows → lists = 316 (sqrt(100000))
-- - 1M rows   → lists = 1000

-- Rebuild index setelah data bertambah banyak:
DROP INDEX idx_embeddings_vector;
CREATE INDEX idx_embeddings_vector 
ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 316);
```

### 2. **Similarity Threshold Guidelines**
```
0.9 - 1.0  : Sangat mirip (kembar identik)
0.8 - 0.9  : Sangat cocok (recommended untuk production)
0.7 - 0.8  : Cocok (good balance)
0.6 - 0.7  : Mungkin cocok (high false positive)
< 0.6      : Berbeda (not recommended)
```

### 3. **Migration dari NPY ke PostgreSQL**

Anda perlu membuat migration script (`migrate_to_postgres.py`):

```python
import numpy as np
import json
import psycopg2
from pathlib import Path

# Load old NPY database
embeddings = np.load('models/face_db.npy')
with open('models/face_db.json', 'r') as f:
    metadata = json.load(f)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="facedb",
    user="faceuser", 
    password="facepass123",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Migrate embeddings
for idx, user_id_str in enumerate(metadata['users']):
    user_id = int(user_id_str)
    embedding = embeddings[idx].tolist()
    
    cur.execute(
        """
        INSERT INTO face_embeddings (user_id, embedding) 
        VALUES (%s, %s)
        """,
        (user_id, embedding)
    )

conn.commit()
cur.close()
conn.close()
```

### 4. **Performance Considerations**

- **Batch Insert**: Gunakan `COPY` atau batch insert untuk migrasi data besar
- **Vacuum**: Jalankan `VACUUM ANALYZE face_embeddings;` setelah bulk insert
- **Connection Pooling**: Gunakan pgbouncer atau SQLAlchemy pool untuk production

### 5. **Backup & Recovery**

```bash
# Backup database
docker exec flask-face-postgres pg_dump -U faceuser facedb > backup.sql

# Restore database
docker exec -i flask-face-postgres psql -U faceuser facedb < backup.sql

# Backup only embeddings
docker exec flask-face-postgres pg_dump -U faceuser -t face_embeddings facedb > embeddings_backup.sql
```

---

## 🚀 Quick Start

1. **Create init.sql** dari script di atas
2. **Create docker-compose.yml** dari example
3. **Run containers**:
   ```bash
   docker-compose up -d
   ```
4. **Verify**:
   ```bash
   docker exec -it flask-face-postgres psql -U faceuser -d facedb
   \dt  -- List tables
   \df  -- List functions
   \q   -- Quit
   ```
5. **Access pgAdmin** (optional): http://localhost:5050

---

## 🔧 Troubleshooting

### pgvector extension not found
```bash
# Make sure using pgvector/pgvector image, not plain postgres
docker-compose down
docker-compose up -d
```

### Init script not running
```bash
# Check if volume already exists (init only runs on first creation)
docker volume ls
docker volume rm <volume_name>
docker-compose up -d
```

### Slow similarity search
```sql
-- Check if index is being used
EXPLAIN ANALYZE 
SELECT * FROM face_embeddings 
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector 
LIMIT 10;

-- Should show "Index Scan using idx_embeddings_vector"
```

---

## ✅ Advantages of PostgreSQL + pgvector

✅ **Scalability**: Handle millions of embeddings  
✅ **ACID Compliance**: Data integrity guaranteed  
✅ **Rich Queries**: JOIN users, photos, embeddings in single query  
✅ **Backup & Replication**: Enterprise-grade reliability  
✅ **Fast Similarity Search**: Optimized vector operations  
✅ **No file corruption**: Unlike NPY files  
✅ **Concurrent Access**: Multiple workers can query simultaneously  

---

Dibuat untuk migrasi dari SQLite + NPY ke PostgreSQL + pgvector 🚀
