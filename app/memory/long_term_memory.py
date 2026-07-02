from sqlalchemy.orm import Session
from app.database import crud
from app.llm.provider import get_chat_completion
from app.llm.prompts import MEMORY_EXTRACT_PROMPT
from app.llm.output_parser import parse_json
import json

class LongTermMemory:
    @staticmethod
    def get_profile_context(db: Session, session_id: str) -> dict:
        """
        Retrieves accumulated long-term facts stored for this session/user.
        """
        memories = crud.get_memories_for_session(db, session_id, type="long_term")
        facts = {}
        for m in memories:
            try:
                data = json.loads(m.content)
                facts.update(data)
            except Exception:
                pass
        return facts
        
    @staticmethod
    def extract_and_update(db: Session, session_id: str, user_input: str, assistant_response: str):
        """
        Analyzes conversation turn, extracts persistent user profile details and stores them.
        """
        prompt = MEMORY_EXTRACT_PROMPT.format(
            user_input=user_input,
            assistant_response=assistant_response
        )
        
        try:
            response = get_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                json_mode=True
            )
            data = parse_json(response)
            extracted_facts = data.get("facts", [])
            
            if extracted_facts:
                # Retrieve current facts
                current_profile = LongTermMemory.get_profile_context(db, session_id)
                
                # Apply updates
                updated = False
                for fact in extracted_facts:
                    key = fact.get("key")
                    val = fact.get("value")
                    if key and val:
                        current_profile[key] = val
                        updated = True
                        
                if updated:
                    # Save updated dict as JSON text content
                    crud.add_memory(
                        db=db,
                        session_id=session_id,
                        type="long_term",
                        content=json.dumps(current_profile)
                    )
                    print(f"[LongTermMemory] Stored new profile facts: {current_profile}")
        except Exception as e:
            print(f"[Warning] Long term profile extract failed: {e}")
