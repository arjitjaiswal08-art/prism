from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class AnonymousLoginRequest(BaseModel):
    alias: Optional[str] = Field(None, max_length=64, description="Optional chosen alias")
    pronouns: Optional[str] = Field("they/them", max_length=32)
    identity_tags: Optional[List[str]] = Field(default_factory=lambda: ["Queer"])
    city: Optional[str] = Field("All India", max_length=64)
    closet_pin: Optional[str] = Field("1234", max_length=8)
    device_info: Optional[str] = Field(None, max_length=255)

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    alias: Optional[str] = Field(None, max_length=64)
    pronouns: Optional[str] = Field("they/them", max_length=32)
    city: Optional[str] = Field("All India", max_length=64)
    upgrade_from_anon_id: Optional[str] = Field(None, description="If upgrading an existing anonymous guest session")

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Email OR Anonymous ID / Handle")
    password: Optional[str] = None
    recovery_key: Optional[str] = None
    device_info: Optional[str] = None

class UpgradeAccountRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserOut(BaseModel):
    id: int
    anon_id: str
    alias: str
    email: Optional[str] = None
    is_anonymous: bool
    pronouns: str
    identity_tags: str
    city: str
    closet_pin: str
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
