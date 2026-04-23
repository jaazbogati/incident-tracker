from psycopg2.extras import RealDictCursor
from database import get_db
from datetime import datetime, UTC
from utils.exceptions import AppError, NotFoundError
from validators import normalize_status, normalize_severity, ALLOWED_STATUSES, ALLOWED_SEVERITIES
from services.event_service import log_event
from repositories.incident_repository import create_incident_record

# Service function to create a new incident, used by routes/incidents.py
def create_incident(data, user_id):
    
    now = datetime.now(UTC).isoformat()

    severity = normalize_severity(data["severity"])

    incident = create_incident_record(
        title=data["title"],
        description=data["description"],
        severity=severity,
        user_id=user_id,
        now=now
    )

    log_event(
        incident["id"], "INCIDENT_CREATED", None, f"Title: {data['title']}, Severity: {data['severity']}", user_id)

    # return {
    #     "id": incident_id,
    #     "title": data["title"],
    #     "description": data["description"],
    #     "severity": severity,
    #     "status": "Open"
    # }

    return incident

# Service function to list incidents with optional filters, used by routes/incidents.py
def list_incidents_service(filters, user):
    db = get_db()

    base_query = "SELECT * FROM incidents"
    count_query = "SELECT COUNT(*) as count FROM incidents"

    conditions = []
    values = []

    #*********Soft delete handling: only include non-deleted incidents unless include_deleted filter is set**********
    include_deleted = filters.get("include_deleted")

    if include_deleted == "true":
        if user["role"] != "admin":
            raise AppError("Only admin can view deleted incidents", 403)
    else:
        conditions.append("deleted_at IS NULL")

    #********Filtering by status**********

    if filters.get("status"):
        status = normalize_status(filters["status"])
        if status not in ALLOWED_STATUSES:
            raise AppError("Invalid status filter", 400)
        conditions.append("status = %s")
        values.append(status)

    #*********Filtering by severity**********
    if filters.get("severity"):
        severity = normalize_severity(filters["severity"])
        if severity not in ALLOWED_SEVERITIES:
            raise AppError("Invalid severity filter", 400)
        conditions.append("severity = %s")
        values.append(severity)

    #*********Build WHERE clause**********
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
        base_query += where_clause
        count_query += where_clause

    #*********Pagination Defaults***************
    limit = int(filters.get("limit") or 20)
    offset = int(filters.get("offset") or 0)

    if limit < 1 or limit > 100:
        raise AppError("Invalid limit. Please specify a value between 1 and 100.", 400)

    if offset < 0 :
        raise AppError("Invalid offset. Please specify a value between 0 and 100.", 400)

    base_query += " LIMIT %s OFFSET %s"
    values_with_pagination = values + [limit, offset]

    #*********Execute count query to get total number of matching incidents**********    
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    cursor.execute(base_query, values_with_pagination)
    incidents = cursor.fetchall()

    cursor.execute(count_query, values)
    total_count = cursor.fetchone()["count"]

    #*********Return results with pagination metadata**********
    incident_list = [dict(row) for row in incidents]

    return {
        "incidents": incident_list,
        "meta": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }     
    }

# Service function to fetch incident by ID, used by routes/incidents.py
def get_incident_by_id(incident_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM incidents WHERE id = %s AND deleted_at IS NULL",
        (incident_id,)
    )
    incident = cursor.fetchone()

    if not incident:
        raise NotFoundError("Incident not found")
    
    return dict(incident)

# Service function to update incident status, used by routes/incidents.py
def update_incident_service(incident_id, data, user_id):
    if not data:
        raise ValueError("No data provided for update")
    
    allowed_fields = ["title", "description", "severity", "status"] 

    updates = []
    values = []

    #Build update list dynamically + validation 
    for field, value in data.items():

        if field not in allowed_fields:
            raise ValueError(f"Unexpected field: {field}")

        if field == "status":
            value = normalize_status(value)
            if value not in ALLOWED_STATUSES:
                raise ValueError("Invalid status")
            
        elif field == "severity":
            value = normalize_severity(value)
            if value not in ALLOWED_SEVERITIES:
                raise ValueError("Invalid severity")
            
        elif field in ["title", "description"]:
            if not value.strip():
                raise ValueError(f"{field} cannot be empty")

        updates.append(f"{field} = %s")
        values.append(value)

    if not updates:
        raise ValueError("No valid fields provided for update")
    
    #Add audit tracking automatically
    now = datetime.now(UTC).isoformat()

    updates.append("updated_at = %s")
    updates.append("updated_by = %s")

    values.append(now)
    values.append(user_id)
    values.append(incident_id)
    
    db = get_db()

    query = f"""
        UPDATE incidents
        SET {', '.join(updates)}
        WHERE id = %s AND deleted_at IS NULL
    """

    cursor = db.cursor()
    cursor.execute(
        query, values
    )
    db.commit()
    
    log_event(
        incident_id, "INCIDENT_UPDATED", None, f"Fields updated: {', '.join(data.keys())}", user_id
    )

    if cursor.rowcount == 0:
        raise NotFoundError("Incident not found or deleted")

    return{
        "updated_id": incident_id, 
        "updated_at": now,
        "updated_by": user_id,
        "updated_fields": list(data.keys())
    }

#Services function to delete incident, used by routes/incidents.py
def delete_incident_service(incident_id, user_id):

    db = get_db()
    now = datetime.now(UTC).isoformat()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE incidents SET deleted_at = %s, deleted_by = %s WHERE id = %s AND deleted_at IS NULL", 
        (now, user_id, incident_id,)
    )
    db.commit()

    log_event(
        incident_id, "INCIDENT_DELETED", None, f"Incident soft-deleted", user_id
    )

    if cursor.rowcount == 0:
        raise NotFoundError("Incident not found or already deleted")

    return {
        "deleted_id": incident_id,
        "deleted_at": now,
        "deleted_by": user_id
    }

#Services function to retore incident, used by routes/incidents.py
def restore_incident_service(incident_id, user_id):
    db = get_db()

    now = datetime.now(UTC).isoformat()
    cursor = db.cursor()
    cursor.execute(
        """UPDATE incidents
        SET deleted_at = NULL,
        updated_at = %s,
        updated_by = %s
        WHERE id = %s AND deleted_at IS NOT NULL""",
        (now, user_id, incident_id,)
    )
    db.commit()

    log_event(
        incident_id, "INCIDENT_RESTORED", None, "Incident restored", user_id
    )

    if cursor.rowcount == 0:
        raise NotFoundError("Incident not found or not deleted")
    
    return{"restore_id": incident_id}


