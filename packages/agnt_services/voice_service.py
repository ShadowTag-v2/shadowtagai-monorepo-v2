# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Voice Service — Ported from Claude Code v2.1.91 voice.ts.

Audio recording service for push-to-talk voice input.
Supports native audio (cpal), SoX rec, and ALSA arecord fallbacks.

Reference: Claude Code v2.1.91 src/services/voice.ts (526 lines)
"""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess
from dataclasses import dataclass
from collections.abc import Callable
import contextlib

logger = logging.getLogger(__name__)

RECORDING_SAMPLE_RATE = 16000
RECORDING_CHANNELS = 1
SILENCE_DURATION_SECS = "2.0"
SILENCE_THRESHOLD = "3%"


@dataclass
class RecordingAvailability:
    available: bool
    reason: str | None = None


@dataclass
class VoiceDependencies:
    available: bool
    missing: list[str]
    install_command: str | None = None


def has_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def detect_package_manager() -> str | None:
    system = platform.system()
    if system == "Darwin" and has_command("brew"):
        return "brew install sox"
    if system == "Linux":
        if has_command("apt-get"):
            return "sudo apt-get install sox"
        if has_command("dnf"):
            return "sudo dnf install sox"
        if has_command("pacman"):
            return "sudo pacman -S sox"
    return None


def check_voice_dependencies() -> VoiceDependencies:
    if platform.system() == "Linux" and has_command("arecord"):
        return VoiceDependencies(available=True, missing=[])
    if has_command("rec"):
        return VoiceDependencies(available=True, missing=[])
    pm = detect_package_manager()
    return VoiceDependencies(available=False, missing=["sox (rec command)"], install_command=pm)


def check_recording_availability() -> RecordingAvailability:
    system = platform.system()
    if system == "Darwin" and has_command("rec"):
        return RecordingAvailability(available=True)
    if system == "Linux" and (has_command("arecord") or has_command("rec")):
        return RecordingAvailability(available=True)
    if system == "Windows":
        return RecordingAvailability(available=False, reason="Voice mode requires native audio module on Windows.")
    pm = detect_package_manager()
    if pm:
        return RecordingAvailability(available=False, reason=f"Voice mode requires SoX. Install: {pm}")
    return RecordingAvailability(available=False, reason="Voice mode requires SoX for audio recording.")


class VoiceRecorder:
    """Manages audio recording via SoX or arecord subprocess."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[bytes] | None = None

    @property
    def is_recording(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start_recording(
        self,
        on_data: Callable[[bytes], None],
        on_end: Callable[[], None],
        *,
        silence_detection: bool = True,
    ) -> bool:
        system = platform.system()
        if system == "Linux" and has_command("arecord"):
            return self._start_arecord(on_data, on_end)
        if has_command("rec"):
            return self._start_sox(on_data, on_end, silence_detection=silence_detection)
        return False

    def _start_sox(self, on_data: Callable[[bytes], None], on_end: Callable[[], None], *, silence_detection: bool) -> bool:
        args = [
            "rec",
            "-q",
            "--buffer",
            "1024",
            "-t",
            "raw",
            "-r",
            str(RECORDING_SAMPLE_RATE),
            "-e",
            "signed",
            "-b",
            "16",
            "-c",
            str(RECORDING_CHANNELS),
            "-",
        ]
        if silence_detection:
            args.extend(["silence", "1", "0.1", SILENCE_THRESHOLD, "1", SILENCE_DURATION_SECS, SILENCE_THRESHOLD])
        try:
            self._process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            logger.error("Failed to start SoX: %s", exc)
            return False
        self._read_output(on_data, on_end)
        return True

    def _start_arecord(self, on_data: Callable[[bytes], None], on_end: Callable[[], None]) -> bool:
        args = ["arecord", "-f", "S16_LE", "-r", str(RECORDING_SAMPLE_RATE), "-c", str(RECORDING_CHANNELS), "-t", "raw", "-q", "-"]
        try:
            self._process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            logger.error("Failed to start arecord: %s", exc)
            return False
        self._read_output(on_data, on_end)
        return True

    def _read_output(self, on_data: Callable[[bytes], None], on_end: Callable[[], None]) -> None:
        import threading

        def _reader() -> None:
            proc = self._process
            if proc is None or proc.stdout is None:
                return
            try:
                while True:
                    chunk = proc.stdout.read(4096)
                    if not chunk:
                        break
                    on_data(chunk)
            except OSError:
                pass
            finally:
                self._process = None
                on_end()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

    def stop_recording(self) -> None:
        if self._process is not None:
            with contextlib.suppress(OSError):
                self._process.terminate()
            self._process = None
