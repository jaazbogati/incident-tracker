from database import get_db
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_db():
    db = get_db()

    with open('schema.sql', 'r') as f:
        db.execute(f.read())
    
    db.commit()
    print("Database initialized successfully")

if __name__ == '__main__':
    init_db()