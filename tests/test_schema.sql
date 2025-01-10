DROP TABLE IF EXISTS user;
CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS trip;
CREATE TABLE trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    budget INTEGER,
    user_id INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);

DROP TABLE IF EXISTS expence;
CREATE TABLE expence (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    amount REAL NOT NULL,
    expense_description TEXT,
    expense_date TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trip (trip_id) ON DELETE CASCADE
);

INSERT INTO user (fullname, username, password, email) VALUES ('Test User', 'test', 'scrypt:32768:8:1$aYKIvKP8qeyftCLI$d6c337bffbf5f25d90e3922f310820b991ab6e013af1ee42cc1f93a953f1aba9b7286c71ca3649e4c6269349ba5f7b5b5f093971e8abe295eab65a05aacd235e', 'test@example.com');

INSERT INTO trip (destination, date, description, budget) VALUES ('Paris', '14.02.2025', 'Valentines trip', 3000);

INSERT INTO expence (amount, expense_description, expense_date) VALUES (300, 'Dinner', '14.02.2025');