# **TripsTracking: A trip application**

## **Introduction**

TripsTracking is a Flask-based web application designed to help travelers plan and manage their trips more effectively, while also enabling travel agents to enhance their services through a certalized trips managements system. 

This app allows users to record and organize key travel data, such as destinations, itineraries and expencies. The goal is to address a common challenge travlers face, having scattered travel details, by offering an all-in-one platform that supports better trip planning and decision-making. 

| Requirements                |
| ------------                |
| blinker >= 1.9.0            |
| click >= 8.1.7              |
| colorama >= 0.4.6           |
| dnspython >= 2.7.0          |
| email_validator >= 2.2.0    |
| Flask >= 3.1.0              |
| Flask-SQLAlchemy >= 3.1.1   |
| Flask-WTF >= 1.2.2          |
| greenlet >= 3.1.1           |
| idna >= 3.10                |
| niconfig >= 2.0.0           |
| itsdangerous >= 2.2.0       |
| Jinja2 >= 3.1.4             |
| MarkupSafe >= 3.0.2         |
| packaging >= 24.2           |
| pluggy >= 1.5.0             |
| pytest >= 8.3.3             |
| pytest-mock >= 3.14.0       |
| setuptools >= 75.6.0        |
| SQLAlchemy >= 2.0.36        |
| typing_extensions >= 4.12.2 |
| Werkzeug >= 3.1.3           |
| WTForms >= 3.2.1            |


## **Install** 

1. Clone the repository: **`git clone https://github.com/AngelikiMt/TripTracking.git`**
2. Create a virtual environment in PowerShell terminal and activate it:      

``` 
python -m venv .venv
.venv/Scripts/activate 
```

3. Install the Required packages: **`pip install -r requirements.txt`**
4. Creating the database: **`flask --app trips.py init-db`**
5. Run the project locally: **`flask --app trips.py run`**



