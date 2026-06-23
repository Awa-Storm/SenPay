from flask import Flask, session
from config import Config
from app.models.database import init_db
import secrets

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.permanent_session_lifetime = Config.PERMANENT_SESSION_LIFETIME

    with app.app_context():
        init_db()

    # Middleware de securite
    @app.after_request
    def security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # CSRF protection
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
    from app.mfa_routes import mfa_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(agent_bp, url_prefix='/agent')
    app.register_blueprint(mfa_bp)

    return app

