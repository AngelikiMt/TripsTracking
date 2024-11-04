import sqlite3
from flask import current_app

conn = sqlite3.connect(
    current_app.config['DATABASE']
)