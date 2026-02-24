"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str
    session_id: str


class EmbeddingResponse(BaseModel):
    embedding: List[float]
    model: str
    message: str


class SearchResult(BaseModel):
    content: str
    section_type: str
    similarity: float
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str


class AddCVSectionRequest(BaseModel):
    section_type: str
    content: str
    metadata: Optional[dict] = None


class AddCVSectionResponse(BaseModel):
    id: int
    section_type: str
    content: str
    embedding_dimensions: int
    message: str
