from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() # Sử dụng Base riêng cho Explanation nếu bạn muốn tách biệt

class Explanation(Base):
    __tablename__ = "explanation"

    id = Column(Integer, primary_key=True, index=True)
    student_username = Column(String(80), nullable=False)
    student_email = Column(String(120), nullable=False)
    class_ = Column("class", String(100), nullable=False) # Đổi tên cột để tránh xung đột với từ khóa 'class'
    lock_part = Column(String(200), nullable=False)
    reason = Column(Text, nullable=False)
    state = Column(String(20), default="pending")
    manager_username = Column(String(80), nullable=True)

