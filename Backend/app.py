from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import hashlib
import os

app = Flask(__name__)

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS(app, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "https://surat-tourism-api-ps.onrender.com",
    "https://suratcitytourism.netlify.app",
])

# ─── DB PATH ─────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def connect_db():
    return sqlite3.connect(DB_PATH)

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── DB SETUP ────────────────────────────────────────────────────────────────

def create_tables():
    with connect_db() as conn:
        c = conn.cursor()

        # USERS
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                email    TEXT UNIQUE,
                password TEXT,
                is_admin INTEGER DEFAULT 0
            )
        """)
        # Safe migration — adds is_admin column if upgrading an old DB
        try:
            c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists, fine

        # ITINERARIES
        c.execute("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                email  TEXT,
                places TEXT,
                events TEXT,
                food   TEXT,
                dates  TEXT,
                UNIQUE(email, dates, places, events, food)
            )
        """)

        # LIVE EVENTS
        c.execute("""
            CREATE TABLE IF NOT EXISTS live_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                venue       TEXT,
                event_date  TEXT,
                time        TEXT,
                image_url   TEXT,
                detail_id   TEXT UNIQUE
            )
        """)

        # EVENT REQUESTS
        c.execute("""
            CREATE TABLE IF NOT EXISTS event_requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                description TEXT,
                created_by  TEXT,
                is_approved INTEGER DEFAULT 0
            )
        """)

        conn.commit()

        # ── Seed admin account ──────────────────────────────────────────────
        # INSERT OR IGNORE — only creates admin if not already there.
        # Does NOT delete/reset on every restart (safe for production).
        admin_hash = hash_pw("admin123@")
        c.execute(
            "INSERT OR IGNORE INTO users (email, password, is_admin) VALUES (?, ?, 1)",
            ("admin@surat.com", admin_hash)
        )
        conn.commit()

        # ── Seed default live events (INSERT OR IGNORE prevents duplicates) ──
        default_events = [
            ("Bluffmaster Gujjubhai",
             "Gujarati comedy play full of twists & laughter.",
             "Sanjeev Kumar Auditorium", "2026-03-25", "9:30 PM",
             "images/event1.jpg", "gujjubhai"),
            ("Krishna – Radhe Se Ranbhumi Tak",
             "Mythology meets theatre in a grand show.",
             "Sanjeev Kumar Auditorium", "2026-04-17", "7:30 PM",
             "images/event2.avif", "krishna-show"),
            ("Gujaratipanu",
             "Relatable Gujarati stand-up comedy.",
             "Osari", "2026-04-04", "8:00 PM",
             "images/event3.jpg", "amit-khuva"),
            ("Usha Uthup Live",
             "Iconic voice with electrifying performance.",
             "Jambna Party Plot", "2026-04-04", "7:00 PM",
             "images/event4.jpg", "usha-uthup"),
            ("Acting Workshop (Kids)",
             "Fun acting & creativity session for kids.",
             "Unvind Studio", "2026-03-22", "5:00 PM",
             "images/event5.jpg", "kids-acting"),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO live_events
                (title, description, venue, event_date, time, image_url, detail_id)
            VALUES (?,?,?,?,?,?,?)
        """, default_events)

        # Fix any existing events with wrong image_url
        for ev in default_events:
            c.execute("""
                UPDATE live_events SET image_url=?, title=?, description=?, venue=?, event_date=?, time=?
                WHERE detail_id=?
            """, (ev[5], ev[0], ev[1], ev[2], ev[3], ev[4], ev[6]))

        conn.commit()

create_tables()


# ─── TEST ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({"message": "Surat Tourism API running 🚀"})


# ─── AUTH ────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["POST"])
def login():
    try:
        data     = request.json or {}
        email    = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        hashed = hash_pw(password)

        with connect_db() as conn:
            c = conn.cursor()
            # Accepts both hashed passwords and legacy plain-text (backwards compat)
            c.execute(
                "SELECT id, email, is_admin FROM users WHERE email=? AND (password=? OR password=?)",
                (email, hashed, password)
            )
            user = c.fetchone()

        if user:
            return jsonify({
                "message":  "Login success",
                "email":    user[1],
                "is_admin": bool(user[2])
            })

        return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register():
    try:
        data     = request.json or {}
        email    = data.get("email", "").strip()
        password = data.get("password", "").strip()
        is_admin = 1 if data.get("is_admin") else 0

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        with connect_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
                (email, hash_pw(password), is_admin)
            )
            conn.commit()

        return jsonify({"message": "Account created", "email": email, "is_admin": bool(is_admin)})

    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with this email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── ITINERARIES ─────────────────────────────────────────────────────────────

@app.route("/plan-trip", methods=["POST"])
def plan_trip():
    try:
        data   = request.json or {}
        email  = data.get("email", "").strip()
        places = data.get("places", [])
        events = data.get("events", [])
        food   = data.get("food", [])
        dates  = data.get("dates", "").strip()

        if not email or not dates:
            return jsonify({"error": "Email and date required"}), 400

        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO itineraries (email, places, events, food, dates)
                VALUES (?, ?, ?, ?, ?)
            """, (email, json.dumps(places), json.dumps(events), json.dumps(food), dates))
            conn.commit()

        return jsonify({
            "message": "Plan saved ✅",
            "preview": {"email": email, "places": places, "events": events, "food": food, "dates": dates}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-plans", methods=["GET"])
def get_plans():
    try:
        email = request.args.get("email", "").strip()
        if not email:
            return jsonify({"error": "Email required"}), 400

        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, places, events, food, dates
                FROM itineraries WHERE email=? ORDER BY id DESC
            """, (email,))
            rows = c.fetchall()

        return jsonify([{
            "id":     r[0],
            "places": json.loads(r[1]),
            "events": json.loads(r[2]),
            "food":   json.loads(r[3]),
            "dates":  r[4]
        } for r in rows])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete-plan/<int:plan_id>", methods=["DELETE"])
def delete_plan(plan_id):
    try:
        email = (request.json or {}).get("email", "").strip()
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM itineraries WHERE id=? AND email=?", (plan_id, email))
            conn.commit()
        return jsonify({"message": "Plan deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── LIVE EVENTS ─────────────────────────────────────────────────────────────

@app.route("/live-events", methods=["GET"])
def get_live_events():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, title, description, venue, event_date, time, image_url, detail_id
                FROM live_events ORDER BY event_date ASC
            """)
            rows = c.fetchall()

        return jsonify([{
            "id": r[0], "title": r[1], "description": r[2],
            "venue": r[3], "event_date": r[4], "time": r[5],
            "image_url": r[6], "detail_id": r[7]
        } for r in rows])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/live-events", methods=["POST"])
def add_live_event():
    try:
        d     = request.json or {}
        title = d.get("title", "").strip()
        if not title:
            return jsonify({"error": "Title required"}), 400

        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO live_events (title, description, venue, event_date, time, image_url, detail_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                d.get("description", ""),
                d.get("venue", ""),
                d.get("event_date", ""),
                d.get("time", ""),
                d.get("image_url", "images/event1.jpg"),
                d.get("detail_id", title.lower().replace(" ", "-"))
            ))
            conn.commit()
            new_id = c.lastrowid

        return jsonify({"message": "Event added ✅", "id": new_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/live-events/<int:event_id>", methods=["PUT"])
def update_live_event(event_id):
    try:
        d = request.json or {}
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE live_events
                SET title=?, description=?, venue=?, event_date=?, time=?, image_url=?
                WHERE id=?
            """, (
                d.get("title"), d.get("description"), d.get("venue"),
                d.get("event_date"), d.get("time"), d.get("image_url"), event_id
            ))
            conn.commit()
        return jsonify({"message": "Event updated ✅"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/live-events/<int:event_id>", methods=["DELETE"])
def delete_live_event(event_id):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM live_events WHERE id=?", (event_id,))
            conn.commit()
        return jsonify({"message": "Event deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── EVENT REQUESTS ───────────────────────────────────────────────────────────

@app.route("/submit-event", methods=["POST"])
def submit_event():
    try:
        d          = request.json or {}
        title      = d.get("title", "").strip()
        created_by = d.get("email", "").strip()
        if not title or not created_by:
            return jsonify({"error": "Title and email required"}), 400

        with connect_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO event_requests (title, description, created_by) VALUES (?, ?, ?)",
                (title, d.get("description", ""), created_by)
            )
            conn.commit()

        return jsonify({"message": "Request submitted ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-requests", methods=["GET"])
def get_requests():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, title, description, created_by, is_approved
                FROM event_requests ORDER BY id DESC
            """)
            rows = c.fetchall()

        return jsonify([{
            "id": r[0], "title": r[1], "description": r[2],
            "created_by": r[3], "is_approved": bool(r[4])
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/approve-event/<int:req_id>", methods=["POST"])
def approve_event(req_id):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("UPDATE event_requests SET is_approved=1 WHERE id=?", (req_id,))
            c.execute(
                "SELECT title, description FROM event_requests WHERE id=?", (req_id,)
            )
            row = c.fetchone()
            if row:
                c.execute("""
                    INSERT INTO live_events
                        (title, description, venue, event_date, time, image_url, detail_id)
                    VALUES (?, ?, 'TBD', 'TBD', 'TBD', 'images/event1.jpg', ?)
                """, (row[0], row[1], row[0].lower().replace(" ", "-")))
            conn.commit()

        return jsonify({"message": "Event approved and published ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reject-event/<int:req_id>", methods=["DELETE"])
def reject_event(req_id):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM event_requests WHERE id=?", (req_id,))
            conn.commit()
        return jsonify({"message": "Request rejected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── ADMIN UTILS ──────────────────────────────────────────────────────────────

@app.route("/get-users", methods=["GET"])
def get_users():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("SELECT id, email, is_admin FROM users ORDER BY id")
            rows = c.fetchall()
        return jsonify([{"id": r[0], "email": r[1], "is_admin": bool(r[2])} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/cleanup-events")
def cleanup_events():
    """One-time GET route to clean duplicate events — delete after use"""
    try:
        with connect_db() as conn:
            c = conn.cursor()
            # Delete all, then reseed via INSERT OR IGNORE
            c.execute("DELETE FROM live_events")
            c.execute("DELETE FROM sqlite_sequence WHERE name='live_events'")
            default_events = [
                ("Bluffmaster Gujjubhai", "Gujarati comedy play full of twists & laughter.",
                 "Sanjeev Kumar Auditorium", "2026-03-25", "9:30 PM", "images/event1.jpg", "gujjubhai"),
                ("Krishna - Radhe Se Ranbhumi Tak", "Mythology meets theatre in a grand show.",
                 "Sanjeev Kumar Auditorium", "2026-04-17", "7:30 PM", "images/event2.avif", "krishna-show"),
                ("Gujaratipanu", "Relatable Gujarati stand-up comedy.",
                 "Osari", "2026-04-04", "8:00 PM", "images/event3.jpg", "amit-khuva"),
                ("Usha Uthup Live", "Iconic voice with electrifying performance.",
                 "Jambna Party Plot", "2026-04-04", "7:00 PM", "images/event4.jpg", "usha-uthup"),
                ("Acting Workshop (Kids)", "Fun acting & creativity session for kids.",
                 "Unvind Studio", "2026-03-22", "5:00 PM", "images/event5.jpg", "kids-acting"),
            ]
            c.executemany("""
                INSERT OR IGNORE INTO live_events
                    (title, description, venue, event_date, time, image_url, detail_id)
                VALUES (?,?,?,?,?,?,?)
            """, default_events)
            conn.commit()
        return jsonify({"message": "Events cleaned and reseeded ✅", "count": 5})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── RUN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)