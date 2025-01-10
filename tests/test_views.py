from pathlib import Path
from tripstracking import db

def test_home(client, auth):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello" in response.data
    
    with client:
        auth.login()
        response = client.get("/")
        assert b'<div class="alert alert-info mt-3">Test User, login successful</div>' in response.data

def test_get_all_trips(client, auth):
    response = auth.login()
    assert response.status_code == 302

    data = {
        "destination": "Paris",
        "date": "01.01.2024",
        "description": "Away from averyone!",
        "budget": 3000,
    }

    client.post("/add_trip", data=data)

    response = client.get("/trips/")
    assert response.status_code == 200
    
def test_post_trip(client, auth):
    auth.login()
    data = {
        "destination": "Paris",
        "date": "01.01.2024",
        "description": "Away from averyone!",
        "budget": 3000,
    }

    response = client.post(
        "/add_trip", data=data)
    assert response.status_code == 302

    response = client.get("/trip/1/Paris")
    assert response.status_code == 200

def test_put_trip(client, auth, mocker):
    auth.login()
    response = client.get("/edit_trip/1/Paris")
    assert response.status_code == 302

    data = {
        "destination": "New York",
        "date": "02.01.2024",
        "description": "Business trip",
        "budget": 5000,
    }

    response = client.post('/edit_trip/1/Paris', data=data)
    assert response.status_code == 302

def test_delete_trip(client, auth):
    auth.login()
    response = client.get("/delete_trip/1/Paris")
    assert response.status_code == 200

    response = client.post("/delete_trip/1/Paris")
    assert response.status_code == 302

def test_get_all_expenses(client, auth):
    auth.login()

    data = {'trip_id': 1,
            'amount': 300,
            'expense_description': 'Dinner',
            'expense_date': '14.02.2025'
    }

    client.post("/trips/add_expense/1/Paris", data=data)

    response = client.get("/trips/expenses/1/Paris", data=data)
    assert response.status_code == 302

def test_post_expense(client, auth):
    auth.login()
    response = client.get("/trips/add_expense/1/Paris")
    assert response.status_code == 302
    data = {
        "trip_id": "1",
        "expense_date": "01.01.2024",
        "expense_description": "Dancing",
        "amount": 30,
    }
    response = client.post("/trips/add_expense/1/Paris", data=data, follow_redirects=False)
    assert response.status_code == 302

    redirect_url = response.headers.get("Location")
    assert redirect_url is not None
    assert redirect_url.startswith("/trips/")

    follow_response = client.get(redirect_url)
    assert follow_response.status_code == 302

    response = client.get("/trips/expenses/1/1/Paris", data=data)
    assert response.status_code == 302

def test_put_expense(client, auth):
    auth.login()
    response = client.get("/trips/edit_expense/1/1/Paris")
    assert response.status_code == 302

    data = {
        "trip_id": "1",
        "expense_date": "01.01.2024",
        "expense_description": "Dancing",
        "amount": 30,
    }

    response = client.post("/trips/edit_expense/1/1/Paris", data=data)
    assert response.status_code == 302

def test_delete_expence(client,auth):
    auth.login()
    response = client.get("/trips/delete_expense/1/1/Paris")
    assert response.status_code == 302

    response = client.post("/trips/delete_expense/1/1/Paris")
    assert response.status_code == 302
