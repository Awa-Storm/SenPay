from flask import Blueprint, render_template, session, request
from app.auth.decorators import require_role
from app.models.database import get_db
from app.crypto.aes import decrypt_balance
from app.transactions.transfer import execute_transfer

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/dashboard')
@require_role('client')
def dashboard():
    conn = get_db()
    user = conn.execute(
        'SELECT id, phone, balance_enc, balance_iv, balance_tag, mfa_secret FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    conn.close()
    try:
        balance = decrypt_balance(user['balance_enc'], user['balance_iv'], user['balance_tag'])
    except Exception as e:
        balance = 0.0
    mfa_active = bool(user['mfa_secret'])
    return render_template('client/dashboard.html', balance=balance, mfa_active=mfa_active)

@client_bp.route('/transfer', methods=['GET', 'POST'])
@require_role('client')
def transfer():
    if request.method == 'POST':
        receiver_phone = request.form.get('receiver_phone')
        amount = float(request.form.get('amount', 0))
        conn = get_db()
        success, result = execute_transfer(conn, session['user_id'], receiver_phone, amount)
        conn.close()
        if success:
            return render_template('client/transfer.html', message=f'Transfert reussi ! Hash: {result[:16]}...')
        else:
            return render_template('client/transfer.html', error=result)
    return render_template('client/transfer.html')

@client_bp.route('/history')
@require_role('client')
def history():
    conn = get_db()
    transactions = conn.execute(
        'SELECT id, amount, tx_type, sender_id, receiver_id, timestamp, tx_hash '
        'FROM transactions WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp DESC LIMIT 50',
        (session['user_id'], session['user_id'])
    ).fetchall()
    conn.close()
    return render_template('client/history.html', transactions=transactions)
