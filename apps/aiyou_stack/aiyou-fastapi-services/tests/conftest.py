"""Pytest configuration and fixtures for ShadowTag v2 tests."""

from pathlib import Path

import cv2
import numpy as np
import pytest
import soundfile as sf


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for test files."""
    return tmp_path


@pytest.fixture
def sample_video(temp_dir: Path) -> Path:
    """Create a minimal test video file."""
    video_path = temp_dir / "test_video.mp4"

    # Create simple 640x480 video with 30 frames at 30 fps
    width, height = 640, 480
    fps = 30.0
    num_frames = 30

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

    for i in range(num_frames):
        # Create gradient frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = (i * 8) % 256  # Blue channel
        frame[:, :, 1] = 128  # Green channel
        frame[:, :, 2] = 255 - (i * 8) % 256  # Red channel
        out.write(frame)

    out.release()
    return video_path


@pytest.fixture
def sample_audio(temp_dir: Path) -> Path:
    """Create a minimal test audio file (48 kHz stereo)."""
    audio_path = temp_dir / "test_audio.wav"

    # Create 2-second stereo sine wave at 440 Hz
    sample_rate = 48000
    duration = 2.0
    frequency = 440.0

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_mono = 0.3 * np.sin(2 * np.pi * frequency * t)
    audio_stereo = np.stack([audio_mono, audio_mono], axis=-1).astype(np.float32)

    sf.write(str(audio_path), audio_stereo, sample_rate)
    return audio_path


@pytest.fixture
def sample_prompt() -> str:
    """Provide sample prompt for testing."""
    return "A sunset over mountains with vibrant orange and purple hues"


@pytest.fixture
def mock_web3_provider(monkeypatch):
    """Mock Web3 provider for blockchain tests (avoid real transactions)."""
    from unittest.mock import MagicMock

    from web3 import Web3

    mock_w3 = MagicMock(spec=Web3)
    mock_w3.is_connected.return_value = True
    mock_w3.eth.get_transaction_count.return_value = 0
    mock_w3.eth.gas_price = 30000000000  # 30 gwei
    mock_w3.to_wei.side_effect = lambda v, u: int(v * 1e9)  # gwei conversion
    mock_w3.eth.send_raw_transaction.return_value = bytes.fromhex("0123456789abcdef" * 4)

    def mock_web3_init(provider):
        return mock_w3

    monkeypatch.setattr("web3.Web3.__new__", lambda cls, provider: mock_w3)
    return mock_w3


# --- Database & Auth Fixtures ---
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app

# Override the database with an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


# Inject the override so the auth routers hit the SQLite memory map instead of Postgres
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Recreate the database tables cleanly before every test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """Yield a functional ASGI HTTPX client bound to the FastAPI app context."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
