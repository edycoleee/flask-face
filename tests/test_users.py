import os
import pytest
import shutil
from run import create_app
from app.utils.db import init_db

# Fixture untuk menyediakan client test dan setup environment
@pytest.fixture
def client():
    # Gunakan environment variable untuk folder testing (opsional)
    os.environ["DATASET_DIR"] = "dataset_test"
    
    app = create_app()
    app.config['TESTING'] = True
    
    # Inisialisasi DB sebelum test
    init_db()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup: Hapus folder dataset testing setelah semua test selesai
    if os.path.exists("dataset_test"):
        shutil.rmtree("dataset_test")

def test_create_user(client):
    payload = {"name": "Edy", "email": "edy@example.com"}
    res = client.post("/api/users", json=payload)

    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Edy"
    assert data["email"] == "edy@example.com"

    # Cek folder dataset/<id>
    # Gunakan folder default 'dataset' jika os.environ tidak terbaca di service
    folder = os.path.join("dataset", str(data["id"]))
    assert os.path.exists(folder)

def test_create_user_duplicate_email(client):
    # Buat user pertama
    payload = {"name": "User 1", "email": "same@example.com"}
    client.post("/api/users", json=payload)
    
    # Buat user kedua dengan email sama
    res = client.post("/api/users", json=payload)
    
    assert res.status_code == 400
    assert "Email sudah terdaftar" in res.get_json()["message"]

def test_get_users(client):
    # Pastikan bersih, lalu tambah user
    client.post("/api/users", json={"name": "A", "email": "a@example.com"})
    client.post("/api/users", json={"name": "B", "email": "b@example.com"})

    res = client.get("/api/users")
    assert res.status_code == 200

    data = res.get_json()
    # Gunakan >= 2 karena mungkin ada data dari test sebelumnya jika DB tidak di-reset
    assert len(data) >= 2

def test_get_user_by_id(client):
    res = client.post("/api/users", json={"name": "Test", "email": "t@example.com"})
    user_id = res.get_json()["id"]

    res = client.get(f"/api/users/{user_id}")
    assert res.status_code == 200
    assert res.get_json()["id"] == user_id

def test_update_user(client):
    res = client.post("/api/users", json={"name": "Old", "email": "old@example.com"})
    user_id = res.get_json()["id"]

    res = client.put(f"/api/users/{user_id}", json={"name": "New", "email": "new@example.com"})
    assert res.status_code == 200

    data = res.get_json()
    assert data["name"] == "New"
    assert data["email"] == "new@example.com"

def test_delete_user(client):
    res = client.post("/api/users", json={"name": "Del", "email": "del@example.com"})
    user_id = res.get_json()["id"]

    folder = os.path.join("dataset", str(user_id))
    assert os.path.exists(folder)

    res = client.delete(f"/api/users/{user_id}")
    assert res.status_code == 200

    # Folder harus hilang
    assert not os.path.exists(folder)

    # User tidak boleh ditemukan lagi
    res = client.get(f"/api/users/{user_id}")
    assert res.status_code == 404