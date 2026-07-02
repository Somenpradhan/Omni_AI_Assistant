from app.llm.provider import get_chat_completion
from app.llm.prompts import ROUTER_PROMPT
from app.llm.output_parser import parse_json

def router_agent(query: str) -> dict:
    """
    Evaluates query intent and returns a routing choice: 'llm', 'rag', 'web_search', or 'planner'.
    """
    prompt = ROUTER_PROMPT.format(query=query)
    try:
        response = get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            json_mode=True
        )
        data = parse_json(response)
        route = data.get("route", "llm").strip().lower()
        reasoning = data.get("reasoning", "")
        
        # Enforce valid routing strings
        if route not in ["llm", "rag", "web_search", "planner"]:
            route = "llm"
            
        # Robust heuristic overrides for tool execution/system details
        q_lower = query.lower()
        if any(k in q_lower for k in ["calculate", "calculator", "math", "date and time", "current time", "run python", "python script", "execute code", "run code", "database query", "database queries", "sql query", "query database"]):
            if route != "planner":
                route = "planner"
                reasoning = "Heuristically routed to 'planner' due to tool execution indicators (math/python/datetime)."
        elif any(k in q_lower for k in ["system manual", "system_manual.pdf", "aether orchestrator"]):
            if route not in ["rag", "planner"]:
                route = "rag"
                reasoning = "Heuristically routed to 'rag' for internal system manual inquiry."
            
        return {"route": route, "reasoning": reasoning}
    except Exception as e:
        print(f"[Warning] Router Agent failed: {e}. Defaulting route to LLM.")
        return {"route": "llm", "reasoning": f"Defaulted due to error: {e}"}
