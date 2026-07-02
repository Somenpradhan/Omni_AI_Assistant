from app.llm.provider import get_chat_completion
from app.llm.prompts import PLANNER_PROMPT

def planner_agent(query: str, context: str = "") -> str:
    """
    Creates a milestone guides roadmap using LLM analysis.
    """
    prompt = PLANNER_PROMPT.format(query=query, context=context or "None provided.")
    try:
        response = get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response
    except Exception as e:
        print(f"[Warning] Planner Agent failed: {e}.")
        return f"Error compiling plan: {e}"
