from flask import Blueprint, render_template, abort, redirect, url_for, request
from flask_restful import Api
from markupsafe import escape
from jinja2 import TemplateNotFound
from .static import login_form

views = Blueprint("views", __name__, template_folder = 'templates')
api = Api(views)

@views.route("/<name>", methods=['GET'])
def home(first_name, name=None):
    if login:
        return render_template('templates/', name=login.get(first_name))
    return redirect(url_for('views.home'))

@views.route("/TripLoginPage", methods=["GET", "POST"])
def login():
    form = login_form
    if request == 'POST':
        if form.valid_on_submit():
            first_name = form.name.data
            last_name = form.name.data
            email = form.email.data
    return redirect(url_for('views.login'))