import os
from flask import Flask, send_from_directory
from extensions import db, migrate, jwt, cors
from dotenv import load_dotenv
from config import DevConfig
from src.models import DPResult
from src.auth.routes import auth_bp
from src.rbac.routes import rbac_bp
from src.audit.logger import init_audit
from src.audit.routes import audit_bp
from src.api.routes import api_bp
from src.dp.routes import dp_bp 


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    cors.init_app(app, resources={
        r"/api/*": {"origins": "*"},
        r"/*": {"origins": "*"}  # Allow CORS for all routes
    })
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(rbac_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dp_bp, url_prefix="/dp")
    

    # Auditing after_request hook & file logging
    init_audit(app)

    # Optional API info endpoint
    @app.get("/api/info")
    def index():
        return {"name": "SecurePy", "features": ["auth", "rbac", "audit", "dp"]}

    # Serve React frontend
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        dist_path = os.path.join(os.path.dirname(__file__), "dist")
        if path != "" and os.path.exists(os.path.join(dist_path, path)):
            return send_from_directory(dist_path, path)
        else:
            return send_from_directory(dist_path, "index.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
