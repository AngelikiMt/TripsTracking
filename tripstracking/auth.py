from flask import Blueprint, request, session, g, jsonify, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
from .db import open_db
import functools
from .static import forms

users = Blueprint("users", __name__, url_prefix='/users', template_folder='templates/auth')

def crud_trips(users):
    '''Ensures that only authenicated users can access any users function. Executes the users function if the user is authenticate, else returns a 401 error.'''
    @functools.wraps(users)
    def wrapped_users(**kwargs):
        if g.user is None:
            return jsonify({"message": "User is not logged in"}), 401
        return users(**kwargs)
    return wrapped_users

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
def register_user():
    form = forms.RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        json_response = "application/json" in request.headers.get("accept", "")

        if json_response:
            data = request.get_json()
        else:
            data = request.form

        username = data.get('username')
        password = data.get('password')
        fullname = data.get('fullname')
        email = data.get('email')

        db = open_db()
        error = None

        if not all([username, fullname, password, email]):
            error = 'All fields required.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, fullname, email) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password), fullname, email)
                )

                db.commit()
                
                message = "Registered successfully!"
                if json_response:
                    return jsonify({"message": message}), 201
                flash(message)
                return redirect(url_for('users.login_user'))

            except db.IntegrityError:
                error = "Registration failed"

        if json_response:
            return jsonify({"error": error}), 409
        flash(error)
        return redirect(url_for('users.register_user'))

    return render_template('register_user.html', form=form)

@users.route('/delete_user', methods = ['GET', 'POST'])
@crud_trips
def delete_user():
    if 'user_id' not in session:
        flash("You need to be logged in to delete your account.")
        return redirect(url_for('users.login'))

    user_id = session['user_id'] 
    json_response = "application/json" in request.headers.get("accept", "")
    db = open_db()

    user = db.execute(
        "SELECT * FROM user WHERE user_id = ?", (user_id,)
    ).fetchone()

    if request.method == 'POST':
        try:
            db.execute(
                'DELETE FROM user WHERE user_id = ?', (user_id,)
            )
            db.commit()
            session.clear()
            
            message = "User deleted successfully!"
            if json_response:
                return jsonify({"message": message}), 200
            flash(message)
            return redirect(url_for('users.register_user'))
        
        except Exception as e:
            error = f"Failed to delete user: {str(e)}"  
        if json_response:
            return jsonify({"error": error}), 404
        flash(error)
        return render_template('delete_user.html', user_id=user_id, user=user)
    return render_template('delete_user.html', user_id=user_id, user=user)

@users.route('/login', methods = ['GET', 'POST'])
def login_user():
    form = forms.RegisterForm(request.form)
    if request.method == 'POST':
        json_response = "application/json" in request.headers.get("accept", "")

        if json_response:
            data = request.get_json()
        else:
            data = request.form

        db = open_db()
        error = None

        username = data.get('username')
        password = data.get('password')

        if (not username) or (not password):
            error = "Username and password are required"

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Invalid username'

        if not check_password_hash(user['password'], password):
            error = 'Invalid password'
        
        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            fullname = user['fullname']

            message = f"{fullname}, login successful"

            if json_response:
                return jsonify({
                    "message": message, 
                    "user_id": user['user_id'], 
                    "username": user['username'], 
                    }), 200
            flash(message)
            return redirect(url_for('views.home'))

        if json_response:
            return jsonify({"error": error}), 401
        flash(error)
        return redirect(url_for('users.login_user', error=error))

    return render_template('login.html', form=form)

@users.route('/logout', methods = ['GET','POST'])
@crud_trips
def logout_user():
    if request.method == 'POST':
        json_response = "application/json" in request.headers.get("accept", "")
        session.clear()

        message = "Logout successfully"
        if json_response:
            return jsonify({"message": message}), 200
        flash(message)
        return redirect(url_for('users.login_user'))
    
    return render_template('logout.html')

