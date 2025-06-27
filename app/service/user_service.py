from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash
from app.repositories import user_repository
from app.models.user_model import User

def login_user(db: Session, email: str, password: str):
    user = user_repository.get_user_by_email(db, email)
    if user and check_password_hash(user.password, password):
        return user
    return None

def register_user(db: Session, username: str, email: str, password: str):
    if user_repository.get_user_by_username(db, username):
        return None
    hashed = generate_password_hash(password)
    return user_repository.create_user(db, username, email, hashed)

