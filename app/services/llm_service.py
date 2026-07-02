from app.agents.llm_agent import llm_agent

class LLMService:
    @staticmethod
    def get_response(query: str, system_context: str = "") -> str:
        return llm_agent(query, system_context)
