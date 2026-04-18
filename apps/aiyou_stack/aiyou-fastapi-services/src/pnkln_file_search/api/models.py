"""API request and response models"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for query processing"""

    query: str = Field(..., description="User query to process")
    vertical: str = Field(..., description="Vertical name (e.g., 'defense', 'healthcare')")
    corpus_name: str | None = Field(
        None,
        description="Optional corpus name (auto-detected if not provided)",
    )
    top_k: int | None = Field(None, description="Number of top results to retrieve", ge=1, le=20)


class PolicyCitation(BaseModel):
    """Policy citation from file search"""

    type: str = Field(..., description="Citation type (corpus, web)")
    uri: str | None = Field(None, description="Source URI")
    title: str | None = Field(None, description="Document title")
    text: str | None = Field(None, description="Citation text")


class PolicyContext(BaseModel):
    """Policy context from file search"""

    citations: list[PolicyCitation]
    source_documents: list[str]
    retrieval_time_ms: float


class EnforcementDecision(BaseModel):
    """Enforcement decision from Judge #6"""

    allowed: bool
    confidence: float
    policy_violations: list[str]
    required_actions: list[str]
    total_latency_ms: float


class TimingMetrics(BaseModel):
    """Timing metrics for request"""

    file_search_ms: float
    judge_layer1_ms: float
    enforcement_ms: float
    total_ms: float


class QueryResponse(BaseModel):
    """Response model for query processing"""

    query: str
    vertical: str
    enforcement: EnforcementDecision
    policy_context: PolicyContext
    timing: TimingMetrics
    metadata: dict[str, str]


class CorpusInfo(BaseModel):
    """Corpus information"""

    name: str
    display_name: str
    description: str


class CorpusCreateRequest(BaseModel):
    """Request to create a corpus"""

    vertical: str = Field(..., description="Vertical name")
    force_recreate: bool = Field(False, description="Force recreate if exists")


class FileImportRequest(BaseModel):
    """Request to import files into corpus"""

    corpus_name: str = Field(..., description="Target corpus name")
    file_paths: list[str] = Field(..., description="List of GCS URIs")
    chunk_size: int | None = Field(None, description="Override chunk size")
    chunk_overlap: int | None = Field(None, description="Override chunk overlap")


class HealthResponse(BaseModel):
    """Health check response"""

    state: str
    healthy: bool
    violations: list[dict]
    metrics: dict


class VerticalInfo(BaseModel):
    """Vertical information"""

    name: str
    display_name: str
    regulations: list[str]
    description: str
