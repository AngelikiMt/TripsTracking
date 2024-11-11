from flask import Blueprint, abort, request, session, jsonify, current_app, g
from flask_restful import Api, Resource
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os

views = Blueprint("views", __name__)
api = Api(views)

class Trips(Resource):
    def get(self, trip_id=None):
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
            
            return jsonify(trips_list), 200
        
        else:
            trip = db.execute(
                'SELECT trip_id, destination, date, description, budget, timestamp FROM trips WHERE trip_id = ?', (trip_id,)
            ).fetchone()

            if trip is None:
                return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
            
            return jsonify({
                "trip_id": escape(trip["trip_id"]),
                "destination": escape(trip["destination"]),
                "date": escape(trip["date"]),
                "description": escape(trip["description"]),
                "budget": escape(trip["budget"]),
                "timestamp": escape(trip["timestamp"]),
            }), 200       
    
    def post(self):
        db = open_db()
        data = request.get_json()

        destination = data.get('destination')
        date = data.get('date')
        description = data.get('description')
        budget = data.get('budget')

        if not destination or not description:
            return jsonify({"error": "Destination and description are required"}), 400
        
        db.execute(
            'INSERT INTO trips (destination, date, descrition, budget) VALUES (?, ?, ?, ?)', (destination, date, description, budget,)
        )
        db.commit()
        return jsonify({"message": "Trip was created successfully!"}), 201
        
    def put(self, trip_id):
        db = open_db()
        data = request.get_json()

        # Fetch the specific trip for editing
        trip = db.execute(
            'SELECT * FROM trip where trip_id = ?', (trip_id,)
        ).fetchone()

        if not trip:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        
        destination = data.get('destination')
        date = data.get('date')
        description = data.get('description')
        budget = data.get('budget')

        if not destination or not description:
            return jsonify({"error": "Description and destination of the trip are required"}), 404
        
        db.execute(
            'UPDATE trips SET destination = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (destination, date, description, budget, trip_id,)
        )
        db.commit()
        return jsonify({"message": f"Trip with trip id {trip_id} updated successfully!"})
        
    def delete(self, trip_id):
        db = open_db()

        trip = db.execute(
            'SELECT * FROM trips WHERE trip_id = ?', (trip_id,)
        )
        
        if not trip:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404

        db.execute(
            'DELETE * FROM trips WHERE trip_id = ?', (trip_id,)
        )

        db.commit()

        return jsonify({"message": "Trip deleted successfully!"}), 200
        
# Retrieve all trips (Read), Create, Read, Update, Delete a trip
api.add_resource(Trips, "/trips/", "/trips/<int:trip_id>/")

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

# uploading photos
# Allowed extensions for photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/api/trips/<int:destination>/photos", methods=['GET'])
def list_photos(trip_id):
    lang = request.args.get('lang', 'en')
    db = open_db()
    try:
        photos = db.execute(
            'SELECT * FROM trips where trip_id = ?', (trip_id,)
        )
        destination = photos['destination']
        return jsonify({"message": "Photos", "destination":destination, "lang": lang}), 200
    except ValueError:
        return jsonify({"error": "No file found", "lang": lang}), 400

@views.route("/api/trips/<int:trip_id>/photos", methods=['POST'])
def upload_photos(trip_id):
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save file path to database
        db = open_db()
        db.execute(
            'INSERT INTO photos (photo_id, file_path) VALUES (?, ?)', (trip_id, file_path)
        )
        db.commit()

        return jsonify({"message": "Photos uploaded successfully"}), 201
    return jsonify({"error": "Invalid file type"}), 400