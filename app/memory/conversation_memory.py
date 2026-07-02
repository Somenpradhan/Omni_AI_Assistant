from sqlalchemy.orm import Session
from app.database import crud

class ConversationMemory:
    @staticmethod
    def add_message(db: Session, session_id: str, role: str, content: str, route: str = "llm",
                    reasoning: str = None, tools_used: str = None, confidence_score: float = 1.0,
                    documents_retrieved: str = None, sources: str = None):
        return crud.add_message(
            db=db,
            session_id=session_id,
            role=role,
            content=content,
            route=route,
            reasoning=reasoning,
            tools_used=tools_used,
            confidence_score=confidence_score,
            documents_retrieved=documents_retrieved,
            sources=sources
        )
        
    @staticmethod
    def get_history(db: Session, session_id: str):
        messages = crud.get_messages_for_session(db, session_id)
        return [
            {
                "role": m.role,
                "content": m.content,
                "route": m.route,
                "reasoning": m.reasoning,
                "tools_used": m.tools_used,
                "confidence_score": m.confidence_score,
                "documents_retrieved": m.documents_retrieved,
                "sources": m.sources,
                "timestamp": m.timestamp
            } for m in messages
        ]
class_conversation_memory = ConversationMemory()
