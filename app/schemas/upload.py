from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    status: str
    chunks_added: int
