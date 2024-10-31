from flask import Blueprint, render_template, abort, redirect, url_for, request, session, flash
from flask_restful import Api
from markupsafe import escape
from jinja2 import TemplateNotFound
from .static import login_form
from werkzeug.utils import secure_filename 

views = Blueprint("views", __name__, template_folder = 'templates')
api = Api(views)

@views.route("/<name>", methods=['GET'])
def home(name=None):
    if 'username' in session:
        flash(f'{request.form['name']} you are logged in!')
    return render_template('templates/', person=name)


@views.route("/TripsLogin", methods=["GET", "POST"])
def login(name=None, error=None):
    form = login_form
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('views.home', person=name, error=error)

@views.route("/TripsLogout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@views.route("/UploadImagies", methods=['GET', 'POST'])
def upload_imagies():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f'{secure_filename(file.filename)}')