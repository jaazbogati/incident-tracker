from utils.exceptions import AppError, NotFoundError
from services.event_service import log_event
from utils.constants import ROLES
from database import get_db
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor
from flask import g
import bcrypt




def create_user_service(data):
    if g.user["role"] != "superuser":
        raise AppError("Only superuser can create users", 403)
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")
    
    if not email or not password:
        raise AppError("Email and password are required", 400)
    
    if not isinstance(email, str) or "@" not in email or "." not in email:
            raise AppError("Invalid email format", 400)

    if not username:
        username = email.split("@")[0]

    if role not in ROLES:
        raise AppError(f"Invalid role: {role}", 400)

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_pw = hashed_pw.decode("utf-8")
    now = datetime.now(UTC).isoformat()

    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        raise AppError("User already exists", 400)

    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (username, email, hashed_pw, role, now, now))

    row = cursor.fetchone()
    user_id = row["id"]
    db.commit()

    log_event(
        None,
        "USER_CREATED",
        None,
        f"User {email} created",
        g.user["id"]
    )

    return {
        "id": user_id,
        "email": email,
        "username": username,
        "role": role   
    }

def list_users_service():
    if g.user["role"] not in ["admin", "superuser"]:
        raise AppError("Only registered users can view users", 403)
    
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT id, email, role, is_active, created_at FROM users
        ORDER BY created_at DESC
    """)

    users = cursor.fetchall()
    return [dict(user) for user in users]


def change_user_role_service(user_id, data):
    if g.user["role"] != "superuser":
        raise AppError("Only superuser can change roles", 403)
    
    role = data.get("role")

    if role not in ROLES:
        raise AppError(f"Invalid role: {role}. Valid roles are: {', '.join(ROLES)}")
    
    now = datetime.now(UTC).isoformat()
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        UPDATE users
        SET role = %s, updated_at = %s
        WHERE id = %s AND is_active = 1
    """, (role, now, user_id))

    if cursor.rowcount == 0:
        raise NotFoundError("User not found or inactive")

    db.commit()

    log_event(
        None,
        "USER_ROLE_CHANGED",
        None,
        f"Role changed to {role}",
        user_id
    )
    return {"updated_user_id": user_id, "new_role": role}

def deactivate_user_service(user_id):
    if g.user["role"] != "superuser":
        raise AppError("Only superusers can deactivate users", 403)
    
    now = datetime.now(UTC).isoformat()
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        UPDATE users SET is_active = 0, updated_at = %s
        WHERE id = %s AND is_active = 1
    """, (now, user_id))

    if cursor.rowcount == 0:
        raise NotFoundError("User not found or already inactive")

    db.commit()

    log_event(
        None,
        "USER_DEACTIVATED",
        None,
        "User deactivated",
        user_id
    )

    return{"deactivated_user_id": user_id}
    

    