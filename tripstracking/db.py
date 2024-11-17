import sqlite3
from flask import current_app, g, jsonify
import click
from datetime import datetime

# Checks if the db connection exists in g if not sets up the connection
def open_db():
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        except Exception as e:
            return jsonify({"error": f"{str(e)}"}), 404
    return g.db

# Closes the connection if exists
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Initializes the database with the schema.sql file
def init_db():
    db = open_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Defines a command to set up the database schema
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('The new database has been created!')

# Registers a converter to handle the datastamp fields
sqlite3.register_converter (
    "timestamp", lambda x: datetime.fromisoformat(x.decode())
)
