from flask import Blueprint, render_template, request
from app.auth.decorators import require_role
from app.models.database import get_db
from app.transactions.verifier import verify_tx_chain
from app.audit.verifier import verify_audit_chain

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@require_role('admin')
def dashboard():
    conn = get_db()
    nb_comptes = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    return render_template('admin/dashboard.html', nb_comptes=nb_comptes)

@admin_bp.route('/users')
@require_role('admin')
def users():
    conn = get_db()
    all_users = conn.execute('SELECT id, phone, role, is_locked FROM users').fetchall()
    conn.close()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/audit')
@require_role('admin')
def audit():
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db()
    entries = conn.execute(
        'SELECT id, timestamp, action, user_id, amount, hmac '
        'FROM audit_log ORDER BY id ASC LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()
    total = conn.execute('SELECT COUNT(*) FROM audit_log').fetchone()[0]
    conn.close()

    entries_display = [
        {**dict(e), 'hmac_short': e['hmac'][:8] + '...'}
        for e in entries
    ]

    return render_template(
        'admin/audit.html',
        entries=entries_display,
        page=page,
        total_pages=(total + per_page - 1) // per_page
    )

@admin_bp.route('/verify')
@require_role('admin')
def verify():
    conn = get_db()
    audit_ok, audit_err_id = verify_audit_chain(conn)
    tx_ok, tx_err_id = verify_tx_chain(conn)
    conn.close()
    return render_template(
        'admin/verify.html',
        audit_ok=audit_ok,
        audit_err_id=audit_err_id,
        tx_ok=tx_ok,
        tx_err_id=tx_err_id
    )
