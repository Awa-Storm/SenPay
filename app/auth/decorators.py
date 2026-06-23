from functools import wraps
from flask import session, redirect, url_for, flash, abort
from datetime import datetime, timedelta

SESSION_TIMEOUT_SECONDS = 60  # 1 minute pour le test

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Vérifier si l'utilisateur est connecté
            if 'user_id' not in session:
                flash('Votre session a expire. Veuillez vous reconnecter.', 'warning')
                return redirect(url_for('auth.login'))

            # Vérifier l'expiration de la session
            if 'last_activity' in session:
                try:
                    last = datetime.fromisoformat(session['last_activity'])
                    if datetime.utcnow() - last > timedelta(seconds=SESSION_TIMEOUT_SECONDS):
                        session.clear()
                        flash('Votre session a expire. Veuillez vous reconnecter.', 'warning')
                        return redirect(url_for('auth.login'))
                except:
                    pass

            # Mettre à jour l'activité
            session['last_activity'] = datetime.utcnow().isoformat()

            # Vérifier le rôle
            if session.get('role') not in roles:
                abort(403)

            return f(*args, **kwargs)
        return wrapper
    return decorator
