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
    app.run(host='0.0.0.0', port=5000, debug=True)