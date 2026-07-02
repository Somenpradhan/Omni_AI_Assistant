from app.llm.provider import get_chat_completion

def llm_agent(query: str, system_context: str = "") -> str:
    """
    Standard general knowledge LLM execution.
    """
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": query})
    
    try:
        return get_chat_completion(messages, temperature=0.7)
    except Exception as e:
        print(f"[Warning] LLM Agent failed: {e}.")
        return f"Error executing general LLM: {e}"
