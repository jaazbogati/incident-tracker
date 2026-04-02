from flask import Blueprint, request, jsonify, g
from flask_cors import cross_origin
import bcrypt
import jwt
from datetime import datetime, timedelta, UTC
from extensions import limiter
from auth import token_required
from database import get_db
from flask import current_app  
from utils.exceptions import AuthenticationError, AuthorizationError, ValidationError
from utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__)


#******API endpoint to fetch all incidents in JSON format****

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()

    if not data:
        raise ValidationError("Invalid JSON Body")

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters")

    if not username or not email or not password:
        raise ValidationError("Username, email, and password are required")
    
    email = email.lower().strip()

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    hashed_pw = hashed_pw.decode("utf-8")

    db = get_db()
    now = datetime.now(UTC).isoformat()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        raise ValidationError("User already exists")

    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, email, hashed_pw, "user", now, now)
    )
    db.commit()

    return success_response({"message": "User registered successfully"}, 201)

#******API endpoint to login user and issue token****
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@cross_origin(origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)
def login():
    data = request.get_json()

    if not data:
        raise ValidationError("Invalid JSON Body")

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("Email and password are required")

    email = email.lower().strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        raise ValidationError("Invalid credentials")
    
#--------Check Lock-----------------------------
    if user["locked_until"]:
        if datetime.now(UTC) < datetime.fromisoformat(user["locked_until"]):
            raise AuthorizationError("Account locked due to multiple failed login attempts. Try again later.")
        
    if not bcrypt.checkpw(
        password.encode("utf-8"), 
        user["password_hash"].encode("utf-8")
    ):
    
        failed_attempts = user["failed_attempts"] + 1

        if failed_attempts >= 5:
            lock_until = datetime.now(UTC) + timedelta(minutes=15)
            cursor = db.cursor()
            cursor.execute(
                "UPDATE users SET failed_attempts = %s, locked_until = %s WHERE id = %s",
                (0, lock_until.isoformat(), user["id"])
            )
        else:
            cursor.execute(
                "UPDATE users SET failed_attempts = %s WHERE id = %s",
                (failed_attempts, user["id"])
            )

        db.commit()
        raise AuthenticationError("Invalid credentials")
    
    if not user["is_active"]:
        raise AuthorizationError("Account is deactivated")
    
#-------if password correct, reset attempts
    cursor.execute(
        "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = %s",
        (user["id"],)
    )
    db.commit()

#--------Issue token----------------------------
    token = jwt.encode(
        {
            "user_id": user["id"],
            "token_version": user["token_version"],
            "exp": datetime.now(UTC) + timedelta(hours=current_app.config["JWT_EXPIRATION_HOURS"])
        },
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return success_response({"token": token})

#******API endpoint to logout user by invalidating token by incrementing token_version in DB****  
@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    db = get_db()

    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET token_version = token_version + 1 WHERE id = %s",
        (g.user["id"],)
    )
    db.commit()

    return success_response({"message": "Logged out succesfully"}, 200)

