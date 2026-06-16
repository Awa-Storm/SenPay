import secrets
from datetime import datetime, timedelta, timezone


def create_session(conn, user_id, role, force_pin_change=0) -> str:
    """Crée une nouvelle session en base de données après connexion réussie
    
    Paramètres :
        conn            → connexion SQLite active
        user_id         → identifiant de l'utilisateur connecté
        role            → 'client', 'agent' ou 'admin'
        force_pin_change → 1 si l'utilisateur doit changer son PIN dès la connexion
    
    Retourne :
        token → jeton de session à stocker dans le cookie côté client
    """
    
    # Génère un jeton aléatoire de 32 octets (64 caractères hex)
    # Impossible à deviner — entropie de 256 bits
    token = secrets.token_hex(32)
    
    now = datetime.now(timezone.utc)
    
    # Expiration fixée à 30 min après la création — exigence EF02
    exp = (now + timedelta(minutes=30)).isoformat()
    
    # Insère la session en base — le token est la clé primaire
    conn.execute(
        '''INSERT INTO sessions
           (token, user_id, role, created_at, expires_at, force_pin_change)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (token, user_id, role, now.isoformat(), exp, force_pin_change)
    )
    conn.commit()
    
    # Retourne le token pour le placer dans le cookie HTTP
    return token


def validate_session(conn, token: str) -> dict | None:
    """Vérifie qu'un token de session est valide et non expiré
    
    Paramètres :
        conn  → connexion SQLite active
        token → token lu depuis le cookie de la requête
    
    Retourne :
        dict de la session si valide, None si expirée ou inexistante
    """
    
    # Cherche le token en base
    row = conn.execute(
        'SELECT * FROM sessions WHERE token=?', (token,)
    ).fetchone()
    
    # Token inexistant → session invalide
    if not row:
        return None
    
    # Vérifie si la session a expiré
    exp = datetime.fromisoformat(row['expires_at']).replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > exp:
        # Session expirée → supprime de la base et refuse l'accès
        conn.execute('DELETE FROM sessions WHERE token=?', (token,))
        conn.commit()
        return None
    
    # Session valide → renouvelle l'expiration (fenêtre glissante de 30 min)
    # Chaque action repart le compteur à zéro — inactivité réelle de 30 min requise
    new_exp = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    conn.execute(
        'UPDATE sessions SET expires_at=? WHERE token=?', (new_exp, token)
    )
    conn.commit()
    
    # Retourne la session mise à jour
    row = dict(row)
    row['expires_at'] = new_exp
    return row


def revoke_session(conn, token: str) -> None:
    """Révoque une session au logout — supprime le token de la base
    
    Après révocation, le token dans le cookie devient inutilisable
    même s'il n'a pas encore expiré.
    """
    conn.execute('DELETE FROM sessions WHERE token=?', (token,))
    conn.commit()
