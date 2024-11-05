import sqlite3
from flask import current_app, g
import click
from datetime import datetime

# checks if the db connection exists in g
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
        )
        g.db.commit()
    return g.db

# closes the connection if exists
def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()

# initializes the database with the schema.sql file
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('The new database has been created!')

sqlite3.register_converter (
    "timestamp", lambda x: datetime.fromisoformat(x.decode())
)