import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from app.utils.db import get_db_connection
from app.utils.logger import logger

DATASET_DIR = "dataset"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
RESIZE_WIDTH = 224
RESIZE_HEIGHT = 224

class PhotoService:

    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def resize_image(file_path, width=RESIZE_WIDTH, height=RESIZE_HEIGHT):
        """Resize image to specified dimensions"""
        try:
            img = Image.open(file_path)
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                img = rgb_img
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            # Pad to exact size
            final_img = Image.new('RGB', (width, height), (255, 255, 255))
            offset = ((width - img.width) // 2, (height - img.height) // 2)
            final_img.paste(img, offset)
            final_img.save(file_path, 'PNG')
            return True
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return False

    @staticmethod
    def upload_photo(user_id, file, width=RESIZE_WIDTH, height=RESIZE_HEIGHT):
        """Upload single photo"""
        try:
            # Validate file
            if not file or file.filename == '':
                return None, "File tidak ditemukan"
            
            if not PhotoService.allowed_file(file.filename):
                return None, "Format file hanya boleh JPG/PNG"
            
            if len(file.read()) > MAX_FILE_SIZE:
                file.seek(0)
                return None, f"Ukuran file tidak boleh lebih dari {MAX_FILE_SIZE // (1024*1024)}MB"
            
            file.seek(0)
            
            # Create user folder if not exists
            user_folder = os.path.join(DATASET_DIR, str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            
            # Save file with timestamp
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = timestamp + filename
            filepath = os.path.join(user_folder, filename)
            
            # Save original file
            file.save(filepath)
            
            # Resize image
            if not PhotoService.resize_image(filepath, width, height):
                os.remove(filepath)
                return None, "Gagal mengubah ukuran gambar"
            
            # Save metadata to database
            conn = get_db_connection()
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO photos (user_id, filename, filepath, width, height, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, filename, filepath, width, height, created_at))
            
            photo_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Photo uploaded: ID={photo_id}, User={user_id}, File={filename}")
            
            return {
                "id": photo_id,
                "user_id": user_id,
                "filename": filename,
                "filepath": filepath,
                "width": width,
                "height": height,
                "created_at": created_at
            }, None
            
        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}")
            return None, f"Error: {str(e)}"

    @staticmethod
    def upload_multiple_photos(user_id, files, width=RESIZE_WIDTH, height=RESIZE_HEIGHT):
        """Upload multiple photos"""
        results = []
        errors = []
        
        if not files:
            return None, "Tidak ada file yang dipilih"
        
        for file in files:
            if file and file.filename != '':
                photo, error = PhotoService.upload_photo(user_id, file, width, height)
                if error:
                    errors.append({"filename": file.filename, "error": error})
                else:
                    results.append(photo)
        
        if not results and errors:
            return None, f"Semua file gagal diunggah: {errors}"
        
        response = {
            "files": results,
            "total": len(results),
            "errors": errors if errors else None
        }
        
        logger.info(f"Multiple photos uploaded: User={user_id}, Success={len(results)}, Failed={len(errors)}")
        return response, None

    @staticmethod
    def get_user_photos(user_id):
        """Get all photos for a user"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT * FROM photos WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user photos: {str(e)}")
            return None

    @staticmethod
    def delete_photo(photo_id, user_id):
        """Delete a photo by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get photo info first
            photo = cursor.execute(
                "SELECT * FROM photos WHERE id = ? AND user_id = ?",
                (photo_id, user_id)
            ).fetchone()
            
            if not photo:
                conn.close()
                return False, "Foto tidak ditemukan"
            
            # Delete from database
            cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
            conn.commit()
            conn.close()
            
            # Delete file
            filepath = dict(photo)["filepath"]
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Photo deleted: ID={photo_id}, File={filepath}")
            
            return True, None
        except Exception as e:
            logger.error(f"Error deleting photo: {str(e)}")
            return False, str(e)
