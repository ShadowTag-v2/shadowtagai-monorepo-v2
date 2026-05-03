"""Local audio recorder — subprocess-based SoX/arecord capture.

Records audio from the system microphone using SoX (rec) or arecord.
The audio is captured to a temporary WAV file for STT processing.
Raw audio bytes NEVER enter the LLM context.
"""

from __future__ import annotations

import contextlib
import logging
import os
import shutil
import subprocess
import tempfile

from ._types import RecordingAvailability, VoiceDependencyCheck

logger = logging.getLogger(__name__)


def check_recording_deps() -> VoiceDependencyCheck:
    """Check if audio recording dependencies are available."""
    missing: list[str] = []
    install_cmd: str | None = None

    # Check for SoX (primary) or arecord (fallback)
    has_sox = shutil.which("rec") is not None or shutil.which("sox") is not None
    has_arecord = shutil.which("arecord") is not None

    if not has_sox and not has_arecord:
        missing.append("sox")
        # Detect package manager for install hint
        if shutil.which("brew"):
            install_cmd = "brew install sox"
        elif shutil.which("apt-get"):
            install_cmd = "apt-get install -y sox"
        elif shutil.which("dnf"):
            install_cmd = "dnf install -y sox"

    return VoiceDependencyCheck(
        available=len(missing) == 0,
        missing=missing,
        install_command=install_cmd,
    )


def check_recording_available() -> RecordingAvailability:
    """Check if audio recording is possible on this system."""
    deps = check_recording_deps()
    if not deps.available:
        hint = f" Install with: {deps.install_command}" if deps.install_command else ""
        return RecordingAvailability(
            available=False,
            reason=f"Missing: {', '.join(deps.missing)}.{hint}",
        )
    return RecordingAvailability(available=True)


class LocalRecorder:
    """Local audio recorder using SoX subprocess.

    Records audio to a temporary WAV file. The caller is responsible
    for processing the audio (e.g., sending to local Whisper STT)
    and cleaning up the temporary file.

    Safe Harbor: No audio streaming to remote services. All audio
    stays on the local filesystem.
    """

    __slots__ = ("_process", "_output_path", "_sample_rate", "_channels")

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> None:
        self._process: subprocess.Popen | None = None
        self._output_path: str = ""
        self._sample_rate = sample_rate
        self._channels = channels

    @property
    def is_recording(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def output_path(self) -> str:
        return self._output_path

    def start(self) -> str:
        """Start recording audio to a temporary WAV file.

        Returns the path to the output file.
        """
        if self.is_recording:
            return self._output_path

        # Create temp file for audio output
        fd, self._output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

        # Prefer SoX 'rec' command
        if shutil.which("rec"):
            cmd = [
                "rec",
                "-q",  # quiet
                "-r",
                str(self._sample_rate),
                "-c",
                str(self._channels),
                "-b",
                "16",  # 16-bit
                self._output_path,
            ]
        elif shutil.which("arecord"):
            cmd = [
                "arecord",
                "-q",
                "-f",
                "S16_LE",
                "-r",
                str(self._sample_rate),
                "-c",
                str(self._channels),
                self._output_path,
            ]
        else:
            msg = "No audio recorder available (need sox or arecord)"
            raise RuntimeError(msg)

        self._process = subprocess.Popen(  # noqa: S603
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug("Recording started: %s (pid=%d)", self._output_path, self._process.pid)
        return self._output_path

    def stop(self) -> str:
        """Stop recording and return the path to the audio file."""
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            self._process = None
            logger.debug("Recording stopped: %s", self._output_path)
        return self._output_path

    def cleanup(self) -> None:
        """Stop recording and delete the temporary file."""
        self.stop()
        if self._output_path and os.path.exists(self._output_path):
            with contextlib.suppress(OSError):
                os.unlink(self._output_path)
            self._output_path = ""
