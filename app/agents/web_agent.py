from app.tools.tavily_search import search_web

def web_agent(query: str) -> str:
    """
    Queries web databases to compile news/event results.
    """
    try:
        return search_web(query)
    except Exception as e:
        print(f"[Warning] Web Agent failed: {e}")
        return f"Web Search Error: {e}"
