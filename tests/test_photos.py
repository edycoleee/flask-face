import os
import pytest
import shutil
from io import BytesIO
from PIL import Image
from run import create_app
from app.utils.db import init_db


# Fixture untuk menyediakan client test dan setup environment
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    # Inisialisasi DB sebelum test
    init_db()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup: Hapus folder dataset setelah semua test selesai
    if os.path.exists("dataset"):
        shutil.rmtree("dataset")


@pytest.fixture
def test_user_counter():
    """Counter untuk membuat unique email"""
    return {"count": 0}


def create_test_user(test_user_counter):
    """Helper untuk membuat unique test user"""
    from app.services.user_service import UserService
    test_user_counter["count"] += 1
    timestamp = int(__import__('time').time() * 1000000)  # Unique timestamp
    email = f"test_user_{timestamp}_{test_user_counter['count']}@example.com"
    user, _ = UserService.create_user(f"Test User {timestamp}", email)
    return user


@pytest.fixture
def test_image_jpg():
    """Fixture untuk membuat test JPG image"""
    img = Image.new('RGB', (500, 500), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def test_image_png():
    """Fixture untuk membuat test PNG image"""
    img = Image.new('RGB', (500, 500), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestPhotoUpload:
    """Test suite untuk endpoint /api/photos/<user_id>/upload"""
    
    def test_upload_single_photo_success(self, client, test_user_counter, test_image_jpg):
        """Test upload single photo JPG"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test_photo.jpg")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        data = res.get_json()
        
        assert data["id"] is not None
        assert data["user_id"] == user_id
        assert data["filename"] is not None
        assert "test_photo" in data["filename"]
        assert data["filepath"] is not None
        assert data["width"] == 224
        assert data["height"] == 224
        assert data["created_at"] is not None
        
        # Verify file exists
        assert os.path.exists(data["filepath"])
    
    def test_upload_single_photo_png(self, client, test_user_counter, test_image_png):
        """Test upload single photo PNG"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_png, "test_photo.png")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        data = res.get_json()
        
        assert data["width"] == 224
        assert data["height"] == 224
        assert os.path.exists(data["filepath"])
    
    def test_upload_no_file(self, client, test_user_counter):
        """Test upload tanpa file"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        res = client.post(f"/api/photos/{user_id}/upload")
        
        assert res.status_code == 400
        assert "tidak ditemukan" in res.get_json()["message"]
    
    def test_upload_invalid_format(self, client, test_user_counter):
        """Test upload dengan format file invalid"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Create invalid file (text file)
        invalid_file = BytesIO(b"This is not an image")
        
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (invalid_file, "test.txt")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 400
        assert "JPG/PNG" in res.get_json()["message"]
    
    def test_upload_user_not_found(self, client, test_image_jpg):
        """Test upload untuk user yang tidak ada"""
        user_id = 99999
        
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test.jpg")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]
    
    def test_upload_creates_folder(self, client, test_user_counter, test_image_jpg):
        """Test bahwa upload membuat folder user jika belum ada"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        user_folder = os.path.join("dataset", str(user_id))
        
        # Folder sudah ada dari user creation, tapi test pastikan ada
        assert os.path.exists(user_folder)
        
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test.jpg")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        assert os.path.exists(user_folder)


class TestPhotoUploadMultiple:
    """Test suite untuk endpoint /api/photos/<user_id>/upload/multiple"""
    
    def test_upload_multiple_success(self, client, test_user_counter, test_image_jpg, test_image_png):
        """Test upload multiple photos"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Reset BytesIO pointers
        test_image_jpg.seek(0)
        test_image_png.seek(0)
        
        res = client.post(
            f"/api/photos/{user_id}/upload/multiple",
            data={
                "files[]": [
                    (test_image_jpg, "photo1.jpg"),
                    (test_image_png, "photo2.png")
                ]
            },
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        data = res.get_json()
        
        assert "files" in data
        assert data["total"] == 2
        assert len(data["files"]) == 2
        assert data["errors"] is None
        
        # Verify all files
        for photo in data["files"]:
            assert photo["id"] is not None
            assert photo["user_id"] == user_id
            assert photo["width"] == 224
            assert photo["height"] == 224
            assert os.path.exists(photo["filepath"])
    
    def test_upload_multiple_no_files(self, client, test_user_counter):
        """Test upload multiple tanpa files"""
        test_user = create_test_user(test_user_counter)
        if test_user is None:
            pytest.skip("Failed to create test user")
        user_id = test_user["id"]
        
        res = client.post(f"/api/photos/{user_id}/upload/multiple")
        
        assert res.status_code == 400
        assert "tidak ditemukan" in res.get_json()["message"]
    
    def test_upload_multiple_partial_invalid(self, client, test_user_counter, test_image_jpg):
        """Test upload multiple dengan beberapa file invalid"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        test_image_jpg.seek(0)
        invalid_file = BytesIO(b"invalid")
        
        res = client.post(
            f"/api/photos/{user_id}/upload/multiple",
            data={
                "files[]": [
                    (test_image_jpg, "valid.jpg"),
                    (invalid_file, "invalid.txt")
                ]
            },
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        data = res.get_json()
        
        # Should have 1 valid file
        assert data["total"] == 1
        assert len(data["files"]) == 1
        # Should have 1 error
        assert data["errors"] is not None
        assert len(data["errors"]) == 1
    
    def test_upload_multiple_user_not_found(self, client, test_image_jpg):
        """Test upload multiple untuk user tidak ada"""
        test_image_jpg.seek(0)
        
        res = client.post(
            f"/api/photos/99999/upload/multiple",
            data={
                "files[]": [(test_image_jpg, "photo.jpg")]
            },
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]


class TestGetUserPhotos:
    """Test suite untuk endpoint /api/photos/<user_id> GET"""
    
    def test_get_user_photos_empty(self, client, test_user_counter):
        """Test get photos untuk user tanpa foto"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        res = client.get(f"/api/photos/{user_id}")
        
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_user_photos_success(self, client, test_user_counter, test_image_jpg, test_image_png):
        """Test get photos untuk user dengan foto"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Upload 2 photos
        test_image_jpg.seek(0)
        test_image_png.seek(0)
        
        client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "photo1.jpg")},
            content_type='multipart/form-data'
        )
        
        test_image_png.seek(0)
        client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_png, "photo2.png")},
            content_type='multipart/form-data'
        )
        
        # Get photos
        res = client.get(f"/api/photos/{user_id}")
        
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify first photo (most recent first)
        assert data[0]["id"] is not None
        assert data[0]["user_id"] == user_id
        assert data[0]["filename"] is not None
        assert data[0]["width"] == 224
        assert data[0]["height"] == 224
    
    def test_get_user_photos_not_found(self, client):
        """Test get photos untuk user tidak ada"""
        res = client.get("/api/photos/99999")
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]


class TestDeletePhoto:
    """Test suite untuk endpoint /api/photos/<user_id>/<photo_id> DELETE"""
    
    def test_delete_photo_success(self, client, test_user_counter, test_image_jpg):
        """Test delete photo"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Upload photo
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test.jpg")},
            content_type='multipart/form-data'
        )
        
        photo_id = res.get_json()["id"]
        filepath = res.get_json()["filepath"]
        
        # Verify file exists
        assert os.path.exists(filepath)
        
        # Delete photo
        res = client.delete(f"/api/photos/{user_id}/{photo_id}")
        
        assert res.status_code == 200
        assert "berhasil dihapus" in res.get_json()["message"]
        
        # Verify file deleted
        assert not os.path.exists(filepath)
    
    def test_delete_photo_not_found(self, client, test_user_counter):
        """Test delete photo yang tidak ada"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        photo_id = 99999
        
        res = client.delete(f"/api/photos/{user_id}/{photo_id}")
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]
    
    def test_delete_photo_wrong_user(self, client, test_user_counter, test_image_jpg):
        """Test delete photo milik user lain"""
        import time
        from app.services.user_service import UserService
        
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Create another user with unique email
        timestamp = int(time.time() * 1000000)
        other_user, _ = UserService.create_user(f"Other User {timestamp}", f"other_delete_{timestamp}@example.com")
        other_user_id = other_user["id"]
        
        # Upload photo to first user
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test.jpg")},
            content_type='multipart/form-data'
        )
        
        photo_id = res.get_json()["id"]
        
        # Try to delete from other user
        res = client.delete(f"/api/photos/{other_user_id}/{photo_id}")
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]
    
    def test_delete_photo_user_not_found(self, client):
        """Test delete photo untuk user tidak ada"""
        res = client.delete("/api/photos/99999/1")
        
        assert res.status_code == 404
        assert "tidak ditemukan" in res.get_json()["message"]


class TestPhotoIntegration:
    """Integration tests untuk Photo API"""
    
    def test_upload_get_delete_workflow(self, client, test_user_counter, test_image_jpg):
        """Test complete workflow: upload -> get -> delete"""
        test_user = create_test_user(test_user_counter)
        user_id = test_user["id"]
        
        # Step 1: Upload photo
        res = client.post(
            f"/api/photos/{user_id}/upload",
            data={"file": (test_image_jpg, "test.jpg")},
            content_type='multipart/form-data'
        )
        
        assert res.status_code == 201
        photo = res.get_json()
        photo_id = photo["id"]
        
        # Step 2: Get photos
        res = client.get(f"/api/photos/{user_id}")
        
        assert res.status_code == 200
        photos = res.get_json()
        assert len(photos) == 1
        assert photos[0]["id"] == photo_id
        
        # Step 3: Delete photo
        res = client.delete(f"/api/photos/{user_id}/{photo_id}")
        
        assert res.status_code == 200
        
        # Step 4: Verify deleted
        res = client.get(f"/api/photos/{user_id}")
        
        assert res.status_code == 200
        photos = res.get_json()
        assert len(photos) == 0
    
    def test_multiple_users_photos(self, client, test_user_counter, test_image_jpg, test_image_png):
        """Test photos dari multiple users tidak tercampur"""
        import time
        from app.services.user_service import UserService
        
        # Create two users with unique emails
        timestamp = int(time.time() * 1000000)
        user1, _ = UserService.create_user(f"User 1 Multi {timestamp}", f"user1_multi_{timestamp}@example.com")
        user2, _ = UserService.create_user(f"User 2 Multi {timestamp}", f"user2_multi_{timestamp}@example.com")
        
        user1_id = user1["id"]
        user2_id = user2["id"]
        
        # Upload photos to user 1
        test_image_jpg.seek(0)
        client.post(
            f"/api/photos/{user1_id}/upload",
            data={"file": (test_image_jpg, "user1_photo.jpg")},
            content_type='multipart/form-data'
        )
        
        # Upload photos to user 2
        test_image_png.seek(0)
        client.post(
            f"/api/photos/{user2_id}/upload",
            data={"file": (test_image_png, "user2_photo.png")},
            content_type='multipart/form-data'
        )
        
        # Verify user 1 photos
        res = client.get(f"/api/photos/{user1_id}")
        user1_photos = res.get_json()
        assert len(user1_photos) == 1
        assert user1_photos[0]["user_id"] == user1_id
        
        # Verify user 2 photos
        res = client.get(f"/api/photos/{user2_id}")
        user2_photos = res.get_json()
        assert len(user2_photos) == 1
        assert user2_photos[0]["user_id"] == user2_id
