import sqlite3
from flask import current_app, g, jsonify
import click
from datetime import datetime

def open_db():
    '''Returns the database connection stored in g, after creating the sqlite3 connection, connecting the file in which the function was called, with the database.
    '''
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        except Exception as e:
            return jsonify({"error": f"Error connecting the file with the database: {str(e)}"}), 404
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    '''Initializes the database using the schema.sql code for creating or resetting the database. The function reads the contents of the schema.sql file and executes them as a script to set up the database structure.
    '''
    db = open_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    '''Creates a user-friendly command to initialize a new database, or erase the existing data to create a new one. Run the command: 
    
    flask init-db 
    
    If returned an error: 
    
    Error: Could not locate Flask application

    Try the command:
    
    flask --app trips.py init-db
    
    This error occurs when Flask cannot detect the application context to run commands. Using the --app option you specify the application file, which in this case is the trips.py.
    '''
    init_db()
    click.echo('The new database has been created!')

sqlite3.register_converter (
    "timestamp", lambda x: datetime.fromisoformat(x.decode())
)

'''The lambda function converts the data from timestamp column to a Python datetime object.'''