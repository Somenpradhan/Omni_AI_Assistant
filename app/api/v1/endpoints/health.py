from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Evaluates configurations and returns service availability status.
    """
    tavily_configured = bool(settings.TAVILY_API_KEY and settings.TAVILY_API_KEY != "your_tavily_api_key_here" and settings.TAVILY_API_KEY.strip())
    groq_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here" and settings.GROQ_API_KEY.strip())
    
    # Evaluate LLM core status
    llm_online = groq_configured
    if groq_configured:
        llm_desc = "Groq (Llama 3.1) Active"
    else:
        llm_desc = "Simulation Mode Active"
        
    # Evaluate RAG vector store state
    try:
        from app.rag.vector_store import vector_store
        chunk_count = len(vector_store.documents)
        rag_online = True
        rag_desc = f"{chunk_count} document chunks indexed" if chunk_count > 0 else "Ready (No documents loaded)"
    except Exception as e:
        rag_online = False
        rag_desc = f"Load Error: {str(e)}"
        
    # Evaluate Agentic Graph compilation status
    try:
        from app.orchestrator.graph import run_orchestrator
        agentic_online = True
        agentic_desc = "LangGraph Pipeline Active"
    except Exception as e:
        agentic_online = False
        agentic_desc = f"Pipeline Compile Error: {str(e)}"
        
    return {
        "status": "online",
        "openai_configured": False,
        "tavily_configured": tavily_configured,
        "groq_configured": groq_configured,
        "llm_online": llm_online,
        "llm_desc": llm_desc,
        "rag_online": rag_online,
        "rag_desc": rag_desc,
        "agentic_online": agentic_online,
        "agentic_desc": agentic_desc
    }
