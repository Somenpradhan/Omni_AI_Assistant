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
    DEFAULT_LLM_PROVIDER = "groq" if (os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here") else "openai"
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
    DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
    DEFAULT_EMBEDDINGS_MODEL = "text-embedding-3-small"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("vector_db", exist_ok=True)
os.makedirs("logs", exist_ok=True)
