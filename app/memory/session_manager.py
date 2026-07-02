from sqlalchemy.orm import Session
from app.database import crud

class SessionManager:
    @staticmethod
    def create_session(db: Session, session_id: str, title: str = "New Session"):
        return crud.create_session(db, session_id, title)
        
    @staticmethod
    def get_session(db: Session, session_id: str):
        return crud.get_session(db, session_id)
        
    @staticmethod
    def list_sessions(db: Session):
        sessions = crud.get_all_sessions(db)
        return [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]
        
    @staticmethod
    def delete_session(db: Session, session_id: str):
        return crud.delete_session(db, session_id)
