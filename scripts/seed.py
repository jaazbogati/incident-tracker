import sys
import os

import bcrypt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from app import create_app
from datetime import datetime, UTC

app = create_app()

with app.app_context():
    db = get_db()
    cursor = db.cursor()
    now = datetime.now(UTC).isoformat()
    # Create a test user
    hashed_pw = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute("DELETE FROM users WHERE email = %s", ("test@test.com",))
    db.commit()

    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
        ("Test User", "test@test.com", hashed_pw, "superuser", now, now)
    )
    db.commit()
    print("Superuser 'Test User' created successfully.")