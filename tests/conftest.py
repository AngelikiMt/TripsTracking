import os
import tempfile
import pytest
from tripstracking import create_app
from tripstracking.db import open_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'test_schema.sql'), 'rb') as f:
    _test_schema_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        open_db().executescript(_test_schema_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self.client = client
    
    def login(self, username='test', password = 'testpassword'):
        return self.client.post('/users/login', data={'username':username, 'password':password})
    def logout(self):
        return self.client.get('/users/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
    