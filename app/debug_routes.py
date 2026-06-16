from flask import Blueprint, render_template, g
from app.auth.decorators import require_role

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/session')
@require_role('admin')
def show_session():
    return f"Session: user_id={g.session['user_id']}, role={g.session['role']}"
