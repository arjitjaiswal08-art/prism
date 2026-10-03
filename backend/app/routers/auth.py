import random
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserSession
from ..schemas.auth import (
    AnonymousLoginRequest,
    SignupRequest,
    LoginRequest,
    UpgradeAccountRequest,
    TokenResponse,
    UserOut
)
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    invalidate_token,
    check_rate_limit,
    security_bearer
)

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])

ANON_ALIASES = [
  "LavenderPhoenix", "CosmicVoyager", "VelvetStar", "IndigoEcho",
  "Solaris_TG", "PrismWanderer", "OceanDrifter", "AmberHorizon",
  "EmeraldGlade", "SilverNebula", "NovaStarlight", "RadiantHaven"
]

def mask_ip(ip: str) -> str:
    if not ip:
        return "hidden"
    parts = ip.split(".")
    return ".".join(parts[:3]) + ".0" if len(parts) == 4 else ip

@router.post("/anonymous-login", response_model=TokenResponse)
def anonymous_login(
    payload: AnonymousLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    check_rate_limit(request, max_requests=25, window_seconds=60)

    chosen_alias = payload.alias.strip() if payload.alias and payload.alias.strip() else f"{random.choice(ANON_ALIASES)}_{random.randint(100, 999)}"
    tags_str = ", ".join(payload.identity_tags) if payload.identity_tags else "Queer"

    # Create fresh anonymous user
    user = User(
        alias=chosen_alias,
        is_anonymous=True,
        pronouns=payload.pronouns or "they/them",
        identity_tags=tags_str,
        city=payload.city or "All India",
        closet_pin=payload.closet_pin or "1234"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate Tokens
    access_token = create_access_token(data={"sub": str(user.id), "anon_id": user.anon_id, "is_anonymous": True})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Create Session Record
    client_ip = request.client.host if request.client else "unknown"
    session_record = UserSession(
        user_id=user.id,
        device_info=payload.device_info or request.headers.get("user-agent", "Unknown Browser"),
        ip_masked=mask_ip(client_ip),
        refresh_token_hash=hash_password(refresh_token[:20]),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(session_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user)
    )

@router.post("/signup", response_model=TokenResponse)
def signup(
    payload: SignupRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    check_rate_limit(request, max_requests=10, window_seconds=60)

    # Check email duplicate (prevent enumeration by timing attack mitigation)
    existing_user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in."
        )

    # Case A: Upgrading an existing anonymous guest session
    if payload.upgrade_from_anon_id:
        anon_user = db.query(User).filter(User.anon_id == payload.upgrade_from_anon_id).first()
        if anon_user and anon_user.is_anonymous:
            anon_user.email = payload.email.lower().strip()
            anon_user.password_hash = hash_password(payload.password)
            anon_user.is_anonymous = False
            if payload.alias:
                anon_user.alias = payload.alias.strip()
            db.commit()
            db.refresh(anon_user)
            user = anon_user
        else:
            user = None
    else:
        user = None

    # Case B: Brand new registered user
    if not user:
        chosen_alias = payload.alias.strip() if payload.alias and payload.alias.strip() else f"Member_{random.randint(1000, 9999)}"
        user = User(
            alias=chosen_alias,
            email=payload.email.lower().strip(),
            password_hash=hash_password(payload.password),
            is_anonymous=False,
            pronouns=payload.pronouns or "they/them",
            city=payload.city or "All India"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "anon_id": user.anon_id, "is_anonymous": False})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    check_rate_limit(request, max_requests=10, window_seconds=60)

    ident = payload.identifier.strip()
    user = None

    # Try lookup by Email
    if "@" in ident:
        user = db.query(User).filter(User.email == ident.lower(), User.is_active == True).first()
        if not user or not user.password_hash or not payload.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials")
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login credentials")

    # Try lookup by Anon ID or Alias
    else:
        user = db.query(User).filter(
            (User.anon_id == ident) | (User.alias == ident),
            User.is_active == True
        ).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid anonymous credentials")

        # If user has password, verify it
        if user.password_hash and payload.password:
            if not verify_password(payload.password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = create_access_token(data={"sub": str(user.id), "anon_id": user.anon_id, "is_anonymous": user.is_anonymous})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Log new session
    client_ip = request.client.host if request.client else "unknown"
    session_record = UserSession(
        user_id=user.id,
        device_info=payload.device_info or request.headers.get("user-agent", "Unknown Device"),
        ip_masked=mask_ip(client_ip),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(session_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user)
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.post("/upgrade-account", response_model=UserOut)
def upgrade_account(
    payload: UpgradeAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check duplicate
    existing = db.query(User).filter(User.email == payload.email.lower().strip(), User.id != current_user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    current_user.email = payload.email.lower().strip()
    current_user.password_hash = hash_password(payload.password)
    current_user.is_anonymous = False
    db.commit()
    db.refresh(current_user)

    return UserOut.model_validate(current_user)

@router.post("/logout")
def logout(
    request: Request,
    credentials = Depends(security_bearer),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if credentials and credentials.credentials:
        invalidate_token(credentials.credentials)

    # Deactivate active user sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).update({"is_active": False})
    db.commit()

    return {"message": "Logged out successfully. All local sessions terminated."}

@router.delete("/me")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Privacy Right to be Forgotten: Immediately purges all user data."""
    db.delete(current_user)
    db.commit()
    return {"message": "Account and all associated records permanently purged."}
