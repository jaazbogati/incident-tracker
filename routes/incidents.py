from flask import Blueprint, request, g
from database import get_db
from validators import *
from auth import token_required, roles_required 
from datetime import datetime, UTC
from flask import abort
from flasgger import swag_from
from utils.responses import success_response, error_response
from services.incident_service import create_incident, get_incident_by_id, update_incident_service, delete_incident_service, restore_incident_service, list_incidents_service
from extensions import limiter


incidents_bp = Blueprint("incidents", __name__)

#*************End point to retrieve incidents by Id**************
@incidents_bp.route("/<int:incident_id>", methods=["GET"])
@token_required
@limiter.limit("60 per minute")
@swag_from({
    "tags": ["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "incident_id",
            "in": "path",
            "required": True,
            "type": "integer"
        }
    ],
    "responses": {
        "200": {
            "description": "Incident retrieved successfully"
        },
        "404": {
            "description": "Incident not found"
        }
    }
})
def get_incident(incident_id):
    
    """
    GET incident by ID
    """
   

    incident = get_incident_by_id(incident_id)

    return success_response(incident, 200)

#*************End point to list incidents with optional filters**************
@incidents_bp.route("", methods=["GET"])
@token_required
@limiter.limit("60 per minute")
@swag_from({
    "tags": ["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "status",
            "in": "query",
            "type": "string"
        },
        {
            "name": "severity",
            "in": "query",
            "type": "string"
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer"
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer"
        }
    ],
    "responses": {
        "200": {
            "description": "List of incidents retrieved successfully"
        }
    }
})
def list_incidents():

    """
    List incidents
    """

    filters = {
        "status": request.args.get("status"),
        "severity": request.args.get("severity"),
        "limit": request.args.get("limit", type=int),
        "offset": request.args.get("offset", type=int),
        "include_deleted": request.args.get("include_deleted")
    }

    result = list_incidents_service(
        filters=filters,
        user=g.user)

    return success_response(result, 200)

#******API endpoint to create a new incident****
@incidents_bp.route("", methods=["POST"])
@token_required
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "severity": {
                        "type": "string",
                        "example": "High"
                    }
                }
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Incident created successfully"
        }
    }
})
def create_incident_api():
    """
    Create a new incident
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("Invalid JSON Body", 400)     

        error = validate_required_fields(data, ["title", "description", "severity"]) #validate required fields  
        if error:
            return error_response(error, 400)
        
        incident = create_incident(data, g.user["id"])

        return success_response(incident, 201) 

    except Exception as e:
        print("ERROR:", str(e))
        raise
  
    
#******API endpoint to update incident status****
#Patch method allows partial updates, so we only require the status field in the request body. We also added a debugging print statement to check the raw data received from the client.

@incidents_bp.route("/<int:incident_id>", methods=["PATCH"])
@token_required
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "incident_id",
            "in": "path",
            "required": True,
            "type": "integer",
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "severity": {"type": "string"},
                    "status": {"type": "string"}, 
                }
            }       
        }
    ],
        
    "responses": {
        "200": {
            "description": "Incident updated successfully"}
    }
})
def update_incident(incident_id):
    """
    Update an incident
    """

    data = request.get_json()

    result = update_incident_service(
            incident_id=incident_id, 
            data=data, 
            user_id=g.user["id"])
    
    return success_response(result, 200)

#******API endpoint to delete an incident****
@incidents_bp.route("/<int:incident_id>", methods=["DELETE"])
@token_required
@roles_required("admin") #only admin can delete
@swag_from({
    "tags":["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "incident_id",
            "in": "path",
            "type": "integer",
            "required": "true"
        }
    ],  
    "responses": {
        "200": {
            "description": "Incident deleted successfully"
        }
    }
        
})
def delete_incident(incident_id):  
    """
    Delete an incident
    ---
   
    """

    result = delete_incident_service(incident_id, g.user["id"])

    return success_response(result, 200)

#******Restore point********
@incidents_bp.route("/<int:incident_id>/restore", methods=["POST"])
@token_required
@roles_required("superuser") #only superuser can restore
@limiter.limit("10 per minute")
@swag_from({
    "tags": ["Incidents"],
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "incident_id",
            "in": "path",
            "required": True,
            "type": "integer"
        }
        
    ],  
    "responses": {
        "200": {
            "description": "Incident restored successfully"
        }        
    }
        
})
def restore_incident(incident_id):
    """
    Restore incident
    ---
   
    """

    result = restore_incident_service(incident_id, g.user["id"])
    
    return success_response(result, 200)

