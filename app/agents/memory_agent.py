from sqlalchemy.orm import Session
from app.memory.long_term_memory import LongTermMemory
from app.memory.summary_memory import SummaryMemory
from app.memory.conversation_memory import ConversationMemory

def memory_agent(db: Session, session_id: str, user_query: str, final_response: str):
    """
    Consolidates long term profiles and summarization checkpoints in the database.
    """
    # 1. Update long term memory traits
    try:
        LongTermMemory.extract_and_update(db, session_id, user_query, final_response)
    except Exception as e:
        print(f"[Warning] Memory agent profile update failed: {e}")
        
    # 2. Check and compile summary memory checkpointers
    try:
        history = ConversationMemory.get_history(db, session_id)
        if len(history) >= 10:  # Compile summary if thread exceeds 10 turns
            SummaryMemory.summarize_and_store(db, session_id, history)
    except Exception as e:
        print(f"[Warning] Memory agent summary failed: {e}")
