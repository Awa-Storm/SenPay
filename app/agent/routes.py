from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.auth.decorators import require_role
from app.models.database import get_db
from app.crypto.pin import hash_pin
from app.transactions.recharge import execute_recharge
import re

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')

@agent_bp.route('/dashboard')
@require_role('agent', 'admin')
def dashboard():
    return render_template('agent/dashboard.html')

@agent_bp.route('/recharge', methods=['GET', 'POST'])
@require_role('agent', 'admin')
def recharge():
    if request.method == 'POST':
        client_phone = request.form.get('client_phone')
        amount = float(request.form.get('amount', 0))
        conn = get_db()
        success, message = execute_recharge(conn, session['user_id'], client_phone, amount)
        conn.close()
        if success:
            return render_template('agent/recharge.html', message=message)
        else:
            return render_template('agent/recharge.html', error=message)
    return render_template('agent/recharge.html')

@agent_bp.route('/history')
@require_role('agent', 'admin')
def history():
    conn = get_db()
    recharges = conn.execute(
        'SELECT id, amount, receiver_id, timestamp FROM transactions '
        'WHERE sender_id = ? AND tx_type = "recharge" ORDER BY timestamp DESC LIMIT 50',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('agent/history.html', recharges=recharges)

@agent_bp.route('/register-client', methods=['GET', 'POST'])
@require_role('agent', 'admin')
def register_client():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')

        if not re.match(r'^[0-9]{9}$', phone):
            return render_template('agent/register_client.html', error='Numéro invalide (9 chiffres)')
        if pin != confirm_pin:
            return render_template('agent/register_client.html', error='Les PIN ne correspondent pas')
        if len(pin) < 4:
            return render_template('agent/register_client.html', error='PIN trop court (min 4)')

        conn = get_db()
        existing = conn.execute('SELECT id FROM users WHERE phone = ?', (phone,)).fetchone()
        if existing:
            conn.close()
            return render_template('agent/register_client.html', error='Ce numéro est déjà utilisé')

        hashed_pin = hash_pin(pin)
        conn.execute(
            'INSERT INTO users (phone, pin_hash, role, balance_enc, balance_iv, balance_tag, force_pin_change) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (phone, hashed_pin, 'client', '', '', '', 1)
        )
        conn.commit()
        conn.close()

        flash('Compte client créé avec succès.', 'success')
        return redirect(url_for('agent.dashboard'))

    return render_template('agent/register_client.html')
