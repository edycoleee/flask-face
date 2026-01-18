#//app/utils/db.py
import sqlite3
import os

DB_PATH = os.path.join("instance", "app.db")

def get_db_connection():
    # check_same_thread=False diperlukan agar SQLite bisa diakses Flask
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Hasil query jadi objek mirip dict
    return conn

def init_db():
    if not os.path.exists("instance"):
        os.makedirs("instance")
        
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            width INTEGER DEFAULT 224,
            height INTEGER DEFAULT 224,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()