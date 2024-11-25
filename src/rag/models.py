from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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

class DocumentMetadata(BaseModel):
    source: str
    chunk_id: int
    timestamp: datetime
    category: Optional[str] = None
    status: str = "completed"  # processing, completed, error
    description: Optional[str] = None
    tags: List[str] = []

class UpdateDocumentRequest(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None 