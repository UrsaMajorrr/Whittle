from pydantic import BaseModel
from typing import Dict, Any

class RequirementParseRequest(BaseModel):
    requirement: str

class RequirementParseResponse(BaseModel):
    parameters: Dict[str, Any]
    original: str 