"""Voice session orchestrator.

Coordinates recording → STT → text injection into agent context.
The orchestrator enforces the text-only bottleneck: raw audio never
reaches the LLM.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from .gate import is_voice_enabled
from .recorder import LocalRecorder, check_recording_available
from .stt_local import LocalWhisperSTT, is_whisper_available

logger = logging.getLogger(__name__)


class VoiceSession:
    """Orchestrates a voice input session.

    Flow:
    1. Check dependencies (SoX + Whisper)
    2. Start recording via LocalRecorder
    3. On stop, run local Whisper STT
    4. Return TEXT ONLY to the caller
    5. Clean up temp audio file

    Safe Harbor: No audio bytes leave the machine. No remote STT APIs.
    """

    __slots__ = (
        "_recorder",
        "_stt",
        "_on_text",
        "_active",
        "_start_time",
        "_whisper_model",
    )

    def __init__(
        self,
        on_text: Callable[[str], None] | None = None,
        whisper_model: str = "base",
    ) -> None:
        self._recorder = LocalRecorder()
        self._stt: LocalWhisperSTT | None = None
        self._on_text = on_text
        self._active = False
        self._start_time: float = 0
        self._whisper_model = whisper_model

    @property
    def is_active(self) -> bool:
        return self._active

    def check_ready(self) -> tuple[bool, str]:
        """Check if voice input is ready.

        Returns (ready, reason) tuple.
        """
        if not is_voice_enabled():
            return False, "Voice input is not enabled"

        rec_check = check_recording_available()
        if not rec_check.available:
            return False, rec_check.reason or "Recording not available"

        if not is_whisper_available():
            return False, ("Whisper not installed. Install with: pip install faster-whisper")

        return True, "Ready"

    def start(self) -> bool:
        """Start recording.

        Returns True if recording started, False if prerequisites fail.
        """
        ready, reason = self.check_ready()
        if not ready:
            logger.warning("Voice session not ready: %s", reason)
            return False

        if self._active:
            logger.warning("Voice session already active")
            return False

        # Lazy-load STT model
        if self._stt is None:
            self._stt = LocalWhisperSTT(model_name=self._whisper_model)
            self._stt.load_model()

        self._recorder.start()
        self._active = True
        self._start_time = time.monotonic()
        logger.info("Voice recording started")
        return True

    def stop(self) -> str | None:
        """Stop recording and transcribe.

        Returns the transcribed text, or None on failure.
        This is the TEXT-ONLY BOTTLENECK — the return value is the
        ONLY thing that should enter the agent context.
        """
        if not self._active:
            return None

        self._active = False
        audio_path = self._recorder.stop()
        duration = time.monotonic() - self._start_time
        logger.info("Voice recording stopped (%.1fs), transcribing...", duration)

        try:
            text = self._stt.transcribe(audio_path) if self._stt else None
        except Exception as exc:
            logger.error("Transcription failed: %s", exc)
            text = None
        finally:
            # Always clean up the audio file
            self._recorder.cleanup()

        if text and self._on_text:
            self._on_text(text)

        return text

    def cancel(self) -> None:
        """Cancel recording without transcribing."""
        self._active = False
        self._recorder.cleanup()
        logger.info("Voice recording cancelled")
