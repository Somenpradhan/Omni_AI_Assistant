from sqlalchemy.orm import Session
from app.memory.conversation_memory import ConversationMemory
from app.memory.summary_memory import SummaryMemory
from app.memory.long_term_memory import LongTermMemory

class MemoryService:
    @staticmethod
    def get_conversation_history(db: Session, session_id: str) -> list:
        return ConversationMemory.get_history(db, session_id)
        
    @staticmethod
    def get_session_summary(db: Session, session_id: str) -> str:
        return SummaryMemory.get_latest_summary(db, session_id)
        
    @staticmethod
    def get_user_profile(db: Session, session_id: str) -> dict:
        return LongTermMemory.get_profile_context(db, session_id)
