from flask import Blueprint, abort, request, session, flash, jsonify, current_app, g
from flask_restful import Api, Resource
from markupsafe import escape
from werkzeug.utils import secure_filename 
from .db import open_db
import os

views = Blueprint("views", __name__, template_folder = 'templates')
api = Api(views)
# Allowed extensions for photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/api/user/<fullname>", methods=['GET'])
def get_home(user_id=None, fullname=None):
    lang = request.args.get('lang', 'en')
    db = open_db()

    user = db.execute(
        'SELECT user_id, username, password FROM user WHERE user_id = ?', (user_id,)
    ).fetchone()

    if user is None:
        return jsonify({"error": f"User with user id: {user_id} not found"}), 404
    
    return jsonify({
        "message": f"{fullname}, you are logged in!",
        "user": {
            "user_id" : user['user_id'],
            "username" : user['username']
        },
        "lang": lang
    }), 200
    
# uploading photos
@views.route("/api/trips/<int:trip_id>/photos", methods=['GET', 'POST'])
def upload_photos(trip_id):
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save file path to database
        db = open_db()
        db.execute(
            'INSERT INTO trips (trip_id, description) VALUES (?, ?)' (trip_id, file_path)
        )
        db.commit()

        return jsonify({"message": "Photos uploaded successfully"}), 201
    return jsonify({"error": "Invalid file type"}), 400

# Create a new trip (Create)
@views.route("/api/my_trips/<int:trip_id>", methods = ['GET', 'POST'])
def myTrips(lang):
    db = open_db()
    if request.method == 'POST':
        location = request.form['location']
        date = request.form['date']
        description = request.form['description']
        budget = request.form['badget']

        if not location:
            flash("Your trip's destination is required.")
        
        if not description:
            flash("Your trip's description is required.")
        
        else:
            db.execute(
                'INSERT INTO trip (location, date, descrition, budget) VALUES (?, ?, ?, ?)', (location, date, description, budget)
            )
            db.commit()
            flash("Trip created successfully!")
            return redirect(url_for('views.myTrips', lang=lang))
        
    # Retrieve all trips (Read)
    trips = db.execute(
        'SELECT trip_id, location, date, description, budget, timestamp FROM trip ORDER BY date DESC'
    ).fetchall()

    return render_template('my_trips.html', trips=trips, lang=lang)

# Update trip
@views.route("/api/my_trips/edit/<int:trip_id>", methods = ['GET', 'PUT'])
def edit_trip(trip_id, lang):
    db = open_db()

    # Fetch the specific trip for editing
    trip = db.execute(
        'SELECT * FROM trip where id = ?', (trip_id)
    ).fetchone()

    if request.method == 'POST':
        location = request.form['location']
        date = request.form['date']
        description = request.form['description']
        budget = request.form['badget']

        if not location:
            flash("Your trip's destination is required.")
        
        if not description:
            flash("Your trip's description is required.")

        else:
            db.execute(
                'UPDATE trip SET location = ?, date = ?, description = ?, budget = ? WHERE trip_id = ?', (location, date, description, budget, trip_id)
            )
            db.commit()
            flash("Trip updated successully!")
            return redirect(url_for('views.myTrips', lang=lang))
    return render_template('edit_trip.html', trip=trip, lang=lang)

# Deleted trip
@views.route("/myTrips/delete/<location>", methods = ['DELETE'])
def deleteTrip(trip_id, lang):
    db = open_db()

    db.execute(
        'DELETE FROM trip WHERE trip_id = ?' , (trip_id)
    )
    db.commit()
    flash("Trip deleted successfully!")
    return redirect(url_for('views.myTrips', lang=lang))

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