from sqlalchemy.orm import Session
from app.db_config import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
