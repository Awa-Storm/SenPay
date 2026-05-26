import secrets
from datetime import datetime, timedelta, timezone
from flask import session

SESSION_LIFETIME = 30  # minutes

def create_session(user_id, role):
    session['user_id'] = user_id
    session['role'] = role
    session['token'] = secrets.token_hex(32)
    session['last_active'] = datetime.now(timezone.utc).isoformat()

def is_session_valid():
    if 'last_active' not in session:
        return False
    last = datetime.fromisoformat(session['last_active'])
    expired = datetime.now(timezone.utc) - last > timedelta(minutes=SESSION_LIFETIME)
    if expired:
        session.clear()
        return False
    session['last_active'] = datetime.now(timezone.utc).isoformat()
    return True

def destroy_session():
    session.clear()
