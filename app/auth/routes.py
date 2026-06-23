from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.database import get_db
from app.crypto.pin import hash_pin
from app.auth.authenticator import authenticate
import bcrypt
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        conn = get_db()
        
        user, error = authenticate(conn, phone, pin)
        
        if error == 'invalid':
            conn.close()
            return render_template('login.html', error='Téléphone ou PIN incorrect')

        if error == 'blocked':
            conn.close()
            return render_template('login.html', error='Ce compte a été bloqué. Contactez un administrateur.')
        
        # Vérifier MFA
        mfa_secret = conn.execute('SELECT mfa_secret FROM users WHERE id = ?', (user['id'],)).fetchone()
        conn.close()
        
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['phone'] = phone
        session['last_activity'] = datetime.utcnow().isoformat()

        if mfa_secret and mfa_secret['mfa_secret']:
            session['mfa_pending'] = user['id']
            return redirect(url_for('mfa.login_verify'))

        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user['role'] == 'agent':
            return redirect(url_for('agent.dashboard'))
        else:
            return redirect(url_for('client.dashboard'))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')
        if not re.match(r'^[0-9]{9}$', phone):
            return render_template('register.html', error='Numéro invalide (9 chiffres)')
        if pin != confirm_pin:
            return render_template('register.html', error='Les PIN ne correspondent pas')
        if len(pin) < 4:
            return render_template('register.html', error='PIN trop court (min 4)')
        conn = get_db()
        existing = conn.execute('SELECT id FROM users WHERE phone = ?', (phone,)).fetchone()
        if existing:
            conn.close()
            return render_template('register.html', error='Ce numéro est déjà utilisé')
        hashed_pin = hash_pin(pin)
        conn.execute(
            'INSERT INTO users (phone, pin_hash, role, balance_enc, balance_iv, balance_tag, force_pin_change) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (phone, hashed_pin, 'client', '', '', '', 0)
        )
        conn.commit()
        conn.close()

        flash('Compte client créé avec succès. Connectez-vous pour activer la double authentification.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/change-pin', methods=['GET', 'POST'])
def change_pin():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        old_pin = request.form.get('old_pin')
        new_pin = request.form.get('new_pin')
        confirm_pin = request.form.get('confirm_pin')
        if new_pin != confirm_pin:
            return render_template('change_pin.html', error='Les PIN ne correspondent pas')
        conn = get_db()
        user = conn.execute('SELECT pin_hash FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        if not bcrypt.checkpw(old_pin.encode('utf-8'), user['pin_hash'].encode('utf-8')):
            conn.close()
            return render_template('change_pin.html', error='Ancien PIN incorrect')
        new_hash = bcrypt.hashpw(new_pin.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
        conn.execute('UPDATE users SET pin_hash = ?, force_pin_change = 0 WHERE id = ?', (new_hash, session['user_id']))
        conn.commit()
        conn.close()
        session['force_pin_change'] = 0
        flash('PIN changé avec succès', 'success')
        return redirect(url_for('auth.login'))
    return render_template('change_pin.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

