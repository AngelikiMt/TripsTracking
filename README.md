# **TripsTracking: A trip application** :desert_island:

## **Table of Contents** :bookmark:
- [Introduction](#introduction)
- [Installation](#installation-seedling)
- [Routes And How It Works](#routes-and-how-it-works-computer)
- [Usage](#usage-world_map)
- [Contributing](#contributing-handshake)
- [License](#license-page_with_curl)
- [Author](#author-woman_technologist)

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

## **Installation** :seedling:
To install Project TripsTracking, follow these steps:

1. Clone the repository: **`git clone https://github.com/AngelikiMt/TripTracking.git`**
2. Navigate to the project directory: **`cd TripsTracking`**
3. Create a virtual environment and activate it. For using PowerShell:         ```python -m venv .venv
.venv/Scripts/activate```
4. Install the Required Python packages: **`pip install -r requirements.txt`**
5. run the project locally: **`flask --app trips.py run`**

## **Routes And How It Works** :computer:
**Views.py **
<ins>Trips</ins>
1. Home page, methods='GET': "/"
    - ![Homepage with a 'Please log in to access and manage your trips' message](/README_photos/homepage.png)

2. Get all trips, methods='GET': "/trips/"
    - ![Get all trips page.](/README_photos/get_all_trips.png)

3. Get a trip, methods='GET': "/trip/<int:trip_id>"
    - ![Get a trip page.](/README_photos/get_trip.png)

4. Post a trip, methods='GET, POST': "/add_trip" 
    - The post-a-trip page appears when: 
        - A user tries to retrieve all trips but no trips are posted yet. Then a 'No trips found' message flashes and redirects the user to the '/add_trip/ URL. 
        ![Post-a-trip page](/README_photos/get_trips_no_trip_found_redirect_add_trip.png) 
        - A user wants to add a trip by pressing the 'add a trip' button, which redirects to the same URL. 

    - After creating a trip, the app flashes a successful creation message and redirects the user to the '/add_trip' URL. 
    ![Trip created successfully message redirected to '/add_trip'.](/README_photos/trip_created_successfully_message_redirect_add_trip.png)

5. Put a trip, methods='GET, POST': "/edit_trip/<int:trip_id>"
    - ![Edit trip page](/README_photos/put_trip.png)
    - After updating a trip, the app redirects the user to the "/trips/<int:trip_id>" URL with a 'trip updated successfully!' flashed message.
    ![Trip updated successfully message redirect to ](/README_photos/trip_updated_successfully_message_redirect_get_trip.png)

6. Delete a trip, methods='GET, POST': "/delete_trip/<int:trip_id>"
    - Both the 'Cancel' and the 'Delete Trip' buttons are redirecting the user to the '/trips/' URL to GET all trips. 
    ![Delete a trip](/README_photos/delete_trip.png)

<ins>Expenses</ins>
1. Get all expenses, methods='GET': "/trips/expenses/<int:trip_id>"
    - ![Get all expenses page.](/README_photos/get_all_expenses.png)

2. Get an expense, methods='GET': "/trips/expenses/<int:trip_id>/<int:expense_id>"
    - ![Get-an-expense page.](/README_photos/get_expense.png)

3. Post an expense, methods='GET, POST': "/trips/add_expense/<int:trip_id>/"
    - The post-an-expense page appears when: 
        - A user tries to retrieve all expenses but no expenses are posted yet. Then a 'No expenses found' message flashes and redirects the user to the '/trips/add_expense/<int:trip_id>/' URL. 
        ![Post-an-expense page](/README_photos/get_expenses_no%20expense_found_redirect_add_expense.png)
        - A user wants to add an expense by pressing the 'add an expense' button, which redirects to the same URL. 

    - After creating an expense, the app flashes a successful creation message and redirects the user to the "/trips/add_expense/<int:trip_id>/" URL. 
    ![Trip created successfully message redirected to the '/add_trip' URL.](/README_photos/expense_successfully_created_redirect_add_expense.png)

4. Put an expense, methods='GET, POST': "/trips/edit_expense/<int:trip_id>/<int:expense_id>/"
    - After updating an expense, the app redirects the user to the "/trips/expenses/<int:trip_id>/<int:expense_id>" URL with an 'expense updated successfully!' flashed message. 
    ![Edit an expense](/README_photos/expense_updated_seccessfully_message_redirect_get_expense.png)

5. Delete an expense, methods='GET, POST': "/trips/delete_expense/<int:trip_id>/<int:expense_id>/"
    - Both the 'Cancel' and the 'Delete Expense' buttons are redirecting the user to the "/trips/expenses/<int:trip_id>" URL to GET all expenses.  
    ![Delete an expense](/README_photos/delete_expense.png)

**Auth.py""
1. Register a user, methods='GET, POST': "/register"
    - ![Register a user form](/README_photos/registration_form.png)

2. Login a user, methods='GET, POST': "/login"
    - When an invalid username or password an error is flashed and the user redirects to the login page. 
    ![Login page with 'Invalid password' message](/README_photos/invalid_password_login.png)

    - When a user logs in successfully, a success message flashes. The app redirects the user to the homepage and greets the user using the username. 
    ![homepage with 'fullname, login successful' flashed message.](/README_photos/login_successfull_message_home_page.png)

3. Delete a user, methods='GET, POST': "/delete_user"
    - When a user is deleted, the app redirects to the registration form. 
    ![Delete a user](/README_photos/delete_user.png)

4. Logout a user, methods='GET, POST': "/logout"
    - ![logout page](/README_photos/logout.png)
    - When the user logs out of the app, it redirects to the login page with a 'logout successfully' message. 
    ![Login page and 'logout successgully' message](/README_photos/logout_message_redirect_login.png)

## **Usage** :world_map:

1. This project is not for commersial use. 

2. For creating the database run the following command in the terminal:
**`flask --app trips.py init-db`**

3. Use the provided routes to create and manage destinations and expenses.

## **Contributing** :handshake:

If you would like to contribute to Project TripsTracking, here are some guidelines:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes at your branch
4. Write tests to cover your changes
5. Run tests to ensure they pass
6. Commit your changes
7. Push your changes to your forked repository
8. Submit the pull request

## **License** :page_with_curl:


## **Author** :woman_technologist:

Project TripsTracking was created by **[Angeliki Matta](https://github.com/AngelikiMt)**


