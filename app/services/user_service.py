import os
import shutil
from app.utils.db import get_db_connection, get_db_cursor
from app.utils.logger import logger

DATASET_DIR = "dataset"

class UserService:

    @staticmethod
    def get_all_users():
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT id, name, email, password FROM users")
            rows = cursor.fetchall()
            # RealDictCursor already returns dict-like objects
            return rows

    @staticmethod
    def get_user(user_id):
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            cursor.execute("SELECT id, name, email, password FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create_user(name, email, password):
        with get_db_connection() as conn:
            try:
                cursor = get_db_cursor(conn)
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
                    (name, email, password)
                )
                user_id = cursor.fetchone()['id']
                conn.commit()

                # Buat folder otomatis berdasarkan ID baru
                folder_path = os.path.join(DATASET_DIR, str(user_id))
                os.makedirs(folder_path, exist_ok=True)
                
                logger.info(f"User created: {user_id} - folder created at {folder_path}")
                return {"id": user_id, "name": name, "email": email, "password": password}, None
            except Exception as e:
                conn.rollback()
                # Check for unique constraint violation (PostgreSQL error code 23505)
                if 'unique constraint' in str(e).lower() or '23505' in str(e):
                    logger.error(f"Integrity Error: {str(e)}")
                    return None, "Email sudah terdaftar!"
                logger.error(f"Database Error: {str(e)}")
                return None, f"Error: {str(e)}"

    @staticmethod
    def update_user(user_id, name, email, password):
        with get_db_connection() as conn:
            try:
                cursor = get_db_cursor(conn)
                cursor.execute(
                    "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
                    (name, email, password, user_id)
                )
                if cursor.rowcount == 0:
                    return None, "User tidak ditemukan"
                
                conn.commit()
                logger.info(f"User updated: {user_id}")
                return {"id": user_id, "name": name, "email": email, "password": password}, None
            except Exception as e:
                conn.rollback()
                if 'unique constraint' in str(e).lower() or '23505' in str(e):
                    return None, "Email baru sudah digunakan oleh user lain!"
                return None, f"Error: {str(e)}"

    @staticmethod
    def delete_user(user_id):
        with get_db_connection() as conn:
            cursor = get_db_cursor(conn)
            
            # Cek apakah user ada sebelum dihapus
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return False

            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()

        # Hapus folder secara rekursif
        folder_path = os.path.join(DATASET_DIR, str(user_id))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        logger.info(f"User deleted: {user_id} - folder removed {folder_path}")
        return True