from pydantic import BaseModel, Field
from typing import List

class ResponseSchema(BaseModel):
    message: str = Field(description="The primary conversational response maintaining persona.")
    citations: List[str] = Field(description="Array of authentic source locations driving the response. Empty if none.", default_factory=list)
    suggested_prompts: List[str] = Field(description="Array of 2-3 short, contextual questions the user might want to follow up with.", default_factory=list)
