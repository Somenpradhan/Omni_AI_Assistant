from sqlalchemy.orm import Session
from app.database import models
from app.database.database import engine, Base

# Auto-create tables on load
Base.metadata.create_all(bind=engine)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, email: str = None):
    db_user = models.User(username=username, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_session(db: Session, session_id: str):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def get_all_sessions(db: Session):
    return db.query(models.Session).order_by(models.Session.created_at.desc()).all()

def create_session(db: Session, session_id: str, title: str = "New Session"):
    db_session = models.Session(id=session_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: str):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session:
        # Cascade delete messages and memories
        db.query(models.Message).filter(models.Message.session_id == session_id).delete()
        db.query(models.Memory).filter(models.Memory.session_id == session_id).delete()
        db.delete(session)
        db.commit()
        return True
    return False

def add_message(db: Session, session_id: str, role: str, content: str, route: str = "llm",
                reasoning: str = None, tools_used: str = None, confidence_score: float = 1.0,
                documents_retrieved: str = None, sources: str = None):
    # Ensure session exists
    session = get_session(db, session_id)
    if not session:
        create_session(db, session_id, title=content[:30] + "...")
        
    db_message = models.Message(
        session_id=session_id,
        role=role,
        content=content,
        route=route,
        reasoning=reasoning,
        tools_used=tools_used,
        confidence_score=confidence_score,
        documents_retrieved=documents_retrieved,
        sources=sources
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_for_session(db: Session, session_id: str):
    return db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.timestamp.ascii if hasattr(models.Message.timestamp, 'ascii') else models.Message.timestamp.asc()).all()

def add_memory(db: Session, session_id: str, type: str, content: str):
    db_memory = models.Memory(session_id=session_id, type=type, content=content)
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

def get_memories_for_session(db: Session, session_id: str, type: str = None):
    query = db.query(models.Memory).filter(models.Memory.session_id == session_id)
    if type:
        query = query.filter(models.Memory.type == type)
    return query.order_by(models.Memory.timestamp.desc()).all()

def log_tool_execution(db: Session, tool_name: str, input_data: str, output_data: str):
    db_log = models.ToolLog(tool_name=tool_name, input_data=input_data, output_data=output_data)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def log_agent_node(db: Session, node_name: str, state_snapshot: str):
    db_log = models.AgentLog(node_name=node_name, state_snapshot=state_snapshot)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
