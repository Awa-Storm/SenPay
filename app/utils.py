from functools import wraps
from flask import session, abort

def require_role(*roles):
    """
    Décorateur RBAC : vérifie que l'utilisateur connecté a l'un des rôles autorisés.
    Retourne 403 si le rôle est insuffisant, 401 si non connecté.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                abort(401)  # Non connecté
            if session.get('role') not in roles:
                abort(403)  # Rôle insuffisant
            return f(*args, **kwargs)
        return decorated_function
    return decorator