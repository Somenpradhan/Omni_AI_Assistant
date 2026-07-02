from app.tools.tavily_search import search_web

class SearchService:
    @staticmethod
    def execute_search(query: str) -> str:
        return search_web(query)
