DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    date TEXT,
    description BLOB NOT NULL,
    budget REAL,
    user_id INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
);

CREATE TABLE expenses (
    expenses_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    amount REAL NOT NULL,
    expenses_description TEXT,
    expenses_date TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips (trip_id) ON DELETE CASCADE
);

CREATE TABLE photos (
    photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    file_path TEXT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips (trip_id) ON DELETE CASCADE
);