from pydantic import BaseModel
from typing import Optional

class LLMConfig(BaseModel):
    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
