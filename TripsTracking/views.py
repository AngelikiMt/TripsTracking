from flask import Blueprint, render_template, abort, redirect, url_for, request, session, flash
from flask_restful import Api
from markupsafe import escape
from jinja2 import TemplateNotFound
#from .static import login_form
from werkzeug.utils import secure_filename 

views = Blueprint("views", __name__, template_folder = 'templates')
api = Api(views)

@views.route("/<fullname>", methods=['GET'])
def home(lang, fullname=None):
    try:
        if 'user_id' in session:
            flash(f'{fullname} you are logged in!')
        return redirect(url_for('views.get_home', person=fullname, lang=lang))
    except TemplateNotFound:
        abort(404)

@views.route("/UploadImagies", methods=['GET', 'POST'])
def upload_imagies():
    if request.method == 'POST':
        file = request.files['the_file']
        file.save(f'{secure_filename(file.filename)}')