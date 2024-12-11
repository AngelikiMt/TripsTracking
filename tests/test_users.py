from tests.conftest import client
from flask import session
from tests.conftest import app, auth
from tripstracking import db

def test_get_register_user_json(client):
    response = client.get("/users/register", headers={"Accept": "application/json"})
    assert response.status_code == 200
    
def test_get_register_user_html(client):
    response = client.get("/users/register")
    assert response.status_code == 200

def test_post_register_user(client):
    data = {
        "username": "Tester",
        "password": "securitypassword",
        "fullname": "Tester User",
        "email": "testerUser@mailexample.com"
    }
    response = client.post("/users/register", json=data)
    assert response.status_code == 200

def test_get_login_user_json(client):
    response = client.get("/users/login", headers={"Accept": "application/json"})
    assert response.status_code == 200

def test_post_login_user(client, auth):
    assert client.get("/users/login").status_code == 200
    response = auth.login()
    
    with client:
        response = client.get('/')
        assert response.status_code == 200

def test_logout_user(client, auth):
    auth.login()

    with client:
        response = auth.logout()
        assert response.status_code == 200
        assert 'user_id' not in session

def test_delete_user(client, auth):
    response = auth.login()
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert 'user_id' in session
        assert session['user_id'] == 1  # Ensure the session user_id matches

    # Attempt to delete the user
    response = auth.delete()
    assert response.status_code == 200

    # Confirm user session is cleared
    with client.session_transaction() as session:
        assert 'user_id' not in session
        assert b"User deleted successfully!" in response.data
