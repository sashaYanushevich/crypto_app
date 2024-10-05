from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base_class import Base  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tgID = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, index=True)
    region = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
