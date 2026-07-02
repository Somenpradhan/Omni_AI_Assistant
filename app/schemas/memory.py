from pydantic import BaseModel
from typing import Dict

class MemoryResponse(BaseModel):
    session_id: str
    summary: str
    long_term_profile: Dict[str, str]
