import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

def generate_uuid_str():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    anon_id = Column(String(64), unique=True, index=True, default=generate_uuid_str)
    alias = Column(String(64), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    pronouns = Column(String(32), default="they/them")
    identity_tags = Column(String(255), default="Queer")
    city = Column(String(64), default="All India")
    closet_pin = Column(String(8), default="1234")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    dating_profile = relationship("DatingProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, default=generate_uuid_str)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_masked = Column(String(64), nullable=True)  # Privacy: stored as truncated/masked CIDR
    refresh_token_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")
