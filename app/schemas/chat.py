from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    query: str
    route: str
    rag_context: Optional[str] = None
    task_output: Optional[str] = None  # Planner output
    web_search_output: Optional[str] = None
    llm_output: Optional[str] = None
    final_response: str
    confidence_score: float = 1.0
    reasoning: Optional[str] = None
    tools_used: List[str] = []
    documents_retrieved: List[str] = []
    sources: List[str] = []
    history: List[dict]
