from database import get_db

def create_incident_record(title, description, severity, user_id, now):
    db = get_db()

    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO incidents
        (title, description, severity, status, created_by, created_at, updated_at)
        VALUES (%s, %s, %s, 'Open', %s, %s, %s)
        RETURNING id, title, description, severity, status, created_by, created_at, updated_at
        """,
        (title, description, severity,user_id, now, now)
    )

    incident = cursor.fetchone()
    db.commit()
    return dict(incident)