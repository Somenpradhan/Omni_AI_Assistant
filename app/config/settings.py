import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///enterprise.db")
    
    # Uploads
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_documents")
    
    # LLM Settings
    DEFAULT_LLM_PROVIDER = "groq"
    DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
    DEFAULT_EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("vector_db", exist_ok=True)
os.makedirs("logs", exist_ok=True)
