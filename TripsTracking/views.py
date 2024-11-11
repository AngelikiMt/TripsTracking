from flask import Blueprint, abort, request, session, jsonify, current_app, g
from flask_restful import Api, Resource
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os

views = Blueprint("views", __name__)
api = Api(views)

class Trips(Resource):
    def get_trip(self, trip_id):
        db = open_db()
        trip = db.execute(
            'SELECT trip_id, destination, date, description, budget, timestamp FROM trip ORDER BY date DESC'
        ).fetchall()
        if trip_id not in trip:
            return jsonify({"error": "Trip not found"}), 404
        return trip[trip_id]
    
    def post_trip(self, trip_id):
        lang = request.args.get('lang', 'en')
        db = open_db()
        data = request.get_json()

        destination = data.get['destination']
        date = data.get['date']
        description = data.get['description']
        budget = data.get['bdget']

        if not destination:
            return jsonify({"error": "Your trip's destination is required"}), 404
        
        if not description:
            return jsonify({"error": "Your trip's description is required"}), 404
        
        else:
            db.execute(
                'INSERT INTO trip (destination, date, descrition, budget) VALUES (?, ?, ?, ?)', (destination, date, description, budget,)
            )
            db.commit()
            return jsonify({"message": f"The trip with trip id {trip_id} created successfully!"}), 200
        
    def put_trip(self, trip_id):
        lang = request.args.get("lang", "en")
        db = open_db()
        data = request.get_json()

        # Fetch the specific trip for editing
        trip = db.execute(
            'SELECT * FROM trip where trip_id = ?', (trip_id,)
        ).fetchone()
        
        destination = data.get['destination']
        date = data.get['date']
        description = data.get['description']
        budget = data.get['badget']

        if not destination and not description:
            return jsonify({"error": "Description and destination of the trip are required"}), 404
        else:
            db.execute(
                'UPDATE trip SET destination = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (destination, date, description, budget, trip_id,)
            )
            db.commit()
            return trip[trip_id]
        
    def delete_trip(self, trip_id):
        lang = request.args.get("lang", "en")
        db = open_db()

        trips = db.execute(
            'DELETE FROM trip WHERE trip_id = ?' , (trip_id,)
        )
        db.commit()
        if trip_id not in trips:
            return jsonify({"error": f"Trip with trip id {trip_id} not found"}), 404
        return jsonify({"message": "Trip deleted successfully"}), 200
        

api.add_resource(Trips, "/trips/<int:trip_id>/")

# Retrieve all trips (Read)
#@views.route("api/my_trips", methods = ['GET'])
#def get_trips():

# Create a new trip (Create)
#@views.route("/api/my_trips/<int:trip_id>", methods = ['POST'])
#def myTrips():
    
# Update trip
#@views.route("/api/my_trips/edit/<int:trip_id>", methods = ['PUT'])
#def edit_trip(trip_id):       

# Deleted trip
#@views.route("/myTrips/delete/<destination>", methods = ['DELETE'])
#def deleteTrip(trip_id, lang):
    

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
            'INSERT INTO photos (photo_id, file_path) VALUES (?, ?)' (trip_id, file_path)
        )
        db.commit()

        return jsonify({"message": "Photos uploaded successfully"}), 201
    return jsonify({"error": "Invalid file type"}), 400