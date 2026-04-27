from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    index: int
    text: str
    distance: float
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = Field(default_factory=list)
    top_k: int
    model: str
    latency_ms: int


class RetrieveResponse(BaseModel):
    query: str
    results: List[SourceChunk]
    count: int


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class ReadyResponse(BaseModel):
    ready: bool
    reason: str


class ReindexRequest(BaseModel):
    data_dir: Optional[str] = None


class ReindexResponse(BaseModel):
    status: str
    document_count: int
    duration_ms: int
    data_dir: str


class UploadResponse(BaseModel):
    id: Optional[str] = None
    filename: str
    storage_path: str
    public_url: Optional[str] = None
    size_bytes: int
    content_type: Optional[str] = None
    uploaded_at: str
