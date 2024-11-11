from flask import Blueprint, request, session, g, jsonify
from flask_restful import Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash
from .db import open_db
import functools

auth = Blueprint("auth", __name__, url_prefix='/auth')
api = Api(auth)

# Register
@auth.route('/api/register', methods=['POST'])
def register():
    lang = request.args.get('lang', 'en')
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')

    db = open_db()
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
                (username, generate_password_hash(password), fullname,)
            )
            db.commit()
            return jsonify({"message": "Registered successfully", "lang": lang}), 201
        except db.IntegrityError:
            error = f"User {username} is already registered."
    
    return jsonify({"error": error, "lang": lang}), 400


# Login
@auth.route('/api/login/<fullname>', methods = ['POST'])
def login(fullname=None):
    lang = request.args.get('lang', 'en')
    data = request.get_json()
    username = data.get('username')
    password = check_password_hash(data.get('password'))

    db = open_db()

    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Please enter a valid username'
    elif not check_password_hash(user['password'], password):
        error = 'Please enter a valid password'
    
    if error is None:
        session.clear()
        session['user_id'] = user['user_id']
        fullname = user['fullname']                                                                               
        return jsonify({"message": f"{fullname}, login successful", "user_id": user['user_id'], "username": user['username'], "lang": lang}), 200
    else:
        return jsonify({"error": error, "lang": lang}), 401


# For user's information to be available to other auth blueprints
@auth.before_request
def users_info():
    db = open_db()
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()

# For crud the trips tracking the user must be logged in.
def crud_trips(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"message": "User is not logged in"}), 401
        return view(**kwargs)
    return wrapped_view

# Logout
@auth.route('/api/logout', methods = ['POST'])
def logout():
    lang = request.args.get('lang', 'en')
    session.clear()
    return jsonify({"message": "Logout successfully", "lang": lang}), 200