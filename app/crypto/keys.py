import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Clé maître depuis variable d'environnement (format hexadécimal)
MASTER_KEY_HEX = os.environ.get('SENPAY_MASTER_KEY', '7228a50ffb3ee0abb0c80b73f4fa3f792949b93261833099825ae08872fe8608')
MASTER_KEY = bytes.fromhex(MASTER_KEY_HEX)

# Dérivation de la clé pour les soldes (AES-256-GCM)
BALANCE_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-balance'
).derive(MASTER_KEY)

# Dérivation de la clé pour l'audit (HMAC)
AUDIT_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-audit'
).derive(MASTER_KEY)
