import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_key'
    with app.test_client() as client:
        yield client

def test_client_ne_peut_pas_acceder_audit(client):
    """Un utilisateur avec rôle 'client' doit recevoir 403."""
    with client.session_transaction() as sess:
        sess['user_id'] = 99
        sess['role'] = 'client'
    response = client.get('/admin/dashboard')
    assert response.status_code == 403

def test_admin_peut_acceder_dashboard(client):
    """Un utilisateur avec rôle 'admin' doit recevoir 200."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    response = client.get('/admin/dashboard')
    assert response.status_code == 200

def test_non_connecte_recoit_401(client):
    """Sans session, l'accès doit retourner 401."""
    response = client.get('/admin/dashboard')
    assert response.status_code == 401