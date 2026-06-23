import pyotp
import qrcode
import io
import base64
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models.database import get_db

mfa_bp = Blueprint('mfa', __name__, url_prefix='/mfa')


def generate_qr_data_uri(uri: str) -> str:
    """Génère un QR code en mémoire, encodé en base64, sans appel réseau externe."""
    img = qrcode.make(uri, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


@mfa_bp.route('/setup')
def setup():
    if 'user_id' not in session:
        flash('Veuillez vous connecter d abord.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_db()
    user = conn.execute('SELECT phone, mfa_secret FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if user and user['mfa_secret']:
        flash('MFA deja active sur ce compte.', 'info')
        return redirect(url_for('client.dashboard'))

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user['phone'], issuer_name='SenPay')

    qr_url = generate_qr_data_uri(uri)

    session['mfa_temp_secret'] = secret
    return render_template('mfa_setup_external.html', qr_url=qr_url, secret=secret)


@mfa_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'user_id' not in session:
        flash('Veuillez vous connecter d abord.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code')
        secret = session.get('mfa_temp_secret')
        if not secret:
            flash('Session MFA expiree. Veuillez recommencer.', 'danger')
            return redirect(url_for('mfa.setup'))

        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            conn = get_db()
            conn.execute('UPDATE users SET mfa_secret = ? WHERE id = ?', (secret, session['user_id']))
            conn.commit()
            conn.close()
            session.pop('mfa_temp_secret', None)
            flash('MFA active avec succes !', 'success')
            return redirect(url_for('client.dashboard'))
        else:
            flash('Code MFA invalide. Veuillez reessayer.', 'danger')

    return render_template('mfa_verify.html')


@mfa_bp.route('/login-verify', methods=['GET', 'POST'])
def login_verify():
    if 'mfa_pending' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code')
        conn = get_db()
        user = conn.execute('SELECT mfa_secret FROM users WHERE id = ?', (session['mfa_pending'],)).fetchone()
        conn.close()

        if not user or not user['mfa_secret']:
            session.pop('mfa_pending', None)
            return redirect(url_for('auth.login'))

        totp = pyotp.TOTP(user['mfa_secret'])
        if totp.verify(code):
            session['user_id'] = session['mfa_pending']
            session.pop('mfa_pending', None)
            return redirect(url_for('client.dashboard'))
        else:
            flash('Code MFA invalide.', 'danger')

    return render_template('mfa_login_verify.html')

@mfa_bp.route('/disable', methods=['GET', 'POST'])
def disable():
    if 'user_id' not in session:
        flash('Veuillez vous connecter d abord.', 'warning')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute('UPDATE users SET mfa_secret = NULL WHERE id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        flash('Double authentification desactivee.', 'info')
        return redirect(url_for('client.dashboard'))
    return render_template('mfa_disable_confirm.html')
