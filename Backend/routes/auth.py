from flask import Blueprint, request, jsonify
from models import connect_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (email, password)
    VALUES (?, ?)
    """, (data["email"], data["password"]))

    conn.commit()
    conn.close()

    return jsonify({"msg": "User registered"})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT email, is_admin, is_approved FROM users
    WHERE email=? AND password=?
    """, (data["email"], data["password"]))

    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            "email": user[0],
            "is_admin": user[1],
            "is_approved": user[2]
        })

    return jsonify({"error": "Invalid credentials"})