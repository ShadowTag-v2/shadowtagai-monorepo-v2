"""Data models for scientific writer API responses."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProgressUpdate:
    """Progress update during paper generation."""
    type: str = "progress"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message: str = ""
    stage: str = "initialization"  # initialization|research|writing|compilation|complete
    percentage: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PaperMetadata:
    """Metadata about the generated paper."""
    title: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    topic: str = ""
    word_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PaperFiles:
    """File paths for all generated paper artifacts."""
    pdf_final: str | None = None
    tex_final: str | None = None
    pdf_drafts: list[str] = field(default_factory=list)
    tex_drafts: list[str] = field(default_factory=list)
    bibliography: str | None = None
    figures: list[str] = field(default_factory=list)
    data: list[str] = field(default_factory=list)
    progress_log: str | None = None
    summary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PaperResult:
    """Final result containing all information about the generated paper."""
    type: str = "result"
    status: str = "success"  # success|partial|failed
    paper_directory: str = ""
    paper_name: str = ""
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    files: PaperFiles = field(default_factory=PaperFiles)
    citations: dict[str, Any] = field(default_factory=dict)
    figures_count: int = 0
    compilation_success: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Ensure nested objects are also dictionaries
        if isinstance(self.metadata, PaperMetadata):
            result['metadata'] = self.metadata.to_dict()
        if isinstance(self.files, PaperFiles):
            result['files'] = self.files.to_dict()
        return result
