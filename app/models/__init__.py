from flask import Flask
from config import Config
from app.models.database import init_db
import logging
import sqlite3

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation de la base de données
    with app.app_context():
        init_db()

    # Vérification d'intégrité du journal d'audit (si module Awa disponible)
    try:
        from app.audit.verifier import verify_audit_chain
        conn = sqlite3.connect(Config.DB_PATH)
        valid, bad_id = verify_audit_chain(conn)
        if not valid:
            logging.critical(f"JOURNAL D'AUDIT CORROMPU — première entrée corrompue : id={bad_id}")
        conn.close()
    except ImportError:
        app.logger.warning("Module audit/verifier.py non disponible — vérification d'intégrité désactivée")

    # Enregistrement des blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app