from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.dependencies import get_db
from app.orchestrator.graph import run_orchestrator
from app.services.memory_service import MemoryService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Submits query to Enterprise Multi-Agent AI system workflow.
    State checkpoints and user memories are automatically persisted.
    """
    try:
        # Run state graph orchestration
        result = run_orchestrator(
            query=request.query,
            thread_id=request.thread_id
        )
        
        # Load accumulated history
        history = MemoryService.get_conversation_history(db, request.thread_id)
        
        # Map fields to ChatResponse schema
        return ChatResponse(
            query=result["query"],
            route=result["route"],
            rag_context=result["rag_context"],
            task_output=result["planner_output"],  # Planner roadmap mapped to old task_output
            web_search_output=result["web_search_output"],
            llm_output=result["final_response"],
            final_response=result["final_response"],
            confidence_score=result["confidence_score"],
            reasoning=result.get("reasoning", ""),
            tools_used=result["tools_used"],
            documents_retrieved=result["documents_retrieved"],
            sources=result["sources"],
            history=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")
