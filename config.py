import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_123456')
    MASTER_KEY = os.environ.get('SENPAY_MASTER_KEY')
    DB_PATH = os.environ.get('DB_PATH', 'senpay.db')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 60  # 60 secondes pour le test

if not Config.MASTER_KEY:
    raise RuntimeError(
        "SENPAY_MASTER_KEY manquante. Vérifie que le fichier .env existe "
        "et contient SENPAY_MASTER_KEY=<clé hexadécimale>."
    )
