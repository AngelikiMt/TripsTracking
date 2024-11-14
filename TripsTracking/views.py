from flask import Blueprint, request, session, jsonify, current_app, g
from flask_restful import Api, Resource
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
from datetime import datetime
import os

views = Blueprint("views", __name__)
api = Api(views)

@views.before_request
def users_info():
    db = open_db()
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()


@views.route('/trip/<trip_id>', methods=['GET'])
def get(trip_id=None):
    db = open_db()

    if trip_id is None:
        trips = db.execute(
            'SELECT trip_id, destination, date, description, budget, timestamp FROM trips ORDER BY date DESC'
        ).fetchall()

        if not trips:
            return jsonify({"error": "No trips found"}), 404
        
        trips_list = []
        for trip in trips:
            trips_list.append({
                "trip_id": escape(trip["trip_id"]),
                "destination": escape(trip["destination"]),
                "date": escape(trip["date"]),
                "description": escape(trip["description"]),
                "budget": escape(trip["budget"]),
                "timestamp": escape(trip["timestamp"])
            })
        
        return jsonify({"trips": trips_list}), 200
    
    else:
        trip = db.execute(
            'SELECT trip_id, destination, date, description, budget, timestamp FROM trips WHERE trip_id = ?', (trip_id,)
        ).fetchone()

        if trip is None:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        
        return jsonify({"message": {
            "trip_id": escape(trip["trip_id"]),
            "destination": escape(trip["destination"]),
            "date": escape(trip["date"]),
            "description": escape(trip["description"]),
            "budget": escape(trip["budget"]),
            "timestamp": escape(trip["timestamp"]),
        }}), 200

@views.route('/add_trip', methods=['POST'])
def post():
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
            'INSERT INTO trips (location, date, description, budget) VALUES (?, ?, ?, ?)', (location, date, description, budget,)
        )
        db.commit()
        trip_id = trip['trip_id']

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

@views.route('/edit_trip', methods=['PUT'])
def put(trip_id):
    db = open_db()
    data = request.get_json()

    # Fetch the specific trip for editing
    trip = db.execute(
        "SELECT trip_id, destination, description, date, budget, timestamp FROM trip where trip_id = ?", (trip_id,)
    ).fetchone()

    if not trip:
        return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
    
    destination = data.get('destination')
    date = data.get('date')
    description = data.get('description')
    budget = data.get('budget')

    if not destination or not description:
        return jsonify({"error": "Description and destination of the trip are required"}), 400
    
    db.execute(
        'UPDATE trips SET destination = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (destination, date, description, budget, trip_id,)
    )
    db.commit()

    response = {"message": "Trip updated successfully!",
                "trip": {
                    "destination": destination,
                    "description": description,
                    "date": date,
                    "budget": budget
                }}
    
    return jsonify(response)

@views.route('/delete_trip', methods=['DELETE'])
def delete(trip_id):
    db = open_db()

    trip = db.execute(
        "SELECT * FROM trips WHERE trip_id = ?", (trip_id,)
    ).fetchone()
    
    if not trip:
        return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404

    db.execute(
        "DELETE FROM trips WHERE trip_id = ?", (trip_id,)
    )

    db.commit()

    return jsonify({"message": "Trip deleted successfully!"}), 200


# uploading photos
# Allowed extensions for photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Photos(Resource):
    def get_photo(self, photo_id=None):
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
        
    def post_photo(self):
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Save file path to database
            db = open_db()

            if not file_path:
                return jsonify({"error": "file path is required"}), 400
            
            db.execute(
                'INSERT INTO photos (file_path) VALUES (?)', (file_path)
            )
            db.session.commit()

            return jsonify({"message": "Photos uploaded successfully"}), 201
        return jsonify({"error": "Invalid file type or no file found"}), 400
    
    def delete_photo(self, photo_id):
        db = open_db()

        photo = db.execute(
            'SELECT * FROM photos WHERE photo_id = ?', (photo_id,)
        )

        if not photo:
            return jsonify({"error": f"Photo with photo id {photo_id} not found"}), 404
        
        db.execute(
            'DELETE FROM photos WHERE photo_id = ?', (photo_id,)
        )

        db.session.commit()

        return jsonify({"message": "Photo deleted successfully!"}), 200


