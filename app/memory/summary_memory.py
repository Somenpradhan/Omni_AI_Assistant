from sqlalchemy.orm import Session
from app.database import crud
from app.llm.provider import get_chat_completion

class SummaryMemory:
    @staticmethod
    def get_latest_summary(db: Session, session_id: str) -> str:
        summaries = crud.get_memories_for_session(db, session_id, type="summary")
        if summaries:
            return summaries[0].content  # Ordered by timestamp desc
        return ""
        
    @staticmethod
    def summarize_and_store(db: Session, session_id: str, messages: list) -> str:
        """
        Summarizes the message exchange and stores it in the database memory table.
        """
        if len(messages) < 6:  # Only summarize if there is substantial history
            return ""
            
        formatted_history = []
        for msg in messages:
            formatted_history.append(f"{msg['role'].upper()}: {msg['content']}")
            
        history_str = "\n".join(formatted_history)
        prompt = f"""You are a conversation summarization engine. 
Review the following conversation exchange and produce a highly compressed, structured summary capturing:
1. User goals and projects discussed
2. Current state of answers and resolution
3. Unresolved questions or tasks

Conversation:
{history_str}

Summary:"""
        try:
            summary = get_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            # Store summary in memory table
            crud.add_memory(db, session_id, type="summary", content=summary)
            return summary
        except Exception as e:
            print(f"[Warning] Failed to generate conversation summary: {e}")
            return ""
