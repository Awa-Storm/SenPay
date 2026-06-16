from functools import wraps
from flask import session, abort

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                abort(401)
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
