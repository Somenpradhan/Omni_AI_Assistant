from typing import TypedDict, List, Optional
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    query: str
    session_id: str
    route: Optional[str]
    rag_context: Optional[str]
    web_search_output: Optional[str]
    planner_output: Optional[str]
    executor_output: Optional[str]
    final_response: Optional[str]
    confidence_score: Optional[float]
    reasoning: Optional[str]
    tools_used: Optional[List[str]]
    documents_retrieved: Optional[List[str]]
    sources: Optional[List[str]]
    messages: List[AnyMessage]
