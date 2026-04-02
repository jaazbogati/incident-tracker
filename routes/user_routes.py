from flask import Blueprint, request, g, jsonify
from datetime import datetime, UTC
from auth import token_required, roles_required
from services.user_services import change_user_role_service, create_user_service, list_users_service, deactivate_user_service
from utils.responses import success_response, error_response
from flasgger import swag_from

user_bp = Blueprint("users", __name__)
#********Update for role**************************

@user_bp.route("", methods=["POST"])
@token_required
@swag_from({
    "tags": ["Users"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "username": {"type": "string", "example": "john"},
                    "email": {"type": "string", "example": "john@test.com"},
                    "password": {"type": "string", "example": "password123"},
                    "role": {"type": "string", "example": "user"}
                }
            }
        }
    ],
    "responses": {
        "201": {"description": "User created successfully"},
        "403": {"description": "Forbidden"}
    }
})
def create_user():
    data = request.get_json()
    result = create_user_service(data)
    return success_response(result, 201)

@user_bp.route("", methods=["GET"])
@token_required
@roles_required("admin", "superuser")
@swag_from({
    "tags": ["Users"],
    "security": [{"Bearer": []}],
    "responses": {
        "200": {"description": "List users"}
    }
})
def list_users():
    result = list_users_service()
    return success_response(result, 200)

@user_bp.route("/<int:user_id>/role", methods=["PATCH"])
@token_required
@roles_required("superuser")# Only Super-user can modify
@swag_from({
    "tags": ["Users"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["role"],
                "properties": {
                    "role": {
                        "type": "string",
                        "example": "admin"
                    }   
                }   
            }  
        }
    ],     
    "responses":{
        "200": {"description": "Role updated successfully"}
    }    
})
def change_user_role(user_id):
    data = request.get_json()
    result = change_user_role_service(user_id, data)
    return success_response(result, 200)

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@token_required
@roles_required("superuser")# Only Super-user can modify
@swag_from ({
    "tags": ["User"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True
        }
    ],
    "responses": {
        "200": {"description": "User deactivation"}
    }
})
def deactivate_user(user_id):
    result = deactivate_user_service(user_id)
    return success_response(result, 200)