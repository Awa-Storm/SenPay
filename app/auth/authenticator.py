import bcrypt
from datetime import datetime, timedelta, timezone

# Coût bcrypt fixé à 12 — exigence OS-01 du cahier des charges
# Plus le coût est élevé, plus le hachage est lent à brute-forcer
BCRYPT_COST = 12

# Nombre maximum de tentatives avant verrouillage — exigence EF02/OS-07
MAX_ATTEMPTS = 3

# Durée de verrouillage en minutes après 3 échecs
LOCK_MINUTES = 15


def hash_pin(pin: str) -> str:
    """Hache un code PIN avec bcrypt (coût 12, sel unique par utilisateur)
    
    Utilisé à la création du compte et lors du changement de PIN.
    Le sel est généré aléatoirement par bcrypt — deux PIN identiques
    donneront des hashs différents.
    """
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=BCRYPT_COST)).decode()


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Vérifie qu'un PIN correspond à son hash bcrypt
    
    bcrypt.checkpw() est résistant aux attaques temporelles —
    il prend toujours le même temps peu importe où la différence se trouve.
    """
    return bcrypt.checkpw(pin.encode(), pin_hash.encode())


def authenticate(conn, phone: str, pin: str) -> tuple:
    """Authentifie un utilisateur par téléphone + PIN
    
    Retourne :
        (user_row, None)     → connexion réussie
        (None, 'locked')     → compte verrouillé
        (None, 'invalid')    → identifiants incorrects
    """
    
    # Cherche l'utilisateur par numéro de téléphone
    user = conn.execute(
        '''SELECT id, pin_hash, role, is_locked, failed_attempts,
                  locked_until, force_pin_change
           FROM users WHERE phone=?''',
        (phone,)
    ).fetchone()
    
    # Numéro introuvable en base
    if not user:
        return None, 'invalid'
    
    uid, pin_hash, role, locked, attempts, locked_until, force_chg = user
    
    # Vérifie si le compte est verrouillé
    if locked and locked_until:
        until = datetime.fromisoformat(locked_until).replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) < until:
            # Verrouillage encore actif → accès refusé
            return None, 'locked'
        
        # Verrouillage expiré → déverrouillage automatique
        conn.execute(
            'UPDATE users SET is_locked=0, failed_attempts=0, locked_until=NULL WHERE id=?',
            (uid,)
        )
    
    # Vérifie le PIN avec bcrypt
    if not verify_pin(pin, pin_hash):
        attempts += 1
        
        if attempts >= MAX_ATTEMPTS:
            # 3 échecs atteints → verrouille pour 15 minutes
            until = (datetime.now(timezone.utc) + timedelta(minutes=LOCK_MINUTES)).isoformat()
            conn.execute(
                'UPDATE users SET failed_attempts=?, is_locked=1, locked_until=? WHERE id=?',
                (attempts, until, uid)
            )
        else:
            # Incrémente seulement le compteur
            conn.execute(
                'UPDATE users SET failed_attempts=? WHERE id=?',
                (attempts, uid)
            )
        
        conn.commit()
        return None, 'invalid'
    
    # Connexion réussie → remet le compteur à zéro et note l'heure
    conn.execute(
        'UPDATE users SET failed_attempts=0, is_locked=0, last_login=? WHERE id=?',
        (datetime.now(timezone.utc).isoformat(), uid)
    )
    conn.commit()
    return user, None
