from flask import Blueprint, render_template, abort, redirect, url_for, request, session, flash
from flask_restful import Api
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint("auth", __name__, url_prefix='/auth')
api = Api(auth)

@auth.route('/tripsRegister', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        