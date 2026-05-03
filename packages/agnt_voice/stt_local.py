"""Local Whisper STT — text-only output bottleneck.

Runs Whisper locally for speech-to-text. The TEXT output is the
only thing that enters the agent context. Raw audio bytes are
NEVER passed to the LLM.

Requires: pip install openai-whisper (or faster-whisper)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def is_whisper_available() -> bool:
    """Check if Whisper is installed."""
    try:
        import whisper  # noqa: F401

        return True
    except ImportError:
        pass
    try:
        from faster_whisper import WhisperModel  # noqa: F401

        return True
    except ImportError:
        pass
    return False


class LocalWhisperSTT:
    """Local Whisper speech-to-text.

    Safe Harbor text-only bottleneck:
    - Input: path to WAV file on local disk
    - Output: plain text string
    - No audio bytes ever touch the LLM context
    - No remote API calls (Whisper runs locally)
    """

    __slots__ = ("_model", "_model_name", "_use_faster")

    def __init__(self, model_name: str = "base") -> None:
        self._model = None
        self._model_name = model_name
        self._use_faster = False

    def load_model(self) -> None:
        """Load the Whisper model. Call once at startup."""
        # Prefer faster-whisper for CTranslate2 acceleration
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8")
            self._use_faster = True
            logger.info("Loaded faster-whisper model: %s", self._model_name)
            return
        except ImportError:
            pass

        # Fall back to openai-whisper
        try:
            import whisper

            self._model = whisper.load_model(self._model_name)
            self._use_faster = False
            logger.info("Loaded whisper model: %s", self._model_name)
            return
        except ImportError:
            pass

        msg = (
            "No Whisper implementation found. Install one with:\n"
            "  pip install faster-whisper   # recommended\n"
            "  pip install openai-whisper   # alternative"
        )
        raise RuntimeError(msg)

    def transcribe(self, audio_path: str) -> str:
        """Transcribe a WAV file to text.

        Returns the transcription as a plain string.
        This is the TEXT-ONLY BOTTLENECK — the return value is
        the ONLY thing that enters the agent context.
        """
        if self._model is None:
            self.load_model()

        if self._use_faster:
            segments, _info = self._model.transcribe(audio_path, beam_size=5)
            return " ".join(seg.text.strip() for seg in segments)
        else:
            result = self._model.transcribe(audio_path)
            return result.get("text", "").strip()


def transcribe_file(audio_path: str, model: str = "base") -> str | None:
    """One-shot transcription convenience function.

    Returns the transcribed text, or None if Whisper is not available.
    """
    if not is_whisper_available():
        logger.warning("Whisper not available for transcription")
        return None

    stt = LocalWhisperSTT(model_name=model)
    return stt.transcribe(audio_path)
