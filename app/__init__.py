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
    return app
