from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.profile import DatingProfile
from ..schemas.dating import DatingProfileUpdate, DatingProfileOut
from ..security import get_current_user

router = APIRouter(prefix="/dating", tags=["Intentional Connection Mode"])

@router.get("/profile", response_model=Optional[DatingProfileOut])
def get_my_dating_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(DatingProfile).filter(DatingProfile.user_id == current_user.id).first()
    if not profile:
        return None
    return DatingProfileOut(
        id=profile.id,
        user_anon_id=current_user.anon_id,
        user_alias=current_user.alias,
        user_pronouns=current_user.pronouns,
        opt_in_dating=profile.opt_in_dating,
        headline=profile.headline,
        bio=profile.bio,
        interests=profile.interests,
        intent=profile.intent,
        looking_for=profile.looking_for,
        safety_boundary_note=profile.safety_boundary_note,
        approx_city=profile.approx_city,
        created_at=profile.created_at
    )

@router.post("/profile", response_model=DatingProfileOut)
def update_dating_profile(
    payload: DatingProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(DatingProfile).filter(DatingProfile.user_id == current_user.id).first()
    if not profile:
        profile = DatingProfile(
            user_id=current_user.id,
            opt_in_dating=payload.opt_in_dating,
            headline=payload.headline,
            bio=payload.bio,
            interests=payload.interests or "Reading, Art, Queer Joy",
            intent=payload.intent or "Friendship & Dating",
            looking_for=payload.looking_for or "Open to all queer folks",
            safety_boundary_note=payload.safety_boundary_note or "Take things slow, anonymous chat first",
            approx_city=payload.approx_city or current_user.city
        )
        db.add(profile)
    else:
        profile.opt_in_dating = payload.opt_in_dating
        profile.headline = payload.headline
        profile.bio = payload.bio
        profile.interests = payload.interests or profile.interests
        profile.intent = payload.intent or profile.intent
        profile.looking_for = payload.looking_for or profile.looking_for
        profile.safety_boundary_note = payload.safety_boundary_note or profile.safety_boundary_note
        profile.approx_city = payload.approx_city or profile.approx_city

    db.commit()
    db.refresh(profile)

    return DatingProfileOut(
        id=profile.id,
        user_anon_id=current_user.anon_id,
        user_alias=current_user.alias,
        user_pronouns=current_user.pronouns,
        opt_in_dating=profile.opt_in_dating,
        headline=profile.headline,
        bio=profile.bio,
        interests=profile.interests,
        intent=profile.intent,
        looking_for=profile.looking_for,
        safety_boundary_note=profile.safety_boundary_note,
        approx_city=profile.approx_city,
        created_at=profile.created_at
    )

@router.get("/discover", response_model=List[DatingProfileOut])
def discover_intentional_matches(
    city: Optional[str] = Query(None, description="Optional city filter"),
    intent: Optional[str] = Query(None, description="Friendship, Dating, Mentorship"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(DatingProfile).filter(
        DatingProfile.opt_in_dating == True,
        DatingProfile.user_id != current_user.id
    )

    if city and city != "All India":
        query = query.filter(DatingProfile.approx_city == city)
    if intent:
        query = query.filter(DatingProfile.intent.contains(intent))

    profiles = query.order_by(DatingProfile.updated_at.desc()).limit(30).all()

    return [
        DatingProfileOut(
            id=p.id,
            user_anon_id=p.user.anon_id,
            user_alias=p.user.alias,
            user_pronouns=p.user.pronouns,
            opt_in_dating=p.opt_in_dating,
            headline=p.headline,
            bio=p.bio,
            interests=p.interests,
            intent=p.intent,
            looking_for=p.looking_for,
            safety_boundary_note=p.safety_boundary_note,
            approx_city=p.approx_city,
            created_at=p.created_at
        )
        for p in profiles
        if p.user and p.user.is_active
    ]
