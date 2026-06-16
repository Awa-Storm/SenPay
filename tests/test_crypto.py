import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SENPAY_MASTER_KEY'] = 'unesuperclesecretede32characterss'

from app.crypto.aes import encrypt_balance, decrypt_balance
from app.crypto.pin import hash_pin, verify_pin

def test_encrypt_decrypt():
    """Chiffrer puis déchiffrer donne le même montant."""
    montant = 15000.0
    enc, iv, tag = encrypt_balance(montant)
    resultat = decrypt_balance(enc, iv, tag)
    assert resultat == montant

def test_iv_aleatoire():
    """Deux chiffrements du même montant donnent des IVs différents."""
    _, iv1, _ = encrypt_balance(15000.0)
    _, iv2, _ = encrypt_balance(15000.0)
    assert iv1 != iv2

def test_hash_pin():
    """Le hash bcrypt est différent du PIN original."""
    pin = "1234"
    hashed = hash_pin(pin)
    assert hashed != pin
    assert len(hashed) > 20

def test_verify_pin():
    """Le bon PIN est accepté, le mauvais est rejeté."""
    pin = "1234"
    hashed = hash_pin(pin)
    assert verify_pin("1234", hashed) == True
    assert verify_pin("9999", hashed) == False