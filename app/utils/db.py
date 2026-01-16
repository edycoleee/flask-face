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
    conn.commit()
    conn.close()