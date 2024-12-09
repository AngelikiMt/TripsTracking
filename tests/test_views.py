
from pathlib import Path
from tripstracking import db
from tests.conftest import app, auth

def test_home(client):
    response = client.get("/")
    assert response.data == b'Hello!'
    assert response.status_code == 200


def test_get_all_trips_json(client, auth):
    auth.login()
    response = client.get("/trips/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert "trips" in response.json

def test_get_all_trips_html(client, auth):
    auth.login()
    response = client.get("/trips/")
    assert response.status_code == 200
    assert b"<h2>Trips List</h2>" in response.data

def test_get_trip_json(client, auth):
    auth.login()
    response = client.get("/trip/1", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert "trip" in response.json

def test_get_trip_html(client, auth):
    auth.login()
    response = client.get("/trip/1")
    assert response.status_code == 200
    assert b"<h2>Trip Details</h2>" in response.data
    
def test_get_post_trip(client, auth):
    response = auth.login()
    assert response.status_code == 302
    response = client.get('/add_trip')
    assert response.status_code == 200
    assert b"Add a New Trip" in response.data

def test_post_post_trip(client, mocker, auth):
    auth.login()
    data = {
        "destination": "Paris",
        "date": "01.01.2024",
        "description": "Away from averyone!",
        "budget": 3000,
    }

    mock_db = mocker.patch(db.open_db)
    mock_db.return_value.execute.return_value.lastrowid = 1
    response = client.post('/add_trip', json=data, headers={"Accept": "application/json"})
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Trip creaded successfully!"
    assert json_data["trip"]["destination"] == data["destination"]

def test_post_post_trip_missing_fields(client, auth):
    auth.login()
    data = {
    "destination": "",
    "date": "01.01.2024",
    "description": "",
    "budget": 3000,
    }
    response = client.post('/add_trip', json=data, headers={"Accept": "application/json"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "destination and description are required"

def test_post_post_trip_no_data(client, auth):
    auth.login()
    response = client.post('/add_trip', json=None, headers={"Accept": "application/json"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No data given"

def test_post_trip_server_error(client, mocker, auth):
    auth.login()
    mock_db = mocker.patch(db.open_db)
    mock_db.return_value.execute.side_effect = Exception("Database error")

    data = {
    "destination": "",
    "date": "01.01.2024",
    "description": "",
    "budget": 3000,
    }

    response = client.post('/add_trip', json=data, headers={"Accept": "application/json"})

    assert response.status_code == 500
    json_data = response.get_json()
    assert "Failed to create trip" in json_data["error"]

def test_get_put_trip(client, auth):
    auth.login()
    response = client.get("/edit_trip/1")
    assert response.status_code == 200
    assert b'Edit Trip' in response.data

def test_post_put_trip(client, auth, mocker):
    auth.login()
    data = {
        "destination": "New York",
        "date": "02.01.2024",
        "description": "Business trip",
        "budget": 5000,
    }

    mock_db = mocker.patch(db.open_db)
    mock_db.return_value.execute.side_effect = Exception("Database error")

    response = client.post('/edit_trip/1', json=data, headers={"Accept": "application/json"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Trip updated successfully!"
    assert json_data["trip"]["destination"] == data["destination"]



resources = Path(__file__).parent/"resources"
def test_get_all_photos(client, auth):
    auth.login()
    response = client.get("/trips/photos/")
    assert response.status_code == 200

def test_get_photo(client, auth):
    auth.login()
    response = client.get("/trips/photos/1")
    assert response.status_code == 200   

def test_post_photo(client, auth):
    auth.login()
    response = client.get("/trips/add_photos")
    assert response.status_code == 200
    res = client.post("/trips/add_photos", data={"file_path": (resources/ "picture.png".open("rb")),})
    assert res.status == 200


def test_get_all_expenses_json(client, auth):
    auth.login()
    response = client.get("/trips/expenses/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert "expenses" in response.json

def test_get_all_expenses_html(client, auth):
    auth.login()
    response = client.get("/trips/expenses/")
    assert response.status_code == 200
    assert b"<h2>All Expenses</h2>" in response.data

def test_get_expense_json(client, auth):
    auth.login()
    response = client.get("/trips/expenses/1", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert "expense" in response.json

def test_get_expense_html(client, auth):
    auth.login()
    response = client.get("/trips/expenses/1")
    assert response.status_code == 200
    assert b"<h2>Expense Details</h2>" in response.data

def test_get_post_expense(client, auth):
    auth.login()
    response = client.get("/trips/add_expense")
    assert response.status_code == 200

def test_post_post_expense(client, auth):
    auth.login()
    data = {
        "trip_id": "1",
        "expense_date": "01.01.2024",
        "expense_description": "Dancing",
        "amount": 30,
    }
    response = client.post("/trips/add_expense", json=data, follow_redirects=False)
    assert response.status_code == 302

    redirect_url = response.headers.get("Location")
    assert redirect_url is not None
    assert redirect_url.startswith("/trips/expenses/")

    follow_response = client.get(redirect_url)
    assert follow_response.status_code == 200
    assert "Dancing" in follow_response.get_data(as_text=True)

def test_put_expense(client, auth):
    auth.login()
    response = client.get("/trips/edit_expense/1")
    assert response.status_code == 200
