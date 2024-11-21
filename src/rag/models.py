from pydantic import BaseModel
from typing import List, Optional

class Document(BaseModel):
    content: str
    metadata: dict = {}

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class SearchResult(BaseModel):
    content: str
    metadata: dict
    score: float 