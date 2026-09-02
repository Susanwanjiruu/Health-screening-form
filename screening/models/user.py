from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
  
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True) 
    telephone = Column(String(20), nullable=True)
    designation = Column(String(50), nullable=True)      
    role = Column(String(20), nullable=False, default="Provider")  
    status = Column(String(20), nullable=False, default="Pending")  

   
    facility_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=True)

  
    is_email_verified = Column(Boolean, default=False)
    email_verification_code = Column(String(6), nullable=True)
    email_verification_code_expires_at = Column(DateTime, nullable=True)

   
    login_otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

 
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    facility = relationship("Facility", back_populates="staff", foreign_keys=[facility_id])
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("SecurityAuditLog", back_populates="admin_user")


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(500), nullable=False, unique=True)
    is_blacklisted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    action_performed = Column(String(100), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    target_beneficiary_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    admin_user = relationship("User", back_populates="audit_logs")
