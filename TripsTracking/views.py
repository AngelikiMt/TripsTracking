from flask import Blueprint, render_template, abort, redirect, url_for, request, session, flash
from flask_restful import Api
from markupsafe import escape
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename 
from .db import open_db

views = Blueprint("views", __name__, template_folder = 'templates')

@views.route("/user/<fullname>", methods=['GET'])
def home(lang, fullname=None):
    try:
        if 'user_id' in session:
            flash(f'{fullname} you are logged in!')
        return redirect(url_for('views.home', person=fullname, lang=lang))
    except TemplateNotFound:
        abort(404)

@views.route("/UploadImages", methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f'{secure_filename(file.filename)}')

# Create a new trip (Create)
@views.route("/myTrips", methods = ['GET', 'POST'])
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
@views.route("/myTrips/edit/<location>", methods = ['GET', 'PUT'])
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