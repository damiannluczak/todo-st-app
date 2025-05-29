import streamlit as st
import sqlite3
import os

# Inicjalizacja bazy danych przy pierwszym uruchomieniu
if not os.path.exists("todo.db"):
    from init_db import init_db
    init_db()

def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_tasks(user_id, done=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND done = ?", (user_id, int(done)))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(user_id, title, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)", (title, description, user_id))
    conn.commit()
    conn.close()

def mark_done(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="ToDo App", page_icon="")
    st.title("ToDo List")

    if "user" not in st.session_state:
        st.subheader("Zaloguj się jako:")
        username = st.text_input("Login")
        password = st.text_input("Hasło", type="password")
        if st.button("Zaloguj"):
            user = login_user(username, password)
            if user:
                st.session_state.user = {"id": user["id"], "username": user["username"]}
                st.experimental_rerun()
            else:
                st.error("Nieprawidłowy login lub hasło.")
        return

    user = st.session_state.user
    st.success(f"Zalogowany jako {user['username']}")
    st.write("## Dodaj nowe zadanie")
    title = st.text_input("Tytuł")
    description = st.text_area("Opis")
    if st.button("Dodaj zadanie"):
        if title:
            add_task(user["id"], title, description)
            st.experimental_rerun()

    st.write("## Twoje zadania")

    tasks = get_tasks(user["id"], done=False)
    for task in tasks:
        st.write(f"**{task['title']}** – {task['description']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔ Zrobione", key=f"done_{task['id']}"):
                mark_done(task["id"])
                st.experimental_rerun()
        with col2:
            if st.button("Usuń", key=f"delete_{task['id']}"):
                delete_task(task["id"])
                st.experimental_rerun()

    st.write("## Zrobione")
    done_tasks = get_tasks(user["id"], done=True)
    for task in done_tasks:
        st.write(f" **{task['title']}** – {task['description']}")

    if st.button("🚪 Wyloguj"):
        del st.session_state.user
        st.experimental_rerun()

if __name__ == "__main__":
    main()