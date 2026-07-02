from app.orchestrator.state import AgentState

def route_next_node(state: AgentState) -> str:
    """
    LangGraph conditional edge router. Evaluates current State route mapping
    and indicates which agent node must execute next.
    """
    route = state.get("route", "llm")
    
    # Fallback/enforce matching key mapping
    if route not in ["llm", "rag", "web_search", "planner"]:
        return "llm"
        
    return route
