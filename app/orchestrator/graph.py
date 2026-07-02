import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage
from app.orchestrator.workflow import compile_enterprise_workflow
from app.database import crud
from app.database.database import SessionLocal

DB_PATH = os.getenv("MEMORY_DB_PATH", "memory.db")

def run_orchestrator(query: str, thread_id: str = "default_session") -> dict:
    """
    Executes the Enterprise Multi-Agent AI Assistant LangGraph pipeline.
    Ensures state checkpoints are persisted in memory.db and transactions are logged.
    """
    # 1. Log the User Message to the SQL database for UI timeline mapping
    db = SessionLocal()
    try:
        crud.add_message(
            db=db,
            session_id=thread_id,
            role="user",
            content=query
        )
    except Exception as e:
        print(f"[Warning] Failed to log User query to database: {e}")
    finally:
        db.close()

    # 2. Invoke the state graph under a SqliteSaver checkpointer
    with SqliteSaver.from_conn_string(DB_PATH) as memory_saver:
        app_workflow = compile_enterprise_workflow(memory_saver)
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke LangGraph workflow
        result = app_workflow.invoke(
            {
                "query": query,
                "session_id": thread_id,
                "messages": [HumanMessage(content=query)]
            },
            config=config
        )
        
        # Format return payload
        return {
            "query": result.get("query"),
            "route": result.get("route", "llm"),
            "rag_context": result.get("rag_context", ""),
            "web_search_output": result.get("web_search_output", ""),
            "planner_output": result.get("planner_output", ""),
            "executor_output": result.get("executor_output", ""),
            "final_response": result.get("final_response", ""),
            "confidence_score": result.get("confidence_score", 1.0),
            "tools_used": result.get("tools_used", []),
            "documents_retrieved": result.get("documents_retrieved", []),
            "sources": result.get("sources", [])
        }
