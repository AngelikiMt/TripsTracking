from flask import Blueprint, request, session, g, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from .db import open_db
import functools

users = Blueprint("users", __name__, url_prefix='/users')

@users.route('/register', methods=['POST'])
def register():
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
            return jsonify({"message": "Registered successfully"}), 201
        except db.IntegrityError:
            error = f"User {username} is already registered."
    
    return jsonify({"error": error}), 400


@users.route('/delete_user', methods = ['DELETE'])
def delete_user():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON format or no data received"}), 400
    
    username = data.get('username')
    
    if username not in data:
        return jsonify({"error": "No username found"}), 400

    db = open_db()

    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        return jsonify({"error": f"No user found with user id {username}"}), 404
    try:
        db.execute(
            'DELETE FROM user WHERE user_id = ?', (username,)
        )

        db.commit()
        
        return jsonify({"message": "User deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500
    
    
@users.route('/login', methods = ['POST'])
def login():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON format or no data received"}), 400
    
    username = data.get('username')
    password = data.get('password')

    db = open_db()
    error = None

    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Invalid username'
    elif not check_password_hash(user['password'], password):
        error = 'Invalid password'
    
    if error is None:
        session.clear()
        session['user_id'] = user['user_id']
        fullname = user['fullname']

        return jsonify({
            "message": f"{fullname}, login successful", 
            "user_id": user['user_id'], 
            "username": user['username'], 
            }), 200
    else:
        return jsonify({"error": error}), 401

@users.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successfully"}), 200


# For user's information to be available to other users blueprints
@users.before_request
def user_info():
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


