import sqlite3
import os
import hashlib

DB_NAME = "todo.db"

# Funkcja haszująca hasła (SHA-256)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    if os.path.exists(DB_NAME):
        print("Baza danych już istnieje.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tworzenie tabeli użytkowników
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL
        )
    ''')

    # Tworzenie tabeli zadań
    cursor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Dodanie przykładowych użytkowników
    users = [
        ("demo1", "demo1@example.com", hash_password("demo1")),
        ("demo2", "demo2@example.com", hash_password("demo2"))
    ]
    cursor.executemany("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", users)

    conn.commit()
    conn.close()
    print("Baza danych została utworzona wraz z przykładowymi użytkownikami.")

if __name__ == "__main__":
    init_db()