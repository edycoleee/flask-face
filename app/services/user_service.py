import os
import shutil
import sqlite3
from app.utils.db import get_db_connection
from app.utils.logger import logger

DATASET_DIR = "dataset"

class UserService:

    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        rows = conn.execute("SELECT id, name, email, password FROM users").fetchall()
        conn.close()
        # Mengembalikan list of dict agar sesuai dengan marshal_with di API
        return [dict(row) for row in rows]

    @staticmethod
    def get_user(user_id):
        conn = get_db_connection()
        row = conn.execute("SELECT id, name, email, password FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create_user(name, email, password):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            user_id = cursor.lastrowid
            conn.commit()

            # Buat folder otomatis berdasarkan ID baru
            folder_path = os.path.join(DATASET_DIR, str(user_id))
            os.makedirs(folder_path, exist_ok=True)
            
            logger.info(f"User created: {user_id} - folder created at {folder_path}")
            return {"id": user_id, "name": name, "email": email, "password": password}, None
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity Error: {str(e)}")
            return None, "Email sudah terdaftar!"
        finally:
            conn.close()

    @staticmethod
    def update_user(user_id, name, email, password):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?",
                (name, email, password, user_id)
            )
            if cursor.rowcount == 0:
                return None, "User tidak ditemukan"
            
            conn.commit()
            logger.info(f"User updated: {user_id}")
            return {"id": user_id, "name": name, "email": email, "password": password}, None
        except sqlite3.IntegrityError:
            return None, "Email baru sudah digunakan oleh user lain!"
        finally:
            conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cek apakah user ada sebelum dihapus
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.close()
            return False

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        # Hapus folder secara rekursif
        folder_path = os.path.join(DATASET_DIR, str(user_id))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        logger.info(f"User deleted: {user_id} - folder removed {folder_path}")
        return True