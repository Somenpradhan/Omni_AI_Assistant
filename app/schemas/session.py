from pydantic import BaseModel
from datetime import datetime

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
