import streamlit as st
import sqlite3
import hashlib

# Funkcja do haszowania haseł
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Połączenie z bazą danych
conn = sqlite3.connect('todo.db', check_same_thread=False)
cursor = conn.cursor()

# Sprawdzenie czy użytkownik istnieje i hasło się zgadza
def login_user(username, password):
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    return cursor.fetchone()

# Pobierz zadania danego użytkownika
def get_tasks(user_id, done=False):
    cursor.execute("SELECT id, title, description FROM tasks WHERE user_id = ? AND done = ?", (user_id, int(done)))
    return cursor.fetchall()

# Dodaj nowe zadanie
def add_task(user_id, title, description):
    cursor.execute("INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)", (title, description, user_id))
    conn.commit()

# Oznacz zadanie jako zrobione
def mark_task_done(task_id):
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()

# Usuń zadanie
def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

# Główna logika
def main():
    st.set_page_config(page_title="ToDo App", layout="centered")
    st.title("ToDo Lista Webowa")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.header("Zaloguj się")

        username = st.text_input("Login")
        password = st.text_input("Hasło", type="password")

        if st.button("Zaloguj"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.success(f"Zalogowano jako {user[1]}")
            else:
                st.error("Nieprawidłowy login lub hasło.")
        return

    st.sidebar.title("Nawigacja")
    page = st.sidebar.radio("Wybierz stronę", ["Moje zadania", "Wyloguj"])

    if page == "Wyloguj":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.experimental_rerun()

    if page == "Moje zadania":
        st.header(f"Zalogowany jako: {st.session_state.username}")
        st.subheader("Dodaj nowe zadanie")

        with st.form("add_task_form"):
            title = st.text_input("Tytuł")
            description = st.text_area("Opis")
            submitted = st.form_submit_button("Dodaj zadanie")
            if submitted and title:
                add_task(st.session_state.user_id, title, description)
                st.success("Dodano zadanie.")
                st.rerun()

        st.subheader("Zadania do wykonania")
        tasks = get_tasks(st.session_state.user_id, done=False)
        for task in tasks:
            with st.expander(f"{task[1]} - {task[2]}"):
                col1, col2 = st.columns(2)
                if col1.button("Oznacz jako zrobione", key=f"done_{task[0]}"):
                    mark_task_done(task[0])
                    st.rerun()
                if col2.button("Usuń", key=f"del_{task[0]}"):
                    delete_task(task[0])
                    st.rerun()

        st.subheader("Zakończone zadania")
        tasks_done = get_tasks(st.session_state.user_id, done=True)
        for task in tasks_done:
            st.markdown(f"✔️ {task[1]} - {task[2]}")

if __name__ == "__main__":
    main()