from flask import Flask
from app.models.database import init_db
def create_app():
    app = Flask(__name__)
    from config import SECRET_KEY, DB_PATH
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DB_PATH'] = DB_PATH
    init_db()
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    import sqlite3
    import logging
    from app.audit.verifier import verify_audit_chain

    conn = sqlite3.connect(DB_PATH)
    valid, bad_id = verify_audit_chain(conn)
    if not valid:
        logging.critical(f"JOURNAL CORROMPU — id={bad_id}")
    conn.close()
    return app
