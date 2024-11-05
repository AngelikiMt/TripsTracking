from flask import Blueprint, render_template, abort, redirect, url_for, request, session, flash
from flask_restful import Api
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db

auth = Blueprint("auth", __name__, url_prefix='/auth')
api = Api(auth)

@auth.route('/tripsRegister', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        if not fullname:
            error = 'Fullname is required'
        elif not password:
            error = 'Password is required'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/tripsRegister.html')