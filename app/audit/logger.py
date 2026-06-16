import hmac
import hashlib
import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


def derive_audit_key(master_key_hex: str) -> bytes:
    """Dérive une clé spécifique pour l'audit depuis la clé maître SENPAY_KEY"""
    
    # Convertit la clé maître de format hex (texte) en bytes
    master_key = bytes.fromhex(master_key_hex)
    
    # HKDF : algorithme standard pour dériver une sous-clé depuis une clé maître
    # length=32 → clé de 32 octets (256 bits) pour HMAC-SHA256
    # info=b'senpay-audit' → étiquette unique, garantit que cette clé
    #                        ne sera jamais la même que celle de Salimata (b'senpay-balance')
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'senpay-audit'
    )
    return hkdf.derive(master_key)


def _get_audit_key() -> bytes:
    """Récupère SENPAY_KEY depuis l'environnement et retourne la clé audit dérivée"""
    
    # Lit la variable d'environnement (jamais dans le code directement)
    master = os.environ.get('SENPAY_KEY')
    
    # Sécurité : on refuse de démarrer si la clé n'est pas définie
    if not master:
        raise RuntimeError("SENPAY_KEY non definie dans l'environnement")
    
    return derive_audit_key(master)


def compute_hmac(action, ts, user_id, amount, prev_hmac) -> str:
    """Calcule l'empreinte HMAC-SHA256 d'une entrée du journal
    
    Paramètres :
        action    → ex: 'LOGIN_SUCCESS', 'TRANSFERT', 'LOGOUT'
        ts        → horodatage UTC au format ISO ex: '2025-01-15T10:30:00'
        user_id   → identifiant de l'utilisateur concerné
        amount    → montant si transaction financière, sinon 0.0
        prev_hmac → empreinte de l'entrée précédente (crée la chaîne)
    """
    
    # Récupère la clé audit depuis l'environnement
    key = _get_audit_key()
    
    # Assemble tous les champs en un seul message séparé par |
    # Exemple : "LOGIN_SUCCESS|2025-01-15T10:30:00|3|0.0|abc123..."
    msg = f"{action}|{ts}|{user_id}|{amount}|{prev_hmac}".encode()
    
    # Calcule et retourne le HMAC-SHA256 en hexadécimal (64 caractères)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()



def get_genesis_hmac() -> str:
    """Calcule l'empreinte de départ de la chaîne d'audit
    
    C'est le prev_hmac de la toute première entrée du journal.
    Toute la chaîne part de ce point fixe — si on le falsifie,
    la vérification échoue immédiatement.
    """
    
    # Récupère la clé audit depuis l'environnement
    key = _get_audit_key()
    
    # Calcule HMAC-SHA256 du mot "GENESIS" en bytes
    # C'est le seul endroit où prev_hmac ne vient pas d'une entrée réelle
    return hmac.new(key, b'GENESIS', hashlib.sha256).hexdigest()



def log_action(conn, user_id, action, detail=None, amount=0.0):
    """Enregistre une action dans le journal d'audit de façon infalsifiable
    
    Paramètres :
        conn    → connexion SQLite active (passée depuis la route Flask)
        user_id → identifiant de l'utilisateur qui effectue l'action
        action  → nom de l'action ex: 'LOGIN_SUCCESS', 'LOGIN_FAIL', 'LOGOUT'
        detail  → information complémentaire optionnelle ex: 'tentative 2/3'
        amount  → montant concerné si transaction financière, sinon 0.0
    """
    
    cursor = conn.cursor()
    
    # Récupère le HMAC de la dernière entrée du journal
    # C'est lui qui deviendra le prev_hmac de la nouvelle entrée
    cursor.execute(
        "SELECT hmac FROM audit_log ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    
    if row is None:
        # Journal vide : c'est la toute première entrée
        # On utilise GENESIS comme point de départ de la chaîne
        prev_hmac = get_genesis_hmac()
    else:
        # Journal non vide : on chaîne avec la dernière empreinte
        prev_hmac = row[0]
    
    # Horodatage UTC de l'action au moment exact de l'appel
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    
    # Calcule l'empreinte de cette nouvelle entrée
    h = compute_hmac(action, ts, user_id, amount, prev_hmac)
    
    # Insère l'entrée dans la base de données
    # prev_hmac est stocké pour permettre la vérification ultérieure
    cursor.execute(
        """INSERT INTO audit_log
           (user_id, action, detail, amount, timestamp, hmac, prev_hmac)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, action, detail, amount, ts, h, prev_hmac)
    )
    
    # Sauvegarde immédiate — aucune action ne doit être perdue
    conn.commit()
