import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Clé maître depuis variable d'environnement (format hexadécimal, obligatoire)
MASTER_KEY_HEX = os.environ.get('SENPAY_MASTER_KEY')
if not MASTER_KEY_HEX:
    raise RuntimeError("SENPAY_MASTER_KEY n'est pas définie")
MASTER_KEY = bytes.fromhex(MASTER_KEY_HEX)

BALANCE_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-balance'
).derive(MASTER_KEY)

AUDIT_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-audit'
).derive(MASTER_KEY)