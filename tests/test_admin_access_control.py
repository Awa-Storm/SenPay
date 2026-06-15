import os
import pytest
from app import create_app

@pytest.fixture
def client():
    # Clés lues depuis l'environnement 
    os.environ.setdefault('SECRET_KEY', os.urandom(32).hex())
    os.environ.setdefault('SENPAY_KEY', 'a' * 64)  # réservé aux tests

    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_client_ne_peut_pas_acceder_audit(client):
    """OS-06 : rôle 'client' → 403 Forbidden sur /admin/dashboard"""
    with client.session_transaction() as sess:
        sess['user_id'] = 99
        sess['role'] = 'client'
    response = client.get('/admin/dashboard')
    assert response.status_code == 403


def test_admin_peut_acceder_dashboard(client):
    """EF08 : rôle 'admin' → 200 OK sur /admin/dashboard"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/dashboard')
    assert response.status_code == 200


def test_non_connecte_recoit_401(client):
    """OS-01 : sans session active → 401 Unauthorized"""
    response = client.get('/admin/dashboard')
    assert response.status_code == 401
