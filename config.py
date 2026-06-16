import os

# Variables directement accessibles par import
SECRET_KEY  = os.environ.get('SECRET_KEY', 'fallback_dev_key') 