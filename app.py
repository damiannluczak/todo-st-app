from flask import Flask, render_template, request, redirect, url_for, jsonify, g, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'sekretnyklucz123'
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'todo.db'),
)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db:
        db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        username = request.form['username']
        email = request.form.get('email', '')
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_pw))
            db.commit()
            flash("Zarejestrowano pomyślnie.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Użytkownik już istnieje.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        username = request.form['username']
        password = request.form['password']
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is None or not check_password_hash(user["password"], password):
            flash("Nieprawidłowy login lub hasło.")
            return render_template("login.html")
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/tasks/<int:user_id>', methods=['GET'])
def api_get_tasks(user_id):
    db = get_db()
    tasks = db.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
    return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    title = data.get('title')
    desc = data.get('description', '')
    user_id = data.get('user_id')
    db = get_db()
    db.execute('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)', (title, desc, user_id))
    db.commit()
    return jsonify({'status': 'ok'}), 201

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form.get('description', '')
        if title:
            db.execute('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)',
                       (title, desc, user_id))
            db.commit()
        return redirect(url_for('index'))

    tasks_todo = db.execute('SELECT * FROM tasks WHERE user_id = ? AND done = 0', (user_id,)).fetchall()
    tasks_done = db.execute('SELECT * FROM tasks WHERE user_id = ? AND done = 1', (user_id,)).fetchall()
    return render_template('index.html', tasks_todo=tasks_todo, tasks_done=tasks_done)

@app.route('/done/<int:task_id>')
def mark_done(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute('UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?', (task_id, session['user_id']))
    db.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, session['user_id']))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    app.run(host='0.0.0.0', port=5050, debug=True)