from flask import Flask
from config import Config
from app.models.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation de la base de données
    with app.app_context():
        init_db()

    # Enregistrement des blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app