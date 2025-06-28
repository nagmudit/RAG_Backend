from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class ScrapeRequest(BaseModel):
    """Request model for the scrape endpoint."""
    urls: List[HttpUrl]
    
class ScrapeResponse(BaseModel):
    """Response model for the scrape endpoint."""
    success: bool
    message: str
    processed_urls: List[str]
    failed_urls: List[str]
    documents_added: int

class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint."""
    success: bool
    message: str
    filename: str
    documents_added: int
    file_type: str

class AskRequest(BaseModel):
    """Request model for the ask endpoint."""
    query: str
    
class Citation(BaseModel):
    """Model for document citations."""
    url: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float
    source_type: Optional[str] = "url"  # "url" or "document"

class AskResponse(BaseModel):
    """Response model for the ask endpoint."""
    answer: str
    citations: List[Citation]
    query: str

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str
    faiss_index_exists: bool
