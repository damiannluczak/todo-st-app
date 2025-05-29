import sqlite3
import os
from werkzeug.security import generate_password_hash

# Upewnij się, że katalog na bazę danych istnieje
if not os.path.isdir('instance'):
    os.mkdir('instance')

# Połączenie z bazą SQLite
conn = sqlite3.connect('instance/todo.db')
c = conn.cursor()

# Tabela użytkowników
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    password TEXT NOT NULL
);
''')

# Tabela zadań
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
''')

# ✅ Użytkownicy testowi (dla prowadzącego)
users = [
    ('demo', 'demo@example.com', 'demo123'),
    ('student1', 's1@example.com', 'haslo1'),
    ('student2', 's2@example.com', 'haslo2'),
]

for username, email, plain_pw in users:
    hashed = generate_password_hash(plain_pw)
    c.execute("INSERT OR IGNORE INTO users (username, email, password) VALUES (?, ?, ?)",
              (username, email, hashed))

conn.commit()
conn.close()
print("Baza danych zainicjalizowana z przykładowymi użytkownikami.")