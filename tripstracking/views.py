from flask import Blueprint, request, session, jsonify, current_app, g, redirect, url_for, render_template, flash
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os
import functools

views = Blueprint("views", __name__, template_folder='templates')

@views.route("/", methods=['GET'])
def home():
    return render_template('home.html')

def crud_trips(view):
    '''Ensures that only authenicated users can access any view function. Executes the view function if the user is authenticate, else returns a 401 error.'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        json_response = "application/json" in request.headers.get("accept", "")
        if g.user is None:
            message = "User is not logged in"
            if json_response:
                return jsonify({"message": message}), 401
            flash(message)
            return redirect(url_for('views.home'))
        
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

@views.route('/trips/', methods=['GET'])
@crud_trips
def get_all_trips():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    trips = db.execute(
        'SELECT trip_id, location, date, description, budget, timestamp FROM trip ORDER BY date DESC'
    ).fetchall()

    if not trips:
        if json_response:
            return jsonify({"error": "No trips found"}), 404
        message = "No trips found"
        flash(message)
        return redirect(url_for('views.post_trip'))
    
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

    if json_response:
        respond = {"trips": trips_list}
        return jsonify(respond), 200
    return render_template('trips.html', trips=trips_list)

@views.route('/trip/<int:trip_id>', methods=['GET'])
@crud_trips
def get_trip(trip_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    trip = db.execute(
        'SELECT trip_id, location, date, description, budget, timestamp FROM trip WHERE trip_id = ?', (trip_id,)
    ).fetchone()

    if trip is None:
        if json_response:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        error = "No trip found"
        flash(error)
        return redirect(url_for('views.get_trip'))
    
    trip_details = {
        "trip_id": escape(trip["trip_id"]),
        "location": escape(trip["location"]),
        "date": escape(trip["date"]),
        "description": escape(trip["description"]),
        "budget": escape(trip["budget"]),
        "timestamp": escape(trip["timestamp"])
    }
    
    if json_response:
        respond = {"trip": trip_details}
        return jsonify(respond), 200
    else:
        return render_template('trip.html', trip=trip_details)

@views.route('/add_trip', methods=['POST'])
@crud_trips
def post_trip():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    data = request.get_json()

    if not data:
        if json_response:
            error = "No data given"
            return jsonify({"error": error}), 400
        message = "Please, provide with trip details"
        flash(message)
        return redirect(url_for("views.post_trip"))

    location = data.get('location')
    date = data.get('date')
    description = data.get('description')
    budget = data.get('budget')

    if not location or not description:
        error = "location and description are required"
        if json_response:
            return jsonify({"error": error}), 400
        flash(error)
        return redirect(url_for("views.post_trip"))
    
    try:
        trip = db.execute(
            'INSERT INTO trip (location, date, description, budget) VALUES (?, ?, ?, ?)', (location, date, description, budget,)
        )

        db.commit()

        trip_id = trip.lastrowid

        trip_details = {"trip_id": trip_id,
                        "location": location,
                        "date": date,
                        "description": description,
                        "budget": budget}
        if json_response:
            response = {"message": "Trip created successfully!",
                        "trip": trip_details}
            return jsonify(response), 201
        else:
            flash("Trip created successfully!")
            return redirect(url_for('views.get_trip'))
    except Exception as e:
        if json_response:
            return jsonify({"error": f"Failed to create trip: {str(e)}"}), 500
        flash(f"{str(e)}")
        return render_template('trip.html')

@views.route('/edit_trip/<int:trip_id>', methods=['PUT'])
@crud_trips
def put_trip(trip_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    data = request.get_json()

    trip = db.execute(
        "SELECT trip_id, location, description, date, budget, timestamp FROM trip where trip_id = ?", (trip_id,)
    ).fetchone()

    if not trip:
        if json_response:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        message = "No trip found"
        flash(message)
        return redirect(url_for('views.put_trip'))

    location = data.get('location')
    date = data.get('date')
    description = data.get('description')
    budget = data.get('budget')

    if not location or not description:
        error = "The location and description of the trip are required"
        if json_response:
            return jsonify({"error": error}), 400
        flash(error)
        return redirect(url_for("views.put_trip"))
    
    db.execute(
        'UPDATE trip SET location = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (location, date, description, budget, trip_id,)
    )
    db.commit()

    trip_details = {"location": location,
                    "description": description,
                    "date": date,
                    "budget": budget
                }
    
    message = "Trip update successfully!"
    if json_response:
        response = {"message": message,
                    "trip": trip_details}
        return jsonify(response)
    else:
        flash(message)
        return render_template('trip.html', trip=trip_details)

@views.route('/delete_trip/<int:trip_id>', methods=['DELETE'])
@crud_trips
def delete_trip(trip_id):
    json_response = "application/json" in request.headers.get("accept", "")
    try:
        db = open_db()

        trip = db.execute(
            "SELECT * FROM trip WHERE trip_id = ?", (trip_id,)
        ).fetchone()
        
        if not trip:
            if json_response:
                return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
            message = "No trip found"
            flash(message)
            return redirect(url_for("views.delete_trip"))

        db.execute(
            "DELETE FROM trip WHERE trip_id = ?", (trip_id,)
        )

        db.commit()

        message = "Trip deleted successfully!"
        if json_response:
            return jsonify({"message": message}), 200
        flash(message)
        return redirect(url_for("views.get_trip"))
    
    except Exception as e:
        error = f"{str(e)}"
        if json_response:
            return jsonify({"error": error}), 500
        flash(error)
        return redirect(url_for("views.get_trip"))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/trips/photos/', methods=['GET'])
@crud_trips
def get_all_photos():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    
    photos = db.execute(
        'SELECT photo_id, file_path, timestamp FROM photos ORDER BY timestamp DESC'
    )
    
    if not photos:
        if json_response:
            return jsonify({"error": "No photos found"}), 400
        error = "No photos found"
        flash(error)
        return redirect(url_for('views.post_photo'))

    photos_list = []

    for photo in photos:
        photos_list.append({
            "photo_id" : escape(photo["photo_id"]),
            "file_path" : escape(photo["file_path"]),
            "timestamp" : escape(photo["timestamp"])
        })

    if json_response:
        response = {"photos": photos_list}
        return jsonify(response), 200
    return render_template('photos.html', photos=photos_list)

@views.route('/trips/photos/<int:photo_id>', methods=['GET'])
@crud_trips
def get_photo(photo_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    photo = db.execute(
        'SELECT photo_id, file_path, timestamp FROM photos where photo_id = ?', (photo_id,)
    )

    if photo is None:
        if json_response:
            return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404
        error = "No photo found"
        flash(error)
        return redirect(url_for('views.get_all_photos'))
    
    photo_details = {
            "photo_id": escape(photo["Photo_id"]),
            "file_path": escape(photo["file_path"]),
            "timestamp": escape(photo["timestamp"])
            }
    if json_response:
        response = {"photo": photo_details}
        return jsonify(response), 200
    return render_template('photo.html', photo=photo_details)

@views.route('/trips/add_photos', methods=['POST'])
@crud_trips
def post_photo():
    json_response = "application/json" in request.headers.get("accept", "")
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        db = open_db()

        if not file_path:
            if json_response:
                return jsonify({"error": "file path is required"}), 400
            flash("error: file path is required")
            return redirect(url_for('views.post_photo'))
        
        db.execute(
            'INSERT INTO photos (file_path) VALUES (?)', (file_path)
        )
        db.commit()

        if json_response:
            return jsonify({"message": "Photos uploaded successfully"}), 201
        flash("Photo uploaded successfully")
        return render_template('photo.html')
    if json_response:
        return jsonify({"error": "Invalid file type or no file found"}), 400
    flash("error: Invalid file type or no file found")
    return render_template('post_photo.html')

@views.route('/trips/delete_photo/<int_photo_id>', methods=['POST'])
@crud_trips
def delete_photo(photo_id):
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    photo = db.execute(
        'SELECT * FROM photos WHERE photo_id = ?', (photo_id,)
    )

    if not photo:
        if json_response:
            return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404
        flash("error: No photo found")
        return redirect(url_for('views.get_all_photos'))
    
    db.execute(
        'DELETE FROM photos WHERE photo_id = ?', (photo_id,)
    )

    db.commit()

    if json_response:
        return jsonify({"message": "Photo deleted successfully!"}), 200
    flash("Photo deleted successfully!")
    return redirect(url_for('views.get_all_photos'))

@views.route('/trips/expenses/', methods=['GET'])
@crud_trips
def get_all_expenses():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    expenses = db.execute(
        'SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expense ORDER BY amount DESC'
    ).fetchall()

    if not expenses:
        if json_response:
            return jsonify({"error": "No expenses found"}), 404
        flash("error: No expenses found")
        return redirect(url_for("views.post_expense"))
    
    all_expenses = []

    for expense in expenses:
        all_expenses.append({
            "expense_id": escape(expense["expense_id"]),
            "expense_description": escape(expense["expense_description"]),
            "expense_date": escape(expense["expense_date"]),
            "amount": escape(expense["amount"]),
            "timestamp": escape(expense["timestamp"])
        })

    if json_response:
        respond = {"expenses": all_expenses}
        return jsonify(respond), 200
    return render_template('expenses.htm', expenses=all_expenses)
    
@views.route('/trips/expenses/<int:expense_id>', methods=['GET'])
@crud_trips
def get_expense(expense_id=None):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    expense = db.execute(
        'SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expense WHERE expense_id = ?', (expense_id,)
    ).fetchone()

    if expense is None:
        if json_response:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        flash("error: No expense found")
        return redirect(url_for("views.get_all_expenses"))

    expense_details = {
        "expense_id": escape(expense["expense_id"]),
        "expense_description": escape(expense["expense_description"]),
        "expense_date": escape(expense["expense_date"]),
        "amount": escape(expense["amount"]),
        "timestamp": escape(expense["timestamp"])
    }
    if json_response:
        response = {"expense": expense_details}
        return jsonify(response), 200
    return render_template('expense.html', expense=expense_details)

@views.route('/trips/add_expense', methods=['POST'])
@crud_trips
def post_expense():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    data = request.get_json()

    if not data:
        if json_response:
            error = "No data given"
            return jsonify({"error": error}), 400
        flash("No data given")
        return redirect(url_for('views.post_expense'))
    
    expense_description = data.get('expense_description')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    
    if not amount:
        error = "Amount is required"
        if json_response: 
            return jsonify({"error": error}), 400
        flash(error)
        return redirect(url_for("views.post_expense"))
        
    try:
        expense = db.execute(
            "INSERT INTO expenses (expense_description, expense_date, amount) VALUES (?, ?, ?)", (expense_description, expense_date, amount)
        )
        db.commit()

        expense_id = expense.lastrowid

        expense_details = {"expense_description": expense_description,
                           "expense_date": expense_date,
                           "amount": amount,
                           "expense_id": expense_id}
        if json_response:
            response = {"message": "Expense created successfully!",
                            "expense": expense_details}
            return jsonify(response), 201
        flash("Expense created successfully!")
        return redirect(url_for('views.get_expense'))
    except Exception as e:
        if json_response:
            return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500
        flash(f"{str(e)}")
        return render_template('expense.html')

@views.route('/trips/edit_expense/<int:expense_id>', methods=['PUT'])
@crud_trips
def put_expenses(expense_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    data = request.get_json()

    expense = db.execute(
        "SELECT expense_id, expense_description, expense_date, amount, timestamp FROM expenses WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        if json_response:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        message = "No expense found"
        flash(message)
        return redirect(url_for('views.put_expense'))
    
    expense_description = data.get('expense_description')
    expense_date = data.get('expense_date')
    amount = data.get('amount')

    if not amount:
        error = "Amount is required"
        if json_response:
            return jsonify({"error": error}), 400
        flash(error)
        return redirect(url_for("views.put_expense"))
  
    db.execute(
        "UPDATE expense SET expense_description = ?, expense_date = ?, amount = ? WHERE expense_id = ?", (expense_description, expense_date, amount, expense_id)
    )

    db.commit()
    
    expense_details = {
                    "expense_description": expense_description,
                    "expense_date": expense_date,
                    "amount": amount
                }
    message = "Expense updated successfully!"
    if json_response:
        response = {"message": message,
                "expense": expense_details}
        return jsonify(response)
    flash(message)
    return render_template('expense.html', expense=expense_details)


@views.route('/trips/delete_expense/<int:expense_id>', methods=['DELETE'])
@crud_trips
def delete_expense(expense_id):
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    expense = db.execute(
        "SELECT * FROM expense WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        if json_response:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        message = "No expense found"
        flash(message)
        return redirect(url_for("views.delete_expense"))
    
    db.execute(
        "DELETE FROM expense WHERE expense_id = ?", (expense_id,)
    )

    db.commit()

    message = "Expense deleted successfully!"
    if json_response:
        return jsonify({"message": message}), 200
    flash(message)
    return redirect(url_for("views.get_all_expenses"))
