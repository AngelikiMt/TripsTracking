# **TripsTracking: A trip application**

## **Introduction**

This repository contains the files used for generating the <ins>TripsTracking<ins> application.

TripsTracking is a Flask-based application that supports travelers creating custom trips or travel agents to level up their businesses and provide a trip app to their customers. This travel app allows the user to collect and record data such as trip destinations or expenses trackers for having all information gathered and making more easy decisions regarding their get aways.

TripsTracking is an application designed using: 
```
Python
RESTfull API
SQLite database
Pytest API testing
```

## **Installation** 
To install Project TripsTracking, follow these steps:

1. Clone the repository: **`git clone https://github.com/AngelikiMt/TripTracking.git`**
2. Navigate to the project directory: **`cd TripsTracking`**
3. Create a virtual environment and activate it. For using PowerShell:         ```python -m venv .venv
.venv/Scripts/activate```
4. Install the Required Python packages: **`pip install -r requirements.txt`**
5. run the project locally: **`flask --app trips.py run`**

## **Routes** 
<ins>Trips</ins>
1. Home page: "/"
2. All trips: "/trips/"
3. Check details of a trip: "/trip/trip_id/destination"
4. Add a trip: "/add_trip" 
5. Edit a trip: "/edit_trip/trip_id/destination"
6. Delete a trip: "/delete_trip/trip_id/destination"

<ins>Expenses</ins>
1. All expenses: "/trips/expenses/trip_id/destination"
2. Check details of an expense: "/trips/expenses/trip_id/expense_id/destination"
3. Add an expense: "/trips/add_expense/trip_id/destination"
4. Edit an expense: "/trips/edit_expense/trip_id/expense_id/destination"
5. Delete an expense: "/trips/delete_expense/trip_id/expense_id/destination"

<ins>User</ins>
1. Register user: "/register"
2. Login user: "/login"
3. Delete a user: "/delete_user"
4. Logout a user: "/logout"

## **Usage**

1. For creating the database run the following command in the terminal:
**`flask --app trips.py init-db`**
2. Use the provided routes to create and manage your trips and expenses.



