import os
from app.config.settings import settings

def read_local_file(filepath: str) -> str:
    """
    Reads contents of a text file inside the uploaded documents or workspace directory.
    """
    # Security: check that the file is located within a safe path
    # Normalise paths
    normalized_path = os.path.abspath(filepath)
    workspace_root = os.path.abspath(os.getcwd())
    
    # Allow reading files in workspace or upload directory
    if not normalized_path.startswith(workspace_root) and not normalized_path.startswith(os.path.abspath(settings.UPLOAD_DIR)):
         return "Security Error: Read access denied for paths outside the workspace directory."
         
    if not os.path.exists(normalized_path):
        return f"Error: File not found at '{filepath}'."
        
    if os.path.isdir(normalized_path):
        return f"Error: Path '{filepath}' is a directory, not a file."
        
    try:
        # Check size to prevent loading gigabytes of data into memory
        file_size = os.path.getsize(normalized_path)
        if file_size > 1 * 1024 * 1024:  # 1MB limit
            return f"Error: File is too large ({file_size} bytes). Max limit for tool reading is 1MB."
            
        with open(normalized_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"
