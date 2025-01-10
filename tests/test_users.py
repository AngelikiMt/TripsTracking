from flask import g, session
from tripstracking.db import open_db


def test_register(client, app):
    assert client.get('/users/register').status_code == 200
    response = client.post(
        'users/register', data={'username': 'tester', 'password': 'testpassword', 'fullname': 'Test User', 'email': 'test@example.com'}
    )
    assert response.headers["Location"] == "/users/login"

    with app.app_context():
        assert open_db().execute(
            "SELECT * FROM user WHERE username = 'tester'",
        ).fetchone() is not None
    
def test_login(client, auth):
    assert client.get('/users/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

def test_logout(client, auth):
    auth.login()

    with client:
        client.get('/')
        assert 'user_id' in session
        auth.logout()
        assert 'user_id' not in session

def test_delete_user(client, auth):
    auth.login()

    with client:
        assert client.get('/users/delete_user').status_code == 200

