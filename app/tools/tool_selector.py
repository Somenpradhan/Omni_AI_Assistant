from app.llm.provider import get_chat_completion
from app.llm.prompts import TOOL_SELECTION_PROMPT
from app.llm.output_parser import parse_json

class ToolSelector:
    @staticmethod
    def select_tools(query: str, plan: str) -> dict:
        """
        Determines which tools (if any) are required to complete the query based on the planning roadmap.
        """
        prompt = TOOL_SELECTION_PROMPT.format(query=query, plan=plan)
        
        try:
            response = get_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                json_mode=True
            )
            data = parse_json(response)
            return {
                "needs_tool": data.get("needs_tool", False),
                "tools": data.get("tools", []),
                "reasoning": data.get("reasoning", "")
            }
        except Exception as e:
            print(f"[Warning] Tool selection failed: {e}. Falling back to default empty tool list.")
            return {
                "needs_tool": False,
                "tools": [],
                "reasoning": str(e)
            }