api.add_resource(Photos, "/api/trips/photos/", "/api/trips/photos/<int:photo_id>")


# EXPENSES
class Expense(Resource):
    def get_expenses(self, expenses_id=None):
        db = open_db()

        if expenses_id is None:
            expenses = db.execute(
                'SELECT expenses_id, expenses_description, expenses_date, amount, timestamp FROM expenses ORDER BY amount DESC'
            ).fetchall()

            if not expenses:
                return jsonify({"error": "No expenses found"}), 404
            
            all_expenses = []
            for expense in expenses:
                all_expenses.append({
                    "expenses_id": escape(expense["expenses_id"]),
                    "expenses_description": escape(expense["expenses_description"]),
                    "expenses_date": escape(expense["expenses_date"]),
                    "amount": escape(expense["amount"]),
                    "timestamp": escape(expense["timestamp"])
                })

            return jsonify(expenses), 200
        
        else:
            expense = db.execute(
                'SELECT expenses_id, expenses_description, expenses_date, amount, timestamp FROM expenses WHERE expenses_id = ?', (expenses_id,)
            ).fetchone()

            if expense is None:
                return jsonify({"error": f"Expense with expense id {expenses_id} not found"}), 404
            
            return jsonify({
                "expenses_id": escape(expense["expenses_id"]),
                "expenses_description": escape(expense["expenses_description"]),
                "expenses_date": escape(expense["expenses_date"]),
                "amount": escape(expense["amount"]),
                "timestamp": escape(expense["timestamp"])
            }), 200

    def post_expenses(self):
        db = open_db()
        data = request.get_json()

        if not data:
            error = "No data given"
            return jsonify({"error": error}), 400
        
        expenses_description = data.get('expenses_description')
        expenses_date = data.get('expenses_date')
        amount = data.get('amount')
        

        if not amount:
            error = "Amount is required"
            return jsonify({"error": error}), 400
        try:
            expense = db.execute(
                "INSERT INTO expenses (expenses_description, expenses_date, amount) VALUES (?, ?, ?)", (expenses_description, expenses_date, amount)
            )
            db.commit()

            expenses_id = expense['expenses_id']

            response_data = {"message": "Expense was created successfully!",
                             "expense": {
                                "expenses_description": expenses_description,
                                "expenses_date": expenses_date,
                                "amount": amount,
                                "expenses_id": expenses_id}}
            return jsonify(response_data), 201
        except Exception as e:
            return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500

    def put_expenses(self, expenses_id):
        db = open_db()
        data = request.get_json()

        expense = db.execute(
            "SELECT expenses_id, expenses_description, expenses_date, amount, timestamp FROM expenses WHERE expenses_id = ?", (expenses_id,)
        ).fetchone()

        if not expense:
            return jsonify({"error": f"Expense with expense id {expenses_id} not found"}), 404
        
        expenses_description = data.get('expenses_description')
        expenses_date = data.get('expenses_date')
        amount = data.get('amount')

        if not amount:
            return jsonify({"error": "Amount is required"}), 400
        
        db.execute(
            "UPDATE expenses SET expenses_description = ?, expenses_date = ?, amount = ? WHERE expenses_id = ?", (expenses_description, expenses_date, amount, expenses_id)
        )

        db.commit()

        response = {"message": "Expense updated successfully!",
                    "expense": {
                        "expenses_description": expenses_description,
                        "expenses_date": expenses_date,
                        "amount": amount
                    }}

        return jsonify(response)

    def delete_expense(self, expenses_id):
        db = open_db()

        expense = db.execute(
            "SELECT * FROM expenses WHERE expenses_id = ?", (expenses_id,)
        ).fetchone()

        if not expense:
            return jsonify({"error": f"Expense with expense id {expenses_id} not found"}), 404
        
        db.execute(
            "DELETE FROM expenses WHERE expenses_id = ?", (expenses_id,)
        )

        db.commit()

        return jsonify({"message": "Expense deleted successfully!"}), 200
    
api.add_resource(Expense, "/api/trips/expenses/", "/api/trips/expenses/<int:expenses_id>")