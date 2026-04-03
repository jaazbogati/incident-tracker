#=======IMPORTS========

import logging
import os
import uuid
from flask import Flask, g, request, render_template
from datetime import datetime, UTC

import config
from routes.incidents import incidents_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.events_routes import events_bp

from database import close_db
from config import Config
from flasgger import Swagger
from flask import has_request_context

from utils.exceptions import AppError
from extensions import limiter
from utils.responses import error_response
from utils.logger import JSONFormatter
from flask_cors import CORS

#======App Setup/Config======
def create_app():

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "https://incident-tracker-ui.onrender.com"], 
    "methods": ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}}) # Enable CORS for API routes

    if __name__ != "__main__":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    
    app.config.from_object(config.Config) #load config from Config class in config.py


    limiter.init_app(app)

    Swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Incident Management API",
            "description": "Professional Incident Management API",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: Bearer <your_token>"
            }
        }
    }

    Swagger(app, template=Swagger_template)

    @app.route("/")
    def home():
        return render_template("index.html")

    def setup_logging(app):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        
        app.logger.handlers = []
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    setup_logging(app)

    @app.before_request
    def start_timer():
        g.request_id  = str(uuid.uuid4())  # Generate a unique request ID for tracing
        g.start_time = datetime.now(UTC)

    @app.after_request
    def log_request(response):
        duration = round((datetime.now(UTC) - g.start_time).total_seconds() * 1000)  # Convert to milliseconds
        app.logger.info(
            "request completed",
            extra={
                "status": response.status_code,
                "duration": duration
            }
        )
        response.headers["X-Request-ID"] = g.request_id
        return response
    
        
#------Global Error Handlers----------------

    @app.errorhandler(400)
    def handle_400(error):      
        return error_response("Bad request", 400)

    @app.errorhandler(401)
    def handle_401(error):      
        return error_response("Unauthorized access", 401)

    @app.errorhandler(403)
    def handle_403(error):
        return error_response("Access forbidden", 403)

    @app.errorhandler(404)
    def handle_404(error):
        return error_response("Endpoint not found", 404)

    @app.errorhandler(500)
    def handle_500(error):
        app.logger.error(f"Internal Server Error: {error}")
        return error_response("Internal server error", 500)


#------Custom AppError Handler----------------
    @app.errorhandler(AppError)
    def handle_app_error(error):
        app.logger.error("application error", extra={"error_message": error.message, "status_code": error.status_code})
        return error_response(error.message, error.status_code, request_id=g.get("request_id"))

#------Database Connection Handling----------------

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

#======Blueprint Registration======
    app.register_blueprint(incidents_bp, url_prefix="/api/v1/incidents") #register incidents blueprint

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth") #register auth blueprint    

    app.register_blueprint(user_bp, url_prefix="/api/v1/users") #register user blueprint

    app.register_blueprint(events_bp, url_prefix="/api/v1/events") #register events blueprintP

    return app  

#======Main Entry Point======

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)



