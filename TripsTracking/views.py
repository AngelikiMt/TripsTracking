from flask import Blueprint, abort, request, session, jsonify, current_app, g
from flask_restful import Api, Resource
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
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
            db.commit()

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
            'DELETE * FROM photos WHERE photo_id = ?', (photo_id,)
        )

        db.commit()

        return jsonify({"message": "Photo deleted successfully!"}), 200


api.add_resource(Photos, "/api/trips/photos/", "/api/trips/photos/<int:photo_id>")
    