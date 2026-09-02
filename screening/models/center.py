from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


class CenterProfile(Base):
  
    __tablename__ = "center_profile"

    center_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    region = Column(String(100), nullable=False)
    contact_info = Column(String(255), nullable=True)
    head_admin_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
