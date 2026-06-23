import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.crypto.keys import BALANCE_KEY

def encrypt_balance(amount_fcfa):
    iv = os.urandom(12)
    aesgcm = AESGCM(BALANCE_KEY)
    ciphertext = aesgcm.encrypt(iv, str(amount_fcfa).encode(), None)
    ct = ciphertext[:-16]
    tag = ciphertext[-16:]
    return (
        base64.b64encode(ct).decode(),
        base64.b64encode(iv).decode(),
        base64.b64encode(tag).decode()
    )

def decrypt_balance(balance_enc, balance_iv, balance_tag):
    # Si le solde est vide ou None, retourner 0.0
    if not balance_enc or not balance_iv or not balance_tag:
        return 0.0

    try:
        ct = base64.b64decode(balance_enc)
        iv = base64.b64decode(balance_iv)
        tag = base64.b64decode(balance_tag)
        aesgcm = AESGCM(BALANCE_KEY)
        plaintext = aesgcm.decrypt(iv, ct + tag, None)
        return float(plaintext.decode())
    except Exception:
        return 0.0
