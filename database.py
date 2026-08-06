"""
database.py
------------
This file handles everything related to the SQLite database.
It creates the tables (if they don't already exist), and gives
simple functions to the rest of the project to talk to the database.

I kept all the database code in one place so that the other files
(login.py, subject.py, exam.py etc) don't have to write SQL again
and again. This is called a "database layer".
"""

import sqlite3
import os
import hashlib

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner.db")


def get_connection():
    """Return a new connection to the database.
    We also turn ON foreign key support because SQLite keeps it OFF by default."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # lets us access columns by name, easier to read
    return conn


def hash_password(password):
    """We should never store plain text passwords in the database.
    Using sha256 hashing so the password is stored in an encrypted form."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    """Creates all the tables required for the project.
    Uses IF NOT EXISTS so running this multiple times is safe."""
    conn = get_connection()
    cur = conn.cursor()

    # 1. USERS table - for login/authentication
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_on TEXT DEFAULT (datetime('now'))
        )
    """)

    # 2. SUBJECTS table - each subject belongs to a user
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            total_topics INTEGER NOT NULL DEFAULT 0,
            created_on TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, subject_name)
        )
    """)

    # 3. EXAMS table - each exam is linked to one subject
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            exam_time TEXT,
            venue TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
        )
    """)

    # 4. STUDY_PLANS table - daily / weekly / monthly study plan entries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            plan_type TEXT NOT NULL CHECK(plan_type IN ('Daily','Weekly','Monthly')),
            plan_date TEXT NOT NULL,
            study_hours REAL NOT NULL DEFAULT 0,
            is_completed INTEGER NOT NULL DEFAULT 0 CHECK(is_completed IN (0,1)),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
        )
    """)

    # 5. PROGRESS table - keeps subject wise progress percentage
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            completed_topics INTEGER NOT NULL DEFAULT 0,
            total_topics INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
            UNIQUE(subject_id)
        )
    """)

    conn.commit()
    conn.close()


def seed_sample_data():
    """Adds one demo user + sample subjects/exams/plans ONLY if the database is empty.
    This is useful so that when the teacher/examiner opens the project for the
    first time, it is not completely empty."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        conn.close()
        return  # already has data, don't touch it again

    # sample user -> username: student, password: student123
    cur.execute("INSERT INTO users (username, password, full_name) VALUES (?,?,?)",
                ("student", hash_password("student123"), "Demo Student"))
    user_id = cur.lastrowid

    subjects = [("Data Structures", 10), ("Operating Systems", 8), ("DBMS", 12)]
    subject_ids = []
    for name, total in subjects:
        cur.execute("INSERT INTO subjects (user_id, subject_name, total_topics) VALUES (?,?,?)",
                    (user_id, name, total))
        subject_ids.append(cur.lastrowid)
        cur.execute("INSERT INTO progress (user_id, subject_id, completed_topics, total_topics) VALUES (?,?,?,?)",
                    (user_id, cur.lastrowid, 0, total))

    cur.execute("""INSERT INTO exams (user_id, subject_id, exam_name, exam_date, exam_time, venue)
                   VALUES (?,?,?,?,?,?)""",
                (user_id, subject_ids[0], "DS Mid Semester Exam", "2026-09-15", "10:00 AM", "Room 101"))
    cur.execute("""INSERT INTO exams (user_id, subject_id, exam_name, exam_date, exam_time, venue)
                   VALUES (?,?,?,?,?,?)""",
                (user_id, subject_ids[1], "OS End Semester Exam", "2026-10-05", "02:00 PM", "Room 204"))

    cur.execute("""INSERT INTO study_plans (user_id, subject_id, topic_name, plan_type, plan_date, study_hours, is_completed)
                   VALUES (?,?,?,?,?,?,?)""",
                (user_id, subject_ids[0], "Arrays and Linked List", "Daily", "2026-08-06", 2, 0))
    cur.execute("""INSERT INTO study_plans (user_id, subject_id, topic_name, plan_type, plan_date, study_hours, is_completed)
                   VALUES (?,?,?,?,?,?,?)""",
                (user_id, subject_ids[2], "ER Model Basics", "Daily", "2026-08-06", 1.5, 0))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # running "python database.py" directly will just set up the database
    create_tables()
    seed_sample_data()
    print("Database created successfully ->", DB_NAME)
