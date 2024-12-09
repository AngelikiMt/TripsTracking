import pytest
from tripstracking.__init__ import create_app
from tripstracking import db
import os
import tempfile

with open(os.path.join(os.path.dirname(__file__), 'test_schema.sql'), 'rb') as f:
    _test_schema_sql = f.read().decode('utf8')

@pytest.fixture()
def app():
    ''' Test configuration. '''
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": db_path
    })

    with app.app_context():
        db.init_db()
        db.open_db().executescript(_test_schema_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture()
def client(app):
    ''' Pass the configured app instance as an input in the tests. '''
    return app.test_client()

class AuthenticationActions(object):
    def __init__(self, client):
        self.client = client
    
    def login(self, username='Tester', password='securitypassword'):
        data = {'username': username,
                'password': password}
        return self.client.post("/users/login", data=data)
    
    def logout(self):
        return self.client.get('/users/logout')
    
    def delete(self):
        return self.client.get('/users/delete_user')

@pytest.fixture
def auth(client):
    return AuthenticationActions(client)