from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class DatingProfileUpdate(BaseModel):
    opt_in_dating: bool = True
    headline: Optional[str] = Field(None, max_length=120)
    bio: Optional[str] = Field(None, max_length=1000)
    interests: Optional[str] = Field("Reading, Queer Cinema, Art", max_length=500)
    intent: Optional[str] = Field("Friendship & Dating", max_length=50)
    looking_for: Optional[str] = Field("Open to all queer folks", max_length=255)
    safety_boundary_note: Optional[str] = Field("Take things slow, anonymous chat first", max_length=255)
    approx_city: Optional[str] = Field("All India", max_length=64)

class DatingProfileOut(BaseModel):
    id: int
    user_anon_id: str
    user_alias: str
    user_pronouns: str
    opt_in_dating: bool
    headline: Optional[str]
    bio: Optional[str]
    interests: str
    intent: str
    looking_for: str
    safety_boundary_note: str
    approx_city: str
    created_at: datetime

    class Config:
        from_attributes = True
