from flask import Blueprint, request, jsonify, g
from auth import token_required
from database import get_db
from flasgger import swag_from
from utils.responses import success_response

events_bp = Blueprint("events", __name__)

@events_bp.route("", methods=["GET"])
@token_required
@swag_from({
    "tags": ["Audit Logs"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "incident_id",
            "in": "path",
            "type": "integer",
            "required": True
        }
    ],
    "responses": {
        "200": {"description": "Audit logs retrieved"}
    }
})
def list_events():

    if g.user["role"] not in ["admin", "superuser"]:
        return jsonify({"error": "Forbidden"}), 403

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM incident_events ORDER BY created_at DESC limit 100")
    events = cursor.fetchall()
    
    return jsonify({
        "success": True,
        "data": [dict(event) for event in events]
    }), 200
