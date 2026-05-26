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
