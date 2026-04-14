"""Mock mode for local development without GCP credentials
"""

import os

import structlog

logger = structlog.get_logger(__name__)


def is_mock_mode() -> bool:
    """Check if running in mock mode"""
    return os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")


class MockCorpusManager:
    """Mock corpus manager for local testing"""

    def __init__(self):
        self._initialized = False
        self._mock_corpora = {
            "defense": "projects/mock/locations/us-central1/ragCorpora/defense-123",
            "healthcare": "projects/mock/locations/us-central1/ragCorpora/healthcare-456",
            "finance": "projects/mock/locations/us-central1/ragCorpora/finance-789",
        }

    async def initialize(self) -> None:
        """Mock initialization"""
        logger.info("mock_corpus_manager_initialized")
        self._initialized = True

    async def create_corpus(self, vertical_config, force_recreate=False) -> str:
        """Mock corpus creation"""
        corpus_name = self._mock_corpora.get(
            vertical_config.name,
            f"projects/mock/locations/us-central1/ragCorpora/{vertical_config.name}-999",
        )
        logger.info(
            "mock_corpus_created",
            vertical=vertical_config.name,
            corpus_name=corpus_name,
        )
        return corpus_name

    async def import_files(self, corpus_name: str, file_paths: list[str], **kwargs) -> None:
        """Mock file import"""
        logger.info(
            "mock_files_imported",
            corpus_name=corpus_name,
            file_count=len(file_paths),
        )

    async def list_corpora(self) -> list[dict[str, str]]:
        """Mock list corpora"""
        return [
            {
                "name": corpus_name,
                "display_name": f"pnkln_{vertical}_policies",
                "description": f"Mock corpus for {vertical}",
            }
            for vertical, corpus_name in self._mock_corpora.items()
        ]

    async def delete_corpus(self, corpus_name: str) -> None:
        """Mock delete corpus"""
        logger.info("mock_corpus_deleted", corpus_name=corpus_name)

    def get_corpus_name(self, vertical_name: str) -> str | None:
        """Get mock corpus name"""
        return self._mock_corpora.get(vertical_name)


class MockGenerativeModel:
    """Mock Gemini model for local testing"""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_content(self, prompt, tools=None):
        """Mock content generation"""
        return MockResponse()


class MockResponse:
    """Mock Gemini response"""

    def __init__(self):
        self.text = "Mock policy context: According to ATP 5-19, information operations must follow proper approval channels."
        self.candidates = [MockCandidate()]


class MockCandidate:
    """Mock response candidate"""

    def __init__(self):
        self.grounding_metadata = MockGroundingMetadata()


class MockGroundingMetadata:
    """Mock grounding metadata"""

    def __init__(self):
        self.grounding_chunks = [
            MockGroundingChunk(
                retrieved_context=MockRetrievedContext(
                    text="ATP 5-19 Section 2.3: Information operations require command approval.",
                    uri="gs://mock-bucket/defense/ATP_5-19.pdf",
                ),
            ),
            MockGroundingChunk(
                retrieved_context=MockRetrievedContext(
                    text="OPSEC guidelines mandate review before external sharing.",
                    uri="gs://mock-bucket/defense/OPSEC_Manual.pdf",
                ),
            ),
        ]


class MockGroundingChunk:
    """Mock grounding chunk"""

    def __init__(self, retrieved_context=None, web=None):
        self.retrieved_context = retrieved_context
        self.web = web


class MockRetrievedContext:
    """Mock retrieved context"""

    def __init__(self, text: str, uri: str):
        self.text = text
        self.uri = uri


def get_mock_responses() -> dict:
    """Get mock responses for different query types"""
    return {
        "default": {
            "policy_context": "Mock policy context returned",
            "citations": [
                {
                    "type": "corpus",
                    "uri": "gs://mock-bucket/defense/ATP_5-19.pdf",
                    "text": "Mock citation text from policy document",
                },
            ],
            "source_documents": ["gs://mock-bucket/defense/ATP_5-19.pdf"],
        },
        "high_risk": {
            "atp_5_19_flags": ["information_disclosure", "opsec_violation"],
            "risk_level": "high",
            "confidence": 0.92,
        },
        "low_risk": {
            "atp_5_19_flags": [],
            "risk_level": "low",
            "confidence": 0.88,
        },
    }
