import bcrypt
import sqlite3
from flask import Blueprint, request, redirect, url_for, session, render_template
from config import DB_PATH
from app.auth.session_mgr import create_session, is_session_valid, destroy_session
from app.audit.logger import log_action

# Blueprint : groupe toutes les routes d'authentification sous un même module
# Flask l'enregistre dans create_app() côté Serigne
auth_bp = Blueprint('auth', __name__)


def get_db():
    """Ouvre et retourne une connexion SQLite à la base de données SenPay"""
    return sqlite3.connect(DB_PATH)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion
    
    GET  → affiche le formulaire de connexion
    POST → vérifie les identifiants et crée la session si corrects
    """
    
    if request.method == 'POST':
        
        # Récupère les champs du formulaire HTML
        phone = request.form.get('phone', '').strip()
        pin   = request.form.get('pin', '').strip()
        
        conn = get_db()
        cur  = conn.cursor()
        
        # Cherche l'utilisateur par son numéro de téléphone
        cur.execute(
            """SELECT id, pin_hash, role, is_locked, failed_attempts
               FROM users WHERE phone=?""",
            (phone,)
        )
        user = cur.fetchone()
        
        # Numéro introuvable dans la base
        if not user:
            conn.close()
            return render_template('login.html', error="Compte introuvable.")
        
        user_id, pin_hash, role, is_locked, failed = user
        
        # Compte verrouillé après 3 échecs → accès refusé
        if is_locked:
            conn.close()
            return render_template('login.html',
                error="Compte verrouille. Contactez l'administrateur.")
        
        # Vérifie le PIN avec bcrypt
        # Note : quand Salimata aura codé verify_pin(), remplace cette ligne par :
        # from app.crypto.crypto import verify_pin
        # if verify_pin(pin, pin_hash):
        if bcrypt.checkpw(pin.encode(), pin_hash.encode()):
            
            # PIN correct : remet le compteur d'échecs à zéro
            cur.execute(
                "UPDATE users SET failed_attempts=0 WHERE id=?",
                (user_id,)
            )
            conn.commit()
            
            # Crée la session Flask (jeton 32 octets + horodatage)
            create_session(user_id, role)
            
            # Enregistre la connexion réussie dans le journal d'audit
            log_action(conn, user_id, 'LOGIN_SUCCESS')
            conn.close()
            
            # Redirige selon le rôle de l'utilisateur
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('auth.login'))
        
        else:
            # PIN incorrect : incrémente le compteur d'échecs
            failed += 1
            
            # Verrouille le compte si 3 échecs consécutifs (exigence EF02/OS-07)
            locked = 1 if failed >= 3 else 0
            
            cur.execute(
                "UPDATE users SET failed_attempts=?, is_locked=? WHERE id=?",
                (failed, locked, user_id)
            )
            conn.commit()
            
            # Enregistre l'échec dans le journal d'audit
            log_action(conn, user_id, 'LOGIN_FAIL',
                detail=f"tentative {failed}/3")
            conn.close()
            
            # Message d'erreur adapté selon si le compte vient d'être verrouillé
            if locked:
                msg = "Compte verrouille apres 3 echecs. Contactez l'administrateur."
            else:
                msg = f"PIN incorrect. Tentative {failed}/3."
            
            return render_template('login.html', error=msg)
    
    # GET : affiche simplement le formulaire
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Route de déconnexion
    
    Enregistre le logout dans le journal puis détruit la session.
    Redirige vers /login.
    """
    
    # Récupère l'identifiant avant de détruire la session
    user_id = session.get('user_id')
    
    if user_id:
        conn = get_db()
        # Enregistre la déconnexion dans le journal d'audit
        log_action(conn, user_id, 'LOGOUT')
        conn.close()
    
    # Détruit la session Flask (cookie inutilisable immédiatement)
    destroy_session()
    
    # Redirige vers la page de connexion
    return redirect(url_for('auth.login'))
