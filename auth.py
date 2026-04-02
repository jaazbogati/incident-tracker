from functools import wraps
import jwt
from flask import request, jsonify, g 
from database import get_db
from flask import current_app
from utils.exceptions import AuthenticationError, AuthorizationError
from utils.responses import success_response, error_response

#---------Token Authorization Check Decorator--------------


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Token missing")
        
        parts = auth_header.split(" ")
        if len(parts) != 2:
            raise AuthenticationError("Invalid token format")
        
        token = parts[1]

        try:    
            data = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

            user_id = data.get("user_id")
            if not user_id:
                raise AuthenticationError("Invalid token: user_id missing")

            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = %s AND is_active = 1",
                (user_id,)
            )
            user = cursor.fetchone()

            if not user:
                raise AuthenticationError("User not found or inactive")
            
            if data.get("token_version") != user["token_version"]:
                raise AuthenticationError("Token has been revoked")
            
            g.user = dict(user)
     
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

        
        return f(*args, **kwargs)
    
    return decorated


def roles_required(*required_roles):
    required_roles = {r.lower() for r in required_roles}
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, "user") or g.user["role"].lower() not in required_roles:
                raise AuthorizationError("Forbidden: insufficient permissions")
            return f(*args, **kwargs)
        return decorated
    return decorator