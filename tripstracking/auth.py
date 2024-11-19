from flask import Blueprint, request, session, g, jsonify, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from .db import open_db
import functools

users = Blueprint("users", __name__, url_prefix='/users')

def crud_trips(view):
    '''Ensures that only authenicated users can access any view function. Executes the view function if the user is authenticate, else returns a 401 error.'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"message": "User is not logged in"}), 401
        return view(**kwargs)
    return wrapped_view


@users.before_request
def user_info():
    '''Runs before any users/view function. Selects all user's info from the database and store them in g.'''
    db = open_db()
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()

@users.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
        
        return jsonify({"error": error}), 409
    return render_template('auth/registration.html')

@users.route('/delete_user', methods = ['GET', 'DELETE'])
@crud_trips
def delete_user():
    if request.method == 'DELETE':
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
    return render_template('auth/delete_user.html')
    
@users.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
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
    return render_template('auth/login.html')

@users.route('/logout', methods = ['POST'])
@crud_trips
def logout():
    session.clear()
    return jsonify({"message": "Logout successfully"}), 200




