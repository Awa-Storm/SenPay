import bcrypt
from datetime import datetime, timezone

BCRYPT_COST = 12

def hash_pin(pin):
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=BCRYPT_COST)).decode()

def verify_pin(pin, pin_hash):
    return bcrypt.checkpw(pin.encode(), pin_hash.encode())

def authenticate(conn, phone, pin):
    """
    Authentifie un utilisateur.
    Retourne (user_row, None) si succès,
             (None, 'invalid') si téléphone/PIN incorrect,
             (None, 'blocked') si le compte est bloqué par un admin.
    """
    user = conn.execute(
        'SELECT id, pin_hash, role, force_pin_change, is_locked FROM users WHERE phone=?',
        (phone,)
    ).fetchone()

    if not user:
        return None, 'invalid'

    uid, pin_hash, role, force_chg, is_locked = user

    if is_locked:
        return None, 'blocked'

    if not verify_pin(pin, pin_hash):
        return None, 'invalid'

    conn.execute('UPDATE users SET last_login=? WHERE id=?', (datetime.utcnow().isoformat()+'Z', uid))
    conn.commit()
    return user, None
