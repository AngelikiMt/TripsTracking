from flask import Blueprint, request, session, jsonify, current_app, g, redirect, url_for, render_template, flash
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os
import functools
from .static import forms

views = Blueprint("views", __name__, template_folder='templates')

@views.route("/", methods=['GET'])
def home():
    username = None
    if g.user:
        username = g.user['username']
    return render_template('home.html', username=username)

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

@views.before_request
def method_override():
    if '_method' in request.form:
        request.environ['REQUEST_METHOD'] = request.form['_method']

@views.route('/trips/', methods=['GET'])
@crud_trips
def get_all_trips():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    trips = db.execute(
        'SELECT trip_id, destination, date, description, budget, created FROM trip ORDER BY date DESC'
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
            "destination": escape(trip["destination"]),
            "date": escape(trip["date"]),
            "description": escape(trip["description"]),
            "budget": escape(trip["budget"]),
            "created": escape(trip["created"])
        })

    if json_response:
        respond = {"trips": trips_list}
        return jsonify(respond), 200
    return render_template('trips/trips.html', trips=trips_list)

@views.route('/trip/<int:trip_id>', methods=['GET'])
@crud_trips
def get_trip(trip_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    trip = db.execute(
        'SELECT trip_id, destination, date, description, budget, created FROM trip WHERE trip_id = ?', (trip_id,)
    ).fetchone()

    if trip is None:
        if json_response:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        flash("No trip found")
        return redirect(url_for('views.get_all_trips'))
    
    trip_details = {
        "trip_id": escape(trip["trip_id"]),
        "destination": escape(trip["destination"]),
        "date": escape(trip["date"]),
        "description": escape(trip["description"]),
        "budget": escape(trip["budget"]),
        "created": escape(trip["created"])
    }
    
    if json_response:
        return jsonify({"trip": trip_details}), 200
    return render_template('trips/trip.html', trip=trip_details, trip_id=trip_id)

@views.route('/add_trip', methods=['GET', 'POST'])
@crud_trips
def post_trip():
    form = forms.AddTripForm(request.form)
    if request.method == 'POST':
        db = open_db()
        json_response = "application/json" in request.headers.get("accept", "")
        if json_response:
            data = request.get_json()
        else:
            data = request.form

        error = None

        if not data:
            if json_response:
                return jsonify({"error": "No data given"}), 400
            return redirect(url_for("views.post_trip"))

        destination = data.get('destination')
        date = data.get('date')
        description = data.get('description')
        budget = data.get('budget')

        if not destination or not description:
            if json_response:
                return jsonify({"error": "destination and description are required"}), 400
            return redirect(url_for("views.post_trip"))
        
        if error is None:
            try:
                trip = db.execute(
                    'INSERT INTO trip (destination, date, description, budget) VALUES (?, ?, ?, ?)', (destination, date, description, budget,)
                )

                db.commit()

                trip_id = trip.lastrowid

                trip_details = {
                                "trip_id": trip_id,
                                "destination": destination,
                                "date": date,
                                "description": description,
                                "budget": budget}
                if json_response:
                    response = {"message": "Trip created successfully!",
                                "trip": trip_details}
                    return jsonify(response), 201  
                return redirect(url_for('views.get_trip'), trip=trip_details, trip_id=trip_id)
            except Exception as e:
                if json_response:
                    return jsonify({"error": f"Failed to create trip: {str(e)}"}), 500
                return redirect(url_for("views.post_trip"))
    return render_template('trips/post_trip.html')

@views.route('/edit_trip/<int:trip_id>', methods=['GET', 'POST'])
@crud_trips
def put_trip(trip_id):
    form = forms.PutTripForm(request.form)
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    trip = db.execute(
        "SELECT trip_id, destination, description, date, budget FROM trip WHERE trip_id = ?", (trip_id,)
    ).fetchone()

    if not trip:
        if json_response:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        flash("No trip found")
        return redirect(url_for('views.get_all_trips'))

    if request.method == 'POST':
        if json_response:
            data = request.get_json()
        else:
            data = request.form

        destination = data.get('destination')
        date = data.get('date')
        description = data.get('description')
        budget = data.get('budget')

        if not destination or not description:
            error = "Both destination and description are required."
            if json_response:
                return jsonify({"error": error}), 400
            flash(error)
            return redirect(url_for("views.put_trip", trip_id=trip_id))
    
        try: 
            db.execute(
                'UPDATE trip SET destination = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (destination, date, description, budget, trip_id,)
            )
            db.commit()

            updated_trip = {
                "trip_id": trip_id,
                "destination": destination,
                "description": description,
                "date": date,
                "budget": budget
            }
            
            message = "Trip updated successfully!"
            if json_response:
                response = {"message": message,
                            "trip": updated_trip}
                return jsonify(response), 200
            flash(message)
            return render_template('trips/trip.html', trip=updated_trip, trip_id=trip_id)
        except Exception as e:
            error = f"Failed to update trip: {str(e)}"
            if json_response:
                return jsonify({"error": error}), 500
            flash(error)
            return render_template("trips/trip.html", trip_id=trip_id)
    return render_template('trips/put_trip.html', trip=trip, trip_id=trip_id, form=form)

@views.route('/delete_trip/<int:trip_id>', methods=['GET', 'POST'])
@crud_trips
def delete_trip(trip_id):
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    trip = db.execute(
            "SELECT * FROM trip WHERE trip_id = ?", (trip_id,)
        ).fetchone()
        
    if request.method == 'POST':
        try:
            db.execute(
                "DELETE FROM trip WHERE trip_id = ?", (trip_id,)
            )
            db.commit()

            message = "Trip deleted successfully!"
            if json_response:
                return jsonify({"message": message}), 200
            flash(message)
            return redirect(url_for("views.get_all_trips"))
        
        except Exception as e:
            error = f"Failed to delete trip: {str(e)}"
            if json_response:
                return jsonify({"error": error}), 500
            flash(error)
            return render_template('trips/delete_trip.html', error=error)
    return render_template('trips/delete_trip.html', trip_id=trip_id, trip=trip)

@views.route('/trips/expenses/', methods=['GET'])
@crud_trips
def get_all_expenses():
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    expenses = db.execute(
        'SELECT expense_id, expense_description, expense_date, amount, created FROM expense ORDER BY amount DESC'
    ).fetchall()

    if not expenses:
        error = "No expenses found"
        if json_response:
            return jsonify({"error": error}), 404
        flash(error)
        return redirect(url_for("views.post_expense"))
    
    all_expenses = []

    for expense in expenses:
        all_expenses.append({
            "expense_id": escape(expense["expense_id"]),
            "expense_description": escape(expense["expense_description"]),
            "expense_date": escape(expense["expense_date"]),
            "amount": escape(expense["amount"]),
            "created": escape(expense["created"]),
        })
    expense_id = expense["expense_id"]
    if json_response:
        respond = {"expenses": all_expenses}
        return jsonify(respond), 200
    return render_template('expenses/expenses.html', expenses=all_expenses, expense_id=expense_id)
    
@views.route('/trips/expenses/<int:expense_id>', methods=['GET'])
@crud_trips
def get_expense(expense_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")

    expense = db.execute(
        'SELECT expense_id, expense_description, expense_date, amount, created FROM expense WHERE expense_id = ?', (expense_id,)
    ).fetchone()

    if expense is None:
        if json_response:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        flash("No expense found")
        return redirect(url_for("views.get_all_expenses"))

    expense_details = {
        "expense_id": escape(expense["expense_id"]),
        "expense_description": escape(expense["expense_description"]),
        "expense_date": escape(expense["expense_date"]),
        "amount": escape(expense["amount"]),
        "created": escape(expense["created"])
    }
    if json_response:
        response = {"expense": expense_details}
        return jsonify(response), 200
    return render_template('expenses/expense.html', expense=expense_details, expense_id=expense_id)

@views.route('/trips/add_expense', methods=['GET', 'POST'])
@crud_trips
def post_expense():
    if request.method == 'POST':
        db = open_db()
        json_response = "application/json" in request.headers.get("accept", "")
        if json_response:
            data = request.get_json()
        else:
            data = request.form
        error = None

        if not data:
            error = "No data given"
            if json_response:
                return jsonify({"error": error}), 400
            flash(error)
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
        if error is None:     
            try:
                expense = db.execute(
                    "INSERT INTO expense (expense_description, expense_date, amount) VALUES (?, ?, ?)", (expense_description, expense_date, amount)
                )
                db.commit()

                expense_id = expense.lastrowid

                expense_details = {"expense_description": expense_description,
                                "expense_date": expense_date,
                                "amount": amount,
                                "expense_id": expense_id}
                message = "Expense created successfully!"
                if json_response:
                    response = {"message": message,
                                    "expense": expense_details}
                    return jsonify(response), 201
                flash(message)
                return redirect(url_for('views.get_expense'), expense=expense_details, expense_id=expense_id)
            except Exception as e:
                if json_response:
                    return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500
                flash(f"{str(e)}")
                return render_template('expenses/post_expense.html')
    return render_template('expenses/post_expense.html')

@views.route('/trips/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@crud_trips
def put_expense(expense_id):
    db = open_db()
    json_response = "application/json" in request.headers.get("accept", "")
    
    expense = db.execute(
        "SELECT expense_id, trip_id, expense_description, expense_date, amount, created FROM expense WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        if json_response:
            return jsonify({"error": f"Expense with expense id {expense_id} not found"}), 404
        flash("No expense found")
        return redirect(url_for('views.put_expense'))
    
    if request.method == 'POST':
        if json_response:
            data = request.get_json()
        else:
            data = request.form

        expense_description = data.get('expense_description')
        trip_id = data.get('trip_id')
        expense_date = data.get('expense_date')
        amount = data.get('amount')

        if not amount:
            error = "Amount is required"
            if json_response:
                return jsonify({"error": error}), 400
            flash(error)
            return redirect(url_for("views.put_expense", expense_id=expense_id))
        try:
            db.execute(
                "UPDATE expense SET trip_id = ?, expense_description = ?, expense_date = ?, amount = ? WHERE expense_id = ?", (trip_id, expense_description, expense_date, amount, expense_id)
            )
            db.commit()
            
            updated_expense = {
                            "expense_id": expense_id,
                            "trip_id": trip_id,
                            "expense_description": expense_description,
                            "expense_date": expense_date,
                            "amount": amount
                        }
            
            message = "Expense updated successfully!"
            if json_response:
                response = {"message": message,
                        "expense": updated_expense}
                return jsonify(response), 200
            flash(message)
            return render_template('expenses/expense.html', expense=updated_expense, expense_id=expense_id)
        except Exception as e:
            error = f"Failed to update expense: {str(e)}"
            if json_response:
                return jsonify({"error": error}), 500
            flash(error)
            return render_template("expenses/expense.html", expense_id=expense_id)
    return render_template('expenses/put_expense.html', expense=expense, expense_id=expense_id)

@views.route('/trips/delete_expense/<int:expense_id>', methods=['GET', 'POST'])
@crud_trips
def delete_expense(expense_id):
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    expense = db.execute(
        "SELECT * FROM expense WHERE expense_id = ?", (expense_id,)
    ).fetchone()

    if request.method == 'POST':
        try:
            db.execute(
                "DELETE FROM expense WHERE expense_id = ?", (expense_id,)
            )
            db.commit()

            message = "Expense deleted successfully!"
            if json_response:
                return jsonify({"message": message}), 200
            flash(message)
            return redirect(url_for("views.get_all_expenses"))
        
        except Exception as e:
            error = f"Failed to delete expense: {str(e)}"
            if json_response:
                return jsonify({"error": error}), 500
            flash(error)
            return render_template('expenses/delete_expense.html', error=error)
    return render_template('expenses/delete_expense.html', expense_id=expense_id, expense=expense)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/trips/photos/', methods=['GET'])
@crud_trips
def get_all_photos():
    db = open_db()
    
    photos = db.execute(
        'SELECT photo_id, file_path, created FROM photo ORDER BY created DESC'
    ).fetchall()
    
    if not photos:
        flash("No photos found")
        return redirect(url_for('views.post_photo'))

    photos_list = []

    for photo in photos:
        photos_list.append({
            "photo_id" : escape(photo["photo_id"]),
            "file_path" : escape(photo["file_path"]),
            "created" : escape(photo["created"])
        })

    return render_template('photos.html', photos=photos_list)

@views.route('/trips/photos/<int:photo_id>', methods=['GET'])
@crud_trips
def get_photo(photo_id):
    db = open_db()

    photo = db.execute(
        'SELECT photo_id, file_path, created FROM photo where photo_id = ?', (photo_id,)
    ).fetchone()

    if photo is None:
        flash("No photo found")
        return redirect(url_for('views.get_all_photos'))
    
    photo_details = {
            "photo_id": escape(photo["Photo_id"]),
            "file_path": escape(photo["file_path"]),
            "created": escape(photo["created"])
            }

    return render_template('photo.html', photo=photo_details)

@views.route('/trips/add_photos', methods=['GET', 'POST'])
@crud_trips
def post_photo():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            db = open_db()

            if not file_path:
                flash("file path is required")
                return redirect(url_for('views.post_photo'))
            
            db.execute(
                'INSERT INTO photo (file_path) VALUES (?)', (file_path)
            )
            db.commit()

            flash("Photos uploaded successfully")
            return render_template('photos/photo.html', file_path=file_path)
        flash("Invalid file type or no file found")
        return redirect(url_for('views.post_photo'))
    return render_template('photos/post_photo.html')

@views.route('/trips/delete_photo/<int_photo_id>', methods=['POST'])
@crud_trips
def delete_photo(photo_id):
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    photo = db.execute(
        'SELECT * FROM photo WHERE photo_id = ?', (photo_id,)
    )

    if not photo:
        if json_response:
            return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404
        flash("No photo found")
        return redirect(url_for('views.get_all_photos'))
    
    db.execute(
        'DELETE FROM photo WHERE photo_id = ?', (photo_id,)
    )

    db.commit()

    message = "Photo deleted successfully!"
    if json_response:
        return jsonify({"message": message}), 200
    flash(message)
    return redirect(url_for('views.get_all_photos'))

