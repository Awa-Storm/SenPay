import sqlite3
from flask import Blueprint, request, redirect, url_for, session, render_template, make_response
from config import DB_PATH
from app.auth.authenticator import authenticate, hash_pin, verify_pin
from app.auth.session_mgr import create_session, validate_session, revoke_session
from app.audit.logger import log_action

auth_bp = Blueprint('auth', __name__)


def get_db():
    """Ouvre une connexion SQLite avec accès par nom de colonne"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permet row['colonne'] au lieu de row[0]
    return conn


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion — GET affiche le formulaire, POST vérifie les identifiants"""
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        pin   = request.form.get('pin', '').strip()
        
        conn = get_db()
        
        # Délègue toute la logique d'authentification à authenticator.py
        # (verrouillage, déverrouillage auto, compteur de tentatives)
        user, error = authenticate(conn, phone, pin)
        
        if error == 'locked':
            log_action(conn, None, 'LOGIN_LOCKED', detail=phone)
            conn.close()
            return render_template('login.html',
                error="Compte verrouillé 15 min après 3 échecs.")
        
        if error == 'invalid':
            log_action(conn, None, 'LOGIN_FAIL', detail=phone)
            conn.close()
            return render_template('login.html',
                error="Numéro ou PIN incorrect.")
        
        # Connexion réussie
        user_id = user[0]
        role    = user[2]
        force   = user[6]  # force_pin_change
        
        # Crée la session en base de données
        token = create_session(conn, user_id, role, force_pin_change=force)
        
        # Enregistre dans le journal d'audit
        log_action(conn, user_id, 'LOGIN_SUCCESS')
        conn.close()
        
        # Place le token dans un cookie HTTP sécurisé
        if force:
            response = make_response(redirect(url_for('auth.change_pin')))
        elif role == 'admin':
            response = make_response(redirect(url_for('admin.dashboard')))
        else:
            response = make_response(redirect(url_for('auth.login')))
        
        # httponly=True → inaccessible depuis JavaScript (protection XSS)
        response.set_cookie('session_token', token, httponly=True, samesite='Strict')
        return response
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Route de déconnexion — révoque le token en base et supprime le cookie"""
    
    token = request.cookies.get('session_token')
    
    if token:
        conn = get_db()
        # Récupère user_id avant de révoquer pour le journal
        row = conn.execute(
            'SELECT user_id FROM sessions WHERE token=?', (token,)
        ).fetchone()
        if row:
            log_action(conn, row['user_id'], 'LOGOUT')
        # Supprime la session de la base — token inutilisable immédiatement
        revoke_session(conn, token)
        conn.close()
    
    # Supprime le cookie côté client
    response = make_response(redirect(url_for('auth.login')))
    response.delete_cookie('session_token')
    return response


@auth_bp.route('/change-pin', methods=['GET', 'POST'])
def change_pin():
    """Route de changement de PIN — obligatoire à la première connexion (EF11)"""
    
    token = request.cookies.get('session_token')
    if not token:
        return redirect(url_for('auth.login'))
    
    conn = get_db()
    sess = validate_session(conn, token)
    if not sess:
        conn.close()
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        old_pin     = request.form.get('old_pin', '')
        new_pin     = request.form.get('new_pin', '')
        confirm_pin = request.form.get('confirm_pin', '')
        
        # Vérifie que les deux nouveaux PIN correspondent
        if new_pin != confirm_pin:
            conn.close()
            return render_template('change_pin.html',
                error="Les PIN ne correspondent pas.")
        
        # Récupère le hash actuel
        user = conn.execute(
            'SELECT pin_hash FROM users WHERE id=?', (sess['user_id'],)
        ).fetchone()
        
        # Vérifie l'ancien PIN avant d'autoriser le changement
        if not verify_pin(old_pin, user['pin_hash']):
            conn.close()
            return render_template('change_pin.html',
                error="Ancien PIN incorrect.")
        
        # Hache le nouveau PIN et met à jour la base
        new_hash = hash_pin(new_pin)
        conn.execute(
            'UPDATE users SET pin_hash=?, force_pin_change=0 WHERE id=?',
            (new_hash, sess['user_id'])
        )
        conn.commit()
        
        # Enregistre dans le journal d'audit
        log_action(conn, sess['user_id'], 'PIN_CHANGED')
        conn.close()
        
        return redirect(url_for('auth.login'))
    
    conn.close()
    return render_template('change_pin.html')
