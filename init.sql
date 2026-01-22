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
