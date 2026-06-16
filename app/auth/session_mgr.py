import secrets
from datetime import datetime, timedelta, timezone

def create_session(conn, user_id, role, force_pin_change=0):
    token = secrets.token_hex(32)
    now = datetime.now(timezone.utc)
    exp = (now + timedelta(minutes=30)).isoformat()
    conn.execute(
        "INSERT INTO sessions (token, user_id, role, created_at, expires_at, force_pin_change) VALUES (?, ?, ?, ?, ?, ?)",
        (token, user_id, role, now.isoformat(), exp, force_pin_change)
    )
    conn.commit()
    return token

def validate_session(conn, token):
    row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
    if not row:
        return None
    
    sess = dict(row)
    exp = datetime.fromisoformat(sess['expires_at']).replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        return None
    
    new_exp = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    conn.execute("UPDATE sessions SET expires_at = ? WHERE token = ?", (new_exp, token))
    conn.commit()
    sess['expires_at'] = new_exp
    
    return sess

def revoke_session(conn, token):
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
