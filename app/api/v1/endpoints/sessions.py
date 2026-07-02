from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.memory.session_manager import SessionManager
from app.services.memory_service import MemoryService
from app.schemas.session import SessionResponse
from typing import List

router = APIRouter()

@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    """
    Lists unique active conversation threads and titles.
    """
    try:
        return SessionManager.list_sessions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full message logs for a session thread.
    """
    try:
        history = MemoryService.get_conversation_history(db, session_id)
        # Format list to prevent issues on static ui loads
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    Clears message logs, memory checkpoints, and session entries.
    """
    try:
        success = SessionManager.delete_session(db, session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found.")
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
