from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.database import get_db
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        pin = request.form.get('pin')
        
        conn = get_db()
        user = conn.execute(
            "SELECT id, phone, pin_hash, role FROM users WHERE phone = ?",
            (phone,)
        ).fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(pin.encode('utf-8'), user['pin_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['phone'] = user['phone']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'agent':
                return redirect(url_for('agent.dashboard'))
            else:
                return redirect(url_for('client.dashboard'))
        else:
            return render_template('login.html', error="Telephone ou PIN incorrect")
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
