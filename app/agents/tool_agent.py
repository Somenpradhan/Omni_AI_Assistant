from app.tools.tool_selector import ToolSelector

def tool_agent(query: str, plan: str) -> dict:
    """
    Interrogates selector prompts to return required tools.
    """
    return ToolSelector.select_tools(query=query, plan=plan)
