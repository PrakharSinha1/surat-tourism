from flask import Blueprint, request, jsonify
from models import connect_db
from services.mail_service import send_admin_request

admin_bp = Blueprint('admin', __name__)

# 🔥 Request admin access
@admin_bp.route('/request-admin', methods=['POST'])
def request_admin():
    data = request.json
    email = data.get("email")

    send_admin_request(email)

    return jsonify({"msg": "Request sent to admin"})

from flask import Blueprint, request, jsonify
from models import connect_db

admin_bp = Blueprint("admin", __name__)

# 📥 GET PENDING REQUESTS
@admin_bp.route("/get-requests")
def get_requests():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, description FROM event_requests WHERE is_approved=0")
    rows = cursor.fetchall()

    conn.close()

    return jsonify([
        {"id": r[0], "title": r[1], "description": r[2]}
        for r in rows
    ])


# 📦 GET APPROVED
@admin_bp.route("/get-approved")
def get_approved():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, description FROM event_requests WHERE is_approved=1")
    rows = cursor.fetchall()

    conn.close()

    return jsonify([
        {"id": r[0], "title": r[1], "description": r[2]}
        for r in rows
    ])


# ✅ APPROVE
@admin_bp.route("/approve-event", methods=["POST"])
def approve_event():
    id = request.json.get("id")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE event_requests SET is_approved=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Approved"})


# ❌ REJECT
@admin_bp.route("/reject-event", methods=["POST"])
def reject_event():
    id = request.json.get("id")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM event_requests WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Rejected"})


# 🔄 REVOKE
@admin_bp.route("/revoke-event", methods=["POST"])
def revoke_event():
    id = request.json.get("id")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE event_requests SET is_approved=0 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Revoked"})
# ✅ Approve admin
@admin_bp.route('/approve-admin', methods=['POST'])
def approve_admin():
    data = request.json
    email = data.get("email")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users SET is_admin=1, is_approved=1 WHERE email=?
    """, (email,))

    conn.commit()
    conn.close()

    return jsonify({"msg": "User is now admin"})