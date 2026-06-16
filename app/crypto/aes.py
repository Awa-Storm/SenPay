import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.crypto.keys import BALANCE_KEY

def encrypt_balance(amount_fcfa):
    """Chiffre un solde en FCFA avec AES-256-GCM."""
    # Générer un IV aléatoire de 96 bits (12 bytes)
    iv = os.urandom(12)
    
    # Chiffrer
    aesgcm = AESGCM(BALANCE_KEY)
    ciphertext = aesgcm.encrypt(iv, str(amount_fcfa).encode(), None)
    
    # Séparer ciphertext et tag (les 16 derniers bytes)
    ct = ciphertext[:-16]
    tag = ciphertext[-16:]
    
    # Retourner en base64 pour stockage dans SQLite
    return (
        base64.b64encode(ct).decode(),
        base64.b64encode(iv).decode(),
        base64.b64encode(tag).decode()
    )

def decrypt_balance(balance_enc, balance_iv, balance_tag):
    """Déchiffre un solde stocké en base64."""
    # Décoder depuis base64
    ct = base64.b64decode(balance_enc)
    iv = base64.b64decode(balance_iv)
    tag = base64.b64decode(balance_tag)
    
    # Reconstituer le ciphertext complet
    aesgcm = AESGCM(BALANCE_KEY)
    plaintext = aesgcm.decrypt(iv, ct + tag, None)
    
    return float(plaintext.decode())