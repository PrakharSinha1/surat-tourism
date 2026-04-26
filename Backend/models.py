import sqlite3

DB_NAME = "database.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # 👤 USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0,
        is_approved INTEGER DEFAULT 0
    )
    """)

    # 🧳 ITINERARY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        places TEXT,
        events TEXT,
        food TEXT,
        dates TEXT
    )
    """)

    # 🎤 EVENT REQUESTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_by TEXT,
        is_approved INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()