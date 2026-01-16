from flask import Flask
from flask_restx import Api
from app.api.halo import api as halo_ns
from app.api.users import api as users_ns
from app.utils.db import init_db
import os

def create_app():
    app = Flask(__name__)
    
    # Setup API Swagger
    api = Api(app, version="1.0", title="Flask Gateway API", doc='/api/docs', prefix='/api')
    api.add_namespace(halo_ns, path="/halo")
    api.add_namespace(users_ns, path="/users")

    # Inisialisasi Database SQLite (Native SQL)
    init_db()

    return app

app = create_app()

LOG_FILE = os.path.join("instance", "app.log")

@app.route("/api/logs")
def get_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            return "".join(lines[-30:])
    return "No logs."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)