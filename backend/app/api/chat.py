from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import ChatSession, User
from app.schemas import ChatMessageCreate, ChatMessageResponse, ChatSessionResponse
from app.services.property_service import add_chat_message, create_chat_session
from app.services.rag_service import rag_service
from app.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/sessions", response_model=ChatSessionResponse)
def new_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_chat_session(db, current_user)


@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatSession)
        .options(joinedload(ChatSession.messages))
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .options(joinedload(ChatSession.messages))
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return session


@router.post(
    "/sessions/{session_id}/message",
    response_model=list[ChatMessageResponse],
)
def send_message(
    session_id: int,
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    user_message, assistant_message = add_chat_message(db, session, data)
    return [user_message, assistant_message]


@router.post("/reindex")
def reindex_properties(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Rebuild the ChromaDB property index. Admin-only operation."""
    count = rag_service.reindex_all(db)

    return {
        "success": True,
        "indexed_properties": count,
        "message": f"{count} properties indexed successfully.",
    }
