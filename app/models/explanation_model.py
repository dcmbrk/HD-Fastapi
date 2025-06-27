from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() 
class Explanation(Base):
    __tablename__ = "explanation"

    id = Column(Integer, primary_key=True, index=True)
    student_username = Column(String(80), nullable=False)
    student_email = Column(String(120), nullable=False)
    class_ = Column("class", String(100), nullable=False)
    lock_part = Column(String(200), nullable=False)
    reason = Column(Text, nullable=False)
    state = Column(String(20), default="pending")
    manager_username = Column(String(80), nullable=True)

