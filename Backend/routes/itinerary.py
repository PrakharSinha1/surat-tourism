from flask import Blueprint, request, jsonify
from services.mail_service import send_email
from models import connect_db

itinerary_bp = Blueprint('itinerary', __name__)

@itinerary_bp.route('/plan-trip', methods=['POST'])
def plan_trip():
    try:
        data = request.json

        email = data.get("email")
        places = data.get("places", [])
        events = data.get("events", [])
        food = data.get("food", [])
        dates = data.get("dates")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # 💾 SAVE TO DB
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO itineraries (email, places, events, food, dates)
        VALUES (?, ?, ?, ?, ?)
        """, (
            email,
            ",".join(places),
            ",".join(events),
            ",".join(food),
            dates
        ))

        conn.commit()
        conn.close()

        preview = {
            "places": places,
            "events": events,
            "food": food,
            "dates": dates
        }

        # 📧 SEND EMAIL
        #send_email(email, preview)

        return jsonify({
            "message": "Itinerary planned successfully ✅",
            "preview": preview
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500