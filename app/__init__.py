from flask import Flask, session
from config import Config
from app.models.database import init_db
import secrets
import sqlite3
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        init_db()
    
    # Middleware de sécurité — headers HTTP (Salimata)
    @app.after_request
    def security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Protection CSRF — jeton injecté dans tous les templates (Salimata)
    @app.context_processor
    def inject_csrf_token():
        def generate_csrf_token():
            if 'csrf_token' not in session:
                session['csrf_token'] = secrets.token_hex(32)
            return session['csrf_token']
        return dict(csrf_token=generate_csrf_token)
    
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.client.routes import client_bp
    from app.agent.routes import agent_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(agent_bp, url_prefix='/agent')
    
    # Vérification intégrité du journal au démarrage (Awa)
    from config import DB_PATH
    from app.audit.verifier import verify_audit_chain
    conn = sqlite3.connect(DB_PATH)
    valid, bad_id = verify_audit_chain(conn)
    if not valid:
        logging.critical(f"JOURNAL CORROMPU — id={bad_id}")
    conn.close()
    
    return app
