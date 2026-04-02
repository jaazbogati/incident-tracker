from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # General Configurations
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key') #default value for development
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://incident_user:strongpassword@localhost:5432/incident_tracker') #default path for development
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")   

    JWT_EXPIRATION_HOURS = 24 #default to 24 hour           