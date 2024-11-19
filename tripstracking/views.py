from flask import Blueprint, request, session, jsonify, current_app, g, redirect, url_for, render_template
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os
import functools

views = Blueprint("views", __name__)

def crud_trips(view):
    '''Ensures that only authenicated users can access any view function. Executes the view function if the user is authenticate, else returns a 401 error.'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"message": "User is not logged in"}), 401
        return view(**kwargs)
    return wrapped_view

@views.before_request
def user_info():
    db = open_db()
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()

@views.route('/trip/<trip_id>', methods=['GET'])
@crud_trips
def get_trip(trip_id=None):
    db = open_db()

    if trip_id is None:
        trips = db.execute(
            'SELECT trip_id, location, date, description, budget, timestamp FROM trip ORDER BY date DESC'
        ).fetchall()

        if not trips:
            return jsonify({"error": "No trips found"}), 404
        
        trips_list = []
        for trip in trips:
            trips_list.append({
                "trip_id": escape(trip["trip_id"]),
                "location": escape(trip["location"]),
                "date": escape(trip["date"]),
                "description": escape(trip["description"]),
                "budget": escape(trip["budget"]),
                "timestamp": escape(trip["timestamp"])
            })
        
        return jsonify({"trips": trips_list}), 200
    
    else:
        trip = db.execute(
            'SELECT trip_id, location, date, description, budget, timestamp FROM trip WHERE trip_id = ?', (trip_id,)
        ).fetchone()

        if trip is None:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        
        return jsonify({"message": {
            "trip_id": escape(trip["trip_id"]),
            "location": escape(trip["location"]),
            "date": escape(trip["date"]),
            "description": escape(trip["description"]),
            "budget": escape(trip["budget"]),
            "timestamp": escape(trip["timestamp"]),
        }}), 200

@views.route('/add_trip', methods=['POST'])
@crud_trips
def post_trip():
    db = open_db()
    data = request.get_json()

    if not data:
        error = "No data given"
        return jsonify({"error": error}), 400

    location = data.get('location')
    date = data.get('date')
    description = data.get('description')
    budget = data.get('budget')

    if not location or not description:
        error = "location and description are required"
        return jsonify({"error": error}), 400
    
    try:
        trip = db.execute(
            'INSERT INTO trip (location, date, description, budget) VALUES (?, ?, ?, ?)', (location, date, description, budget,)
        )

        db.commit()

        trip_id = trip.lastrowid

        response_data = {"message": "Trip was created successfully!",
                        "trip": {
                            "trip_id": trip_id,
                            "location": location,
                            "date": date,
                            "description": description,
                            "budget": budget}}
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create trip: {str(e)}"}), 500

@views.route('/edit_trip/<int:trip_id>', methods=['PUT'])
@crud_trips
def put_trip(trip_id):
    db = open_db()
    data = request.get_json()

    trip = db.execute(
        "SELECT trip_id, location, description, date, budget, timestamp FROM trip where trip_id = ?", (trip_id,)
    ).fetchone()

    if not trip:
        return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
    
    location = data.get('location')
    date = data.get('date')
    description = data.get('description')
    budget = data.get('budget')

    if not location or not description:
        return jsonify({"error": "Description and location of the trip are required"}), 400
    
    db.execute(
        'UPDATE trip SET location = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (location, date, description, budget, trip_id,)
    )
    db.commit()

    response = {"message": "Trip updated successfully!",
                "trip": {
                    "location": location,
                    "description": description,
                    "date": date,
                    "budget": budget
                }}
    
    return jsonify(response)

@views.route('/delete_trip/<int:trip_id>', methods=['DELETE'])
@crud_trips
def delete_trip(trip_id):
    try:
        db = open_db()

        trip = db.execute(
            "SELECT * FROM trip WHERE trip_id = ?", (trip_id,)
        ).fetchone()
        
        if not trip:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404

        db.execute(
            "DELETE FROM trip WHERE trip_id = ?", (trip_id,)
        )

        db.commit()

        return jsonify({"message": "Trip deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/trips/photos/<int:photo_id>', methods=['GET'])
@crud_trips
def get_photo(photo_id=None):
    db = open_db()
    
    if photo_id is None:
        photos = db.execute(
            'SELECT photo_id, file_path, timestamp FROM photos ORDER BY timestamp DESC'
        )
        
        if not photos:
            return jsonify({"error": "No photos found"}), 400

        photos_list = []

        for photo in photos:
            photos_list.append({
                "photo_id" : escape(photo["photo_id"]),
                "file_path" : escape(photo["file_path"]),
                "timestamp" : escape(photo["timestamp"])
            })

        return jsonify(photos_list), 200

    else:
        photo = db.execute(
            'SELECT photo_id, file_path, timestamp FROM photos where photo_id = ?', (photo_id,)
        )

        if photo is None:
            return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404

        return jsonify({
            "photo_id": escape(photo["Photo_id"]),
            "file_path": escape(photo["file_path"]),
            "timestamp": escape(photo["timestamp"])
            }), 200

@views.route('/trips/photos/post', methods=['POST'])
@crud_trips
def post_photo():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        db = open_db()

        if not file_path:
            return jsonify({"error": "file path is required"}), 400
        
        db.execute(
            'INSERT INTO photos (file_path) VALUES (?)', (file_path)
        )
        db.commit()

        return jsonify({"message": "Photos uploaded successfully"}), 201
    return jsonify({"error": "Invalid file type or no file found"}), 400


@views.route('/trips/photos/delete', methods=['POST'])
@crud_trips
def delete_photo(photo_id):
    db = open_db()

    photo = db.execute(
        'SELECT * FROM photos WHERE photo_id = ?', (photo_id,)
    )

    if not photo:
        return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404
    
    db.execute(
        'DELETE FROM photos WHERE photo_id = ?', (photo_id,)
    )

    db.commit()

    return jsonify({"message": "Photo deleted successfully!"}), 200


@views.route('/trips/expenses/<int:expense_id>', methods=['GET'])
@crud_trips
def get_expense(expense_id=None):
    db = open_db()

    if expense_id is None:
        expenses = db.execute(
            'SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expense ORDER BY amount DESC'
        ).fetchall()

        if not expenses:
            return jsonify({"error": "No expenses found"}), 404
        
        all_expenses = []

        for expense in expenses:
            all_expenses.append({
                "expense_id": escape(expense["expense_id"]),
                "expense_description": escape(expense["expense_description"]),
                "expense_date": escape(expense["expense_date"]),
                "amount": escape(expense["amount"]),
                "timestamp": escape(expense["timestamp"])
            })

        return jsonify(expenses), 200
    
    else:
        expense = db.execute(
            'SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expense WHERE expense_id = ?', (expense_id,)
        ).fetchone()

        if expense is None:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        
        return jsonify({
            "expense_id": escape(expense["expense_id"]),
            "expense_description": escape(expense["expense_description"]),
            "expense_date": escape(expense["expense_date"]),
            "amount": escape(expense["amount"]),
            "timestamp": escape(expense["timestamp"])
        }), 200


@views.route('/trips/expenses/post', methods=['POST'])
@crud_trips
def post_expense():
    db = open_db()
    data = request.get_json()

    if not data:
        error = "No data given"
        return jsonify({"error": error}), 400
    
    expense_description = data.get('expense_description')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    
    if not amount:
        error = "Amount is required"
        return jsonify({"error": error}), 400
    try:
        expense = db.execute(
            "INSERT INTO expenses (expense_description, expense_date, amount) VALUES (?, ?, ?)", (expense_description, expense_date, amount)
        )
        db.commit()

        expense_id = expense.lastrowid

        response_data = {"message": "Expense was created successfully!",
                            "expense": {
                            "expense_description": expense_description,
                            "expense_date": expense_date,
                            "amount": amount,
                            "expense_id": expense_id}}
        
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500


@views.route('/trips/expenses/editing/<int:photo_id>', methods=['PUT'])
@crud_trips
def put_expenses(expense_id):
    db = open_db()
    data = request.get_json()

    expense = db.execute(
        "SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expenses WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
    
    expense_description = data.get('expense_description')
    expense_date = data.get('expense_date')
    amount = data.get('amount')

    if not amount:
        return jsonify({"error": "Amount is required"}), 400
    
    db.execute(
        "UPDATE expense SET expense_description = ?, expense_date = ?, amount = ? WHERE expense_id = ?", (expense_description, expense_date, amount, expense_id)
    )

    db.commit()

    response = {"message": "Expense updated successfully!",
                "expense": {
                    "expense_description": expense_description,
                    "expense_date": expense_date,
                    "amount": amount
                }}

    return jsonify(response)


@views.route('/trips/expenses/delete', methods=['POST'])
@crud_trips
def delete_expense(expense_id):
    db = open_db()

    expense = db.execute(
        "SELECT * FROM expense WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
    
    db.execute(
        "DELETE FROM expense WHERE expense_id = ?", (expense_id,)
    )

    db.commit()

    return jsonify({"message": "Expense deleted successfully!"}), 200
