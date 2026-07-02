from app.llm.provider import get_chat_completion
from app.llm.prompts import RESPONSE_PROMPT
from app.services.citation_service import CitationService

def response_agent(query: str, route: str, rag_context: str = "", web_search_output: str = "",
                   planner_output: str = "", executor_output: str = "") -> str:
    """
    Synthesizes plan instructions, searches, and tool actions into a final readable answer.
    """
    prompt = RESPONSE_PROMPT.format(
        query=query,
        route=route,
        rag_context=rag_context or "None",
        web_search_output=web_search_output or "None",
        planner_output=planner_output or "None",
        executor_output=executor_output or "None"
    )
    
    try:
        response = get_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        # Integrate CitationService if RAG context was used
        if rag_context and rag_context != "None":
            sources = CitationService.extract_sources(rag_context)
            if sources:
                citations_md = CitationService.format_citations_markdown(sources)
                response = response.strip() + citations_md
                
        return response
    except Exception as e:
        print(f"[Warning] Response Agent synthesis failed: {e}.")
        return f"System consolidation error: {e}"
