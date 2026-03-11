from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Question(BaseModel):
    user_id: str
    question: str
    context: Optional[Dict[str, Any]] = None

class Answer(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    related_topics: List[str]
    recommended_resources: List[Dict[str, Any]]