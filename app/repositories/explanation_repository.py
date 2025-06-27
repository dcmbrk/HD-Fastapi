from sqlalchemy.orm import Session
from app.models.explanation_model import Explanation

def get_all_explanations(db: Session):
    return db.query(Explanation).all()

def create_explanation(db: Session, student_username: str, student_email: str, class_: str, lock_part: str, reason: str):
    new_explanation = Explanation(
        student_username=student_username,
        student_email=student_email,
        class_=class_,
        lock_part=lock_part,
        reason=reason
    )
    db.add(new_explanation)
    db.commit()
    db.refresh(new_explanation)
    return new_explanation

def get_pending_explanations(db: Session):
    return db.query(Explanation).filter(Explanation.state == 'pending').all()

def get_explanation_by_id(db: Session, explanation_id: int):
    return db.query(Explanation).filter(Explanation.id == explanation_id).first()

