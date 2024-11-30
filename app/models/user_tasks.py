from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserTask(Base):
    __tablename__ = "user_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    status = Column(String, default='pending')  # Possible values: 'pending', 'completed'
    last_completed_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    task = relationship("Task", back_populates="users", lazy="joined")
