from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_db
from ..models.user import User
from ..models.connection import ConnectionRequest, Connection, Message
from ..schemas.connection import (
    ConnectionRequestCreate,
    ConnectionRequestOut,
    ConnectionOut,
    MessageCreate,
    MessageOut,
    IdentityRevealUpdate
)
from ..security import get_current_user

router = APIRouter(prefix="/connections", tags=["Consent-Based Connections & Chat"])

@router.post("/request", response_model=ConnectionRequestOut)
def send_connection_request(
    payload: ConnectionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    receiver = db.query(User).filter(User.anon_id == payload.receiver_anon_id, User.is_active == True).first()
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    if receiver.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send connection request to yourself")

    # Check existing connection
    existing_conn = db.query(Connection).filter(
        or_(
            and_(Connection.user1_id == current_user.id, Connection.user2_id == receiver.id),
            and_(Connection.user1_id == receiver.id, Connection.user2_id == current_user.id)
        ),
        Connection.is_active == True
    ).first()
    if existing_conn:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already connected with this member")

    # Check pending request
    existing_req = db.query(ConnectionRequest).filter(
        ConnectionRequest.sender_id == current_user.id,
        ConnectionRequest.receiver_id == receiver.id,
        ConnectionRequest.status == "pending"
    ).first()
    if existing_req:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A connection request is already pending")

    req = ConnectionRequest(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        intro_note=payload.intro_note,
        intent=payload.intent or "Friendship",
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return ConnectionRequestOut(
        id=req.id,
        request_id=req.request_id,
        sender_anon_id=current_user.anon_id,
        sender_alias=current_user.alias,
        sender_pronouns=current_user.pronouns,
        receiver_anon_id=receiver.anon_id,
        intro_note=req.intro_note,
        intent=req.intent,
        status=req.status,
        created_at=req.created_at
    )

@router.get("/requests", response_model=List[ConnectionRequestOut])
def get_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(ConnectionRequest).filter(
        ConnectionRequest.receiver_id == current_user.id,
        ConnectionRequest.status == "pending"
    ).order_by(ConnectionRequest.created_at.desc()).all()

    return [
        ConnectionRequestOut(
            id=r.id,
            request_id=r.request_id,
            sender_anon_id=r.sender.anon_id,
            sender_alias=r.sender.alias,
            sender_pronouns=r.sender.pronouns,
            receiver_anon_id=current_user.anon_id,
            intro_note=r.intro_note,
            intent=r.intent,
            status=r.status,
            created_at=r.created_at
        )
        for r in requests
    ]

@router.post("/requests/{request_id}/accept")
def accept_connection_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(ConnectionRequest).filter(
        ConnectionRequest.request_id == request_id,
        ConnectionRequest.receiver_id == current_user.id,
        ConnectionRequest.status == "pending"
    ).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending request not found")

    req.status = "accepted"
    req.responded_at = datetime.now(timezone.utc)

    # Establish mutual connection
    connection = Connection(
        user1_id=req.sender_id,
        user2_id=current_user.id,
        is_active=True
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)

    return {"message": "Connection accepted! Safe chat is now enabled.", "connection_id": connection.connection_id}

@router.post("/requests/{request_id}/reject")
def reject_connection_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(ConnectionRequest).filter(
        ConnectionRequest.request_id == request_id,
        ConnectionRequest.receiver_id == current_user.id,
        ConnectionRequest.status == "pending"
    ).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending request not found")

    req.status = "rejected"
    req.responded_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Connection request declined quietly without notification."}

@router.get("", response_model=List[ConnectionOut])
def get_my_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conns = db.query(Connection).filter(
        or_(Connection.user1_id == current_user.id, Connection.user2_id == current_user.id),
        Connection.is_active == True
    ).order_by(Connection.last_message_at.desc()).all()

    results = []
    for c in conns:
        is_user1 = (c.user1_id == current_user.id)
        peer = c.user2 if is_user1 else c.user1
        i_revealed = c.user1_revealed_identity if is_user1 else c.user2_revealed_identity
        peer_revealed = c.user2_revealed_identity if is_user1 else c.user1_revealed_identity

        results.append(ConnectionOut(
            id=c.id,
            connection_id=c.connection_id,
            peer_anon_id=peer.anon_id,
            peer_alias=peer.alias,
            peer_pronouns=peer.pronouns,
            peer_city=peer.city,
            is_active=c.is_active,
            i_revealed_identity=i_revealed,
            peer_revealed_identity=peer_revealed,
            mutual_reveal_active=(i_revealed and peer_revealed),
            created_at=c.created_at,
            last_message_at=c.last_message_at
        ))
    return results

@router.post("/{connection_id}/messages", response_model=MessageOut)
def send_message(
    connection_id: str,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conn = db.query(Connection).filter(
        Connection.connection_id == connection_id,
        or_(Connection.user1_id == current_user.id, Connection.user2_id == current_user.id),
        Connection.is_active == True
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active connection not found")

    msg = Message(
        connection_id=conn.id,
        sender_id=current_user.id,
        content=payload.content.strip(),
        is_sensitive=payload.is_sensitive or False
    )
    db.add(msg)
    conn.last_message_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)

    return MessageOut(
        id=msg.id,
        message_id=msg.message_id,
        sender_alias=current_user.alias,
        sender_anon_id=current_user.anon_id,
        content=msg.content,
        is_sensitive=msg.is_sensitive,
        is_self=True,
        created_at=msg.created_at
    )

@router.get("/{connection_id}/messages", response_model=List[MessageOut])
def get_messages(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conn = db.query(Connection).filter(
        Connection.connection_id == connection_id,
        or_(Connection.user1_id == current_user.id, Connection.user2_id == current_user.id),
        Connection.is_active == True
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active connection not found")

    messages = db.query(Message).filter(Message.connection_id == conn.id).order_by(Message.created_at.asc()).all()

    return [
        MessageOut(
            id=m.id,
            message_id=m.message_id,
            sender_alias=m.sender.alias,
            sender_anon_id=m.sender.anon_id,
            content=m.content,
            is_sensitive=m.is_sensitive,
            is_self=(m.sender_id == current_user.id),
            created_at=m.created_at
        )
        for m in messages
    ]

@router.post("/{connection_id}/reveal")
def toggle_identity_reveal(
    connection_id: str,
    payload: IdentityRevealUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conn = db.query(Connection).filter(
        Connection.connection_id == connection_id,
        or_(Connection.user1_id == current_user.id, Connection.user2_id == current_user.id),
        Connection.is_active == True
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    if conn.user1_id == current_user.id:
        conn.user1_revealed_identity = payload.reveal
    else:
        conn.user2_revealed_identity = payload.reveal

    db.commit()
    return {"message": "Identity reveal preference updated.", "mutual_active": (conn.user1_revealed_identity and conn.user2_revealed_identity)}
