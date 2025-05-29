import sqlite3

def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()

    # Tworzenie tabeli użytkowników
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tworzenie tabeli zadań
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Dodanie dwóch testowych użytkowników
    try:
        c.execute("INSERT INTO users (username, password) VALUES ('demo1', 'demo1')")
        c.execute("INSERT INTO users (username, password) VALUES ('demo2', 'demo2')")
    except sqlite3.IntegrityError:
        pass  # użytkownicy już istnieją

    conn.commit()
    conn.close()