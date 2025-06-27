from sqlalchemy.orm import Session
from app.repositories import explanation_repository

def get_all_explanations(db: Session):
    return explanation_repository.get_all_explanations(db)

def create_explanation(db: Session, student_username: str, student_email: str, class_: str, lock_part: str, reason: str):
    return explanation_repository.create_explanation(db, student_username, student_email, class_, lock_part, reason)

def get_pending_explanations(db: Session):
    return explanation_repository.get_pending_explanations(db)

def process_application(db: Session, application_id: int, action: str, manager_username: str):
    explanation = explanation_repository.get_explanation_by_id(db, application_id)
    if explanation:
        if action == 'accept':
            explanation.state = 'accepted'
            explanation.manager_username = manager_username
        elif action == 'delice':
            explanation.state = 'delice'
            explanation.manager_username = manager_username
        db.commit()
        db.refresh(explanation)
    return explanation

