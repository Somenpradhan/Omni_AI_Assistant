import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage, HumanMessage

from app.orchestrator.state import AgentState
from app.orchestrator.router import route_next_node
from app.agents.router_agent import router_agent
from app.agents.planner_agent import planner_agent
from app.agents.rag_agent import rag_agent
from app.agents.llm_agent import llm_agent
from app.agents.web_agent import web_agent
from app.agents.tool_agent import tool_agent
from app.agents.executor_agent import executor_agent
from app.agents.reflection_agent import reflection_agent
from app.agents.response_agent import response_agent
from app.agents.memory_agent import memory_agent

from app.database import crud
from app.database.database import SessionLocal

# --- Node Handlers ---

def node_router(state: AgentState) -> dict:
    query = state["query"]
    decision = router_agent(query)
    print(f"[RouterNode] Routing intent to: '{decision['route']}' ({decision['reasoning']})")
    
    # Log node execution
    db = SessionLocal()
    crud.log_agent_node(db, "router", f"Route choice: {decision['route']}")
    db.close()
    
    return {
        "route": decision["route"],
        "reasoning": decision["reasoning"],
        "rag_context": "",
        "web_search_output": "",
        "planner_output": "",
        "executor_output": "",
        "tools_used": [],
        "documents_retrieved": [],
        "sources": [],
        "final_response": "",
        "confidence_score": 1.0
    }

def node_llm(state: AgentState) -> dict:
    query = state["query"]
    output = llm_agent(query)
    return {"final_response": output}

def node_rag(state: AgentState) -> dict:
    query = state["query"]
    rag_res = rag_agent(query)
    return {
        "rag_context": rag_res["context"],
        "documents_retrieved": rag_res["documents_retrieved"],
        "sources": rag_res["sources"]
    }

def node_web_search(state: AgentState) -> dict:
    query = state["query"]
    search_res = web_agent(query)
    return {"web_search_output": search_res}

def node_planner(state: AgentState) -> dict:
    query = state["query"]
    # Pass any RAG context if it exists
    context = state.get("rag_context", "")
    plan = planner_agent(query, context=context)
    return {"planner_output": plan}

def node_tool_selector(state: AgentState) -> dict:
    query = state["query"]
    plan = state.get("planner_output", "")
    selection = tool_agent(query, plan)
    
    # Store tools listed in state
    tools = selection.get("tools", [])
    needs_tool = selection.get("needs_tool", False)
    
    print(f"[ToolSelectorNode] Tools requested: {tools} (needs_tool: {needs_tool})")
    
    return {
        "tools_used": tools if needs_tool else []
    }

def node_executor(state: AgentState) -> dict:
    query = state["query"]
    plan = state.get("planner_output", "")
    tools = state.get("tools_used", [])
    
    if not tools:
        return {"executor_output": "No tools executed."}
        
    output = executor_agent(tools, query, plan)
    return {"executor_output": output}

def node_response(state: AgentState) -> dict:
    query = state["query"]
    route = state.get("route", "llm")
    
    # Run synthesizer
    response_text = response_agent(
        query=query,
        route=route,
        rag_context=state.get("rag_context", ""),
        web_search_output=state.get("web_search_output", ""),
        planner_output=state.get("planner_output", ""),
        executor_output=state.get("executor_output", "")
    )
    
    return {"final_response": response_text}

def node_reflection(state: AgentState) -> dict:
    query = state["query"]
    final_response = state.get("final_response", "")
    
    # Evidence is concatenation of any active RAG, Search or Exec outputs
    evidence_parts = []
    if state.get("rag_context"):
        evidence_parts.append(f"RAG:\n{state['rag_context']}")
    if state.get("web_search_output"):
        evidence_parts.append(f"Search:\n{state['web_search_output']}")
    if state.get("executor_output"):
        evidence_parts.append(f"Tools:\n{state['executor_output']}")
    evidence = "\n\n".join(evidence_parts)
    
    audit = reflection_agent(query, evidence, final_response)
    print(f"[ReflectionNode] Confidence: {audit['confidence_score']} (Valid: {audit['is_valid']})")
    
    return {
        "confidence_score": audit["confidence_score"]
    }

def node_memory(state: AgentState) -> dict:
    query = state["query"]
    session_id = state.get("session_id", "default_session")
    final_response = state.get("final_response", "")
    
    # Save exchange to SQLAlchemy tables
    db = SessionLocal()
    try:
        # 1. Log assistant response to message list
        crud.add_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=final_response,
            route=state.get("route", "llm"),
            reasoning=state.get("reasoning", ""),
            tools_used=",".join(state.get("tools_used", [])) if state.get("tools_used") else None,
            confidence_score=state.get("confidence_score", 1.0),
            documents_retrieved=",".join(state.get("documents_retrieved", [])) if state.get("documents_retrieved") else None,
            sources=",".join(state.get("sources", [])) if state.get("sources") else None
        )
        # 2. Extract profile details and summarize conversation
        memory_agent(db, session_id, query, final_response)
    except Exception as e:
        print(f"[Warning] MemoryNode save failed: {e}")
    finally:
        db.close()
        
    # Return updates to messages timeline in LangGraph checkpointers
    ai_msg = AIMessage(
        content=final_response,
        additional_kwargs={
            "route": state.get("route"),
            "confidence_score": state.get("confidence_score", 1.0),
            "tools_used": state.get("tools_used", []),
            "documents_retrieved": state.get("documents_retrieved", []),
            "sources": state.get("sources", [])
        }
    )
    
    return {
        "messages": [ai_msg]
    }

# --- Graph Assembly ---

def compile_enterprise_workflow(checkpointer):
    workflow = StateGraph(AgentState)
    
    # Register Nodes
    workflow.add_node("router", node_router)
    workflow.add_node("llm", node_llm)
    workflow.add_node("rag", node_rag)
    workflow.add_node("web_search", node_web_search)
    workflow.add_node("planner", node_planner)
    workflow.add_node("tool_selector", node_tool_selector)
    workflow.add_node("executor", node_executor)
    workflow.add_node("response", node_response)
    workflow.add_node("reflection", node_reflection)
    workflow.add_node("memory", node_memory)
    
    # Establish router entry point
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_next_node,
        {
            "llm": "llm",
            "rag": "rag",
            "web_search": "web_search",
            "planner": "planner"
        }
    )
    
    # Connecting nodes
    workflow.add_edge("llm", "response")
    workflow.add_edge("rag", "response")
    workflow.add_edge("web_search", "response")
    
    workflow.add_edge("planner", "tool_selector")
    workflow.add_edge("tool_selector", "executor")
    workflow.add_edge("executor", "response")
    
    workflow.add_edge("response", "reflection")
    workflow.add_edge("reflection", "memory")
    workflow.add_edge("memory", END)
    
    return workflow.compile(checkpointer=checkpointer)
