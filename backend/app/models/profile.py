from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class DatingProfile(Base):
    __tablename__ = "dating_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    opt_in_dating = Column(Boolean, default=False)
    
    headline = Column(String(120), nullable=True)
    bio = Column(Text, nullable=True)
    interests = Column(String(500), default="Reading, Queer Cinema, Cafe Hopping")
    intent = Column(String(50), default="Friendship & Dating") # Dating, Friendship, Mentorship, Creative Collab
    looking_for = Column(String(255), default="Open to all queer folks")
    safety_boundary_note = Column(String(255), default="Take things slow, anonymous chat first")
    approx_city = Column(String(64), default="All India")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="dating_profile")
