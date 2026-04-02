from flask import jsonify

def success_response(data=None, status_code=200, request_id=None):
    response = {"success": True, "data": data}
    if request_id is not None:
        response["request_id"] = request_id
    return jsonify(response), status_code

def error_response(message, status_code=400, request_id=None):
    response = {"success": False, "error": message}
    if request_id is not None:
        response["request_id"] = request_id
    return jsonify(response), status_code