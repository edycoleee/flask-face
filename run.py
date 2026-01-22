from flask import Flask, render_template, send_file
from flask_restx import Api
from app.api.halo import api as halo_ns
from app.api.users import api as users_ns
from app.api.photos import api as photos_ns
from app.api.training import training_ns
from app.api.prediction import api as prediction_ns
from app.api.auth import api as auth_ns
from app.utils.db import init_db
import os
import warnings
import logging

# Suppress all warnings untuk Raspberry Pi (cleaner output)
warnings.filterwarnings('ignore')

# Suppress ONNX Runtime warnings
os.environ['ORT_LOGGING_LEVEL'] = '3'

# Suppress TensorFlow/ONNX verbose logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

# Set logging untuk library external
logging.getLogger('onnxruntime').setLevel(logging.ERROR)
logging.getLogger('insightface').setLevel(logging.ERROR)

def create_app():
    app = Flask(__name__)
    
    # Setup API Swagger
    api = Api(app, version="1.0", title="Flask Gateway API", doc='/api/docs', prefix='/api')
    api.add_namespace(halo_ns, path="/halo")
    api.add_namespace(users_ns, path="/users")
    api.add_namespace(photos_ns, path="/photos")
    api.add_namespace(training_ns, path="/training")
    api.add_namespace(prediction_ns, path="/face")
    api.add_namespace(auth_ns, path="/auth")

    # Inisialisasi Database SQLite (Native SQL)
    init_db()

    return app

app = create_app()

LOG_FILE = os.path.join("instance", "app.log")

@app.route("/")
def index():
    """Serve the main UI page"""
    return render_template("page.html")

@app.route("/api/logs")
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return "".join(lines[-30:])
    return "No logs."

@app.route("/api/photos/<int:user_id>/<int:photo_id>/view")
def view_photo(user_id, photo_id):
    """View photo by ID"""
    from app.utils.db import get_db_connection
    
    conn = get_db_connection()
    photo = conn.execute(
        "SELECT filepath FROM photos WHERE id = ? AND user_id = ?",
        (photo_id, user_id)
    ).fetchone()
    conn.close()
    
    if not photo:
        return {"message": "Photo not found"}, 404
    
    filepath = dict(photo)["filepath"]
    if not os.path.exists(filepath):
        return {"message": "Photo file not found"}, 404
    
    return send_file(filepath, mimetype='image/png')

if __name__ == "__main__":
    # Check if SSL certificates exist for HTTPS
    cert_file = 'certs/cert.pem'
    key_file = 'certs/key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        # HTTPS mode (production)
        print("=" * 60)
        print("🔒 HTTPS MODE ENABLED")
        print("=" * 60)
        print(f"Certificate: {cert_file}")
        print(f"Key: {key_file}")
        print("Server running on https://0.0.0.0:443")
        print("=" * 60)
        
        app.run(
            host='0.0.0.0',
            port=443,
            ssl_context=(cert_file, key_file),
            debug=False
        )
    else:
        # HTTP mode (development)
        print("=" * 60)
        print("⚠️  HTTP MODE (Development)")
        print("=" * 60)
        print("SSL certificates not found.")
        print("Server running on http://0.0.0.0:5000")
        print("For HTTPS: Generate certificates in certs/ folder")
        print("=" * 60)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )