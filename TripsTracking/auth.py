from flask import Blueprint, render_template, redirect, url_for, request, session, flash, g
from flask_restful import Api
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
import functools

auth = Blueprint("auth", __name__, url_prefix='/auth')
api = Api(auth)

# Register
@auth.route('/tripsRegister', methods=['GET', 'POST'])
def register(lang):
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
                    "INSERT INTO user (username, password, fullname) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), fullname)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        flash(error)
    return render_template('auth/tripsRegister.html', lang=lang)

# Login
@auth.route('/login', methods = ['GET', 'POST'])
def login(lang):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username)
        ).fetchone()

        if user is None:
            error = 'Please enter a valid username'
        elif not check_password_hash(user['password'], password):
            error = 'Please enter a valid password'
        
        if error is None:
            session.clear()
            session['user_id'] = user['user_id']                                                                                  
            return redirect(url_for('views.home'))
        flash(error)
    return render_template('auth/login.html', lang=lang)

# For user's information to be available to other views
@auth.app_requests
def users_info():
    db = get_db()
    user_id = session.get('user_id')

    if user_id in None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id)
        ).fetchone()

# For crud the trips tracking the user must be logged in.
def crud_trips(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user in None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# Logout
@auth.roote('/logout', methods = ['GET'])
def logout():
    session.clear()
    return redirect(url_for('views.home'))