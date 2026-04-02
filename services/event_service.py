from database import get_db
from datetime import datetime, UTC

def log_event(incident_id, event_type, old_value, new_value, user_id):
    db = get_db()
    created_at = datetime.now(UTC).isoformat()

    if isinstance(user_id, dict):
        user_id = user_id.get("id")

    if isinstance(incident_id, dict):
        incident_id = incident_id.get("id")

    if not isinstance(user_id, (int, type(None))):
        raise ValueError("user_id must be an integer")

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO incident_events (incident_id, event_type, old_value, new_value, performed_by, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (incident_id, event_type, old_value, new_value, user_id, created_at)
    )
    db.commit()