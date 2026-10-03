from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ConnectionRequestCreate(BaseModel):
    receiver_anon_id: str = Field(..., description="Target user's anonymous ID")
    intro_note: Optional[str] = Field(None, max_length=280, description="Respectful short introduction note")
    intent: Optional[str] = Field("Friendship", description="Friendship, Mentorship, Dating, Advice")

class ConnectionRequestOut(BaseModel):
    id: int
    request_id: str
    sender_anon_id: str
    sender_alias: str
    sender_pronouns: str
    receiver_anon_id: str
    intro_note: Optional[str]
    intent: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    is_sensitive: Optional[bool] = False

class MessageOut(BaseModel):
    id: int
    message_id: str
    sender_alias: str
    sender_anon_id: str
    content: str
    is_sensitive: bool
    is_self: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ConnectionOut(BaseModel):
    id: int
    connection_id: str
    peer_anon_id: str
    peer_alias: str
    peer_pronouns: str
    peer_city: str
    is_active: bool
    i_revealed_identity: bool
    peer_revealed_identity: bool
    mutual_reveal_active: bool
    created_at: datetime
    last_message_at: datetime

    class Config:
        from_attributes = True

class IdentityRevealUpdate(BaseModel):
    reveal: bool = True
