import sys
import os
import bcrypt
import random
from datetime import datetime, timedelta, UTC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import get_db

app = create_app()

INCIDENTS = [
    ("Database Connection Timeout", "Production DB failing intermittently", "Critical", "Closed"),
    ("API Gateway 503 Errors", "Gateway returning 503 under load", "High", "Closed"),
    ("Memory Leak in Worker Service", "Worker RAM usage growing over time", "High", "In Progress"),
    ("SSL Certificate Expiry Warning", "Cert expires in 14 days", "Medium", "Open"),
    ("Login Page Slow Response", "Login taking 8+ seconds", "Medium", "Closed"),
    ("Failed Backup Job", "Nightly backup did not complete", "High", "Closed"),
    ("Disk Space Warning on Server 2", "Disk at 87% capacity", "Medium", "Open"),
    ("Email Notifications Not Sending", "SMTP service unresponsive", "High", "In Progress"),
    ("Unauthorized Access Attempt", "Multiple failed logins from unknown IP", "Critical", "Closed"),
    ("CDN Cache Invalidation Failure", "Stale assets being served", "Low", "Closed"),
    ("Payment Gateway Timeout", "Stripe webhooks timing out", "Critical", "Closed"),
    ("DNS Resolution Failure", "Internal DNS intermittently failing", "High", "Closed"),
    ("Report Generation Stuck", "PDF export hanging indefinitely", "Low", "Open"),
    ("Mobile App Crash on Login", "iOS app crashing for some users", "High", "In Progress"),
    ("Search Index Out of Sync", "Search returning stale results", "Medium", "Closed"),
    ("Rate Limiter False Positives", "Legit users getting 429s", "Medium", "Open"),
    ("File Upload Size Limit Error", "Uploads failing above 2MB", "Low", "Closed"),
    ("Queue Worker Stopped", "Background jobs not processing", "Critical", "Closed"),
    ("Third Party API Degraded", "Weather API returning slow responses", "Low", "Open"),
    ("Two Factor Auth Bypass Report", "Security researcher reported potential bypass", "Critical", "In Progress"),
]

with app.app_context():
    db = get_db()
    cursor = db.cursor()
    now = datetime.now(UTC)

    hashed_pw = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    # ---- Cleanup first — order matters ----
    cursor.execute("DELETE FROM incident_events")  # delete events first
    db.commit()
    cursor.execute("DELETE FROM incidents")  # then incidents
    db.commit()
    cursor.execute("DELETE FROM users WHERE email = %s", ("test@test.com",))
    db.commit()
    print("Cleaned up existing data.")

    # ---- Default superuser ----
    cursor.execute("DELETE FROM users WHERE email = %s", ("test@test.com",))
    db.commit()

    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
        ("Test User", "test@test.com", hashed_pw, "superuser", now.isoformat(), now.isoformat())
    )
    db.commit()
    print("Superuser 'Test User' created successfully.")

    # After inserting the user, get their actual ID:
    cursor.execute("SELECT id FROM users WHERE email = %s", ("test@test.com",))
    user_id = cursor.fetchone()["id"]

    # ---- Sample incidents ----
    for title, description, severity, status in INCIDENTS:
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = (now - timedelta(days=days_ago, hours=hours_ago)).isoformat()
        updated_at = (now - timedelta(days=max(days_ago - 1, 0))).isoformat()

        cursor.execute("""
            INSERT INTO incidents 
            (title, description, severity, status, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, description, severity, status, user_id, created_at, updated_at))

    db.commit()
    print(f"Seeded {len(INCIDENTS)} sample incidents.")