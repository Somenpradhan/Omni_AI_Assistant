from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(100), primary_key=True, index=True)  # Using string ID for thread_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), default="New Session")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    route = Column(String(50), default="llm")
    reasoning = Column(Text, nullable=True)
    tools_used = Column(String(500), nullable=True)  # comma separated names
    confidence_score = Column(Float, default=1.0)
    documents_retrieved = Column(Text, nullable=True)  # JSON or text chunk names
    sources = Column(Text, nullable=True)  # JSON or comma separated URLs
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    source_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())

class EmbeddingsMetadata(Base):
    __tablename__ = "embeddings_metadata"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200), nullable=False)
    filepath = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, processed, failed
    upload_time = Column(DateTime(timezone=True), server_default=func.now())

class Memory(Base):
    __tablename__ = "memory"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("sessions.id"), nullable=False)
    type = Column(String(50), nullable=False)  # conversation, summary, long_term
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ToolLog(Base):
    __tablename__ = "tool_logs"
    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(50), nullable=False)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True, index=True)
    node_name = Column(String(50), nullable=False)
    state_snapshot = Column(Text, nullable=True)  # JSON dump of active state keys
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
