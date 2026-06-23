from flask import Blueprint, render_template, request, g, redirect, url_for, flash, session
from app.auth.decorators import require_role
from app.models.database import get_db
from app.crypto.pin import hash_pin
from app.transactions.verifier import verify_tx_chain
from app.audit.verifier import verify_audit_chain
import re

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
    all_users = conn.execute('SELECT id, phone, role, force_pin_change, is_locked FROM users').fetchall()
    conn.close()
    return render_template('admin/users_new.html', users=all_users)

@admin_bp.route('/audit')
@require_role('admin')
def audit():
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db()
    entries = conn.execute(
        'SELECT id, timestamp, action, user_id, amount, hmac FROM audit_log ORDER BY id ASC LIMIT ? OFFSET ?',
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

@admin_bp.route('/force-pin-change/<int:user_id>', methods=['POST'])
@require_role('admin')
def force_pin_change(user_id):
    conn = get_db()
    conn.execute('UPDATE users SET force_pin_change = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash(f'Changement PIN forcé pour l utilisateur #{user_id}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/register-user', methods=['GET', 'POST'])
@require_role('admin')
def register_user():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')
        role = request.form.get('role')

        if not re.match(r'^[0-9]{9}$', phone):
            return render_template('admin/register_user.html', error='Numéro invalide (9 chiffres)')
        if pin != confirm_pin:
            return render_template('admin/register_user.html', error='Les PIN ne correspondent pas')
        if len(pin) < 4:
            return render_template('admin/register_user.html', error='PIN trop court (min 4)')

        conn = get_db()
        existing = conn.execute('SELECT id FROM users WHERE phone = ?', (phone,)).fetchone()
        if existing:
            conn.close()
            return render_template('admin/register_user.html', error='Ce numéro est déjà utilisé')

        hashed_pin = hash_pin(pin)
        conn.execute(
            'INSERT INTO users (phone, pin_hash, role, balance_enc, balance_iv, balance_tag, force_pin_change) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (phone, hashed_pin, role, '', '', '', 1)
        )
        conn.commit()
        conn.close()

        flash(f'Compte {role} créé avec succès.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/register_user.html')

@admin_bp.route('/delete/<int:user_id>', methods=['POST'])
@require_role('admin')
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('admin.users'))

    conn = get_db()
    user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('admin.users'))

    conn.execute('DELETE FROM transactions WHERE sender_id = ? OR receiver_id = ?', (user_id, user_id))
    conn.execute('DELETE FROM audit_log WHERE user_id = ?', (user_id,))
    conn.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash(f'Utilisateur #{user_id} supprimé avec succès.', 'danger')
    return redirect(url_for('admin.users'))


@admin_bp.route('/toggle-block/<int:user_id>', methods=['POST'])
@require_role('admin')
def toggle_block(user_id):
    if user_id == session.get('user_id'):
        flash('Vous ne pouvez pas bloquer votre propre compte.', 'danger')
        return redirect(url_for('admin.users'))

    conn = get_db()
    user = conn.execute('SELECT is_locked FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('admin.users'))

    new_state = 0 if user['is_locked'] else 1
    conn.execute('UPDATE users SET is_locked = ? WHERE id = ?', (new_state, user_id))
    conn.commit()
    conn.close()

    action = 'bloqué' if new_state else 'débloqué'
    flash(f'Compte #{user_id} {action} avec succès.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/repair-audit', methods=['POST'])
@require_role('admin')
def repair_audit():
    from app.audit.logger import compute_hmac, get_genesis_hmac
    from datetime import datetime, timezone

    conn = get_db()
    rows = conn.execute(
        'SELECT id, user_id, action, detail, amount, timestamp FROM audit_log ORDER BY id ASC'
    ).fetchall()

    prev_hmac = get_genesis_hmac()
    for row in rows:
        new_hmac = compute_hmac(row['action'], row['timestamp'], row['user_id'], row['amount'], prev_hmac)
        conn.execute(
            'UPDATE audit_log SET hmac = ?, prev_hmac = ? WHERE id = ?',
            (new_hmac, prev_hmac, row['id'])
        )
        prev_hmac = new_hmac

    conn.commit()
    conn.close()

    flash(f'Chaîne d\'audit réparée : {len(rows)} entrée(s) resignée(s) avec la clé actuelle.', 'success')
    return redirect(url_for('admin.verify'))

