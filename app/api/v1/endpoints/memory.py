from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.memory_service import MemoryService
from app.database import crud
import json

router = APIRouter()

@router.get("/memory/{session_id}")
def get_session_memories(session_id: str, db: Session = Depends(get_db)):
    """
    Returns aggregated long-term preferences and latest conversation summaries.
    """
    try:
        summary = MemoryService.get_session_summary(db, session_id)
        profile = MemoryService.get_user_profile(db, session_id)
        return {
            "session_id": session_id,
            "summary": summary,
            "long_term_profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/{session_id}")
def add_user_preference(session_id: str, key: str = Body(...), value: str = Body(...), db: Session = Depends(get_db)):
    """
    Injects a manual user preference or long-term trait fact.
    """
    try:
        # Load profile
        profile = MemoryService.get_user_profile(db, session_id)
        profile[key] = value
        
        # Save to memory table
        crud.add_memory(
            db=db,
            session_id=session_id,
            type="long_term",
            content=json.dumps(profile)
        )
        return {"status": "saved", "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
