#!/usr/bin/env python3
"""Voice-Enabled UnGPT Client
Cross-platform voice capture for Mac/PC with hotkey activation
Integrates with UnGPT atomic orchestrator and consensus system
"""

import argparse
import asyncio
import tempfile
from pathlib import Path
from typing import Any

import speech_recognition as sr
import whisper

# Try to import optional dependencies
try:
    from rich.console import Console
    from rich.panel import Panel

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

try:
    import keyboard  # noqa: F401

    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


class VoiceCapture:
    """Cross-platform voice capture using system microphone
    Supports push-to-talk or continuous listening
    """

    def __init__(
        self,
        transcription_engine: str = "whisper_local",
        model_size: str = "base",
        language: str = "en",
    ):
        self.engine = transcription_engine
        self.language = language
        self.recognizer = sr.Recognizer()

        # Initialize Whisper if using local
        if transcription_engine == "whisper_local":
            self._print("[yellow]Loading Whisper {model_size} model...[/yellow]")
            self.whisper_model = whisper.load_model(model_size)
            self._print("[green]✓ Whisper model loaded[/green]")

        # Adjust for ambient noise
        with sr.Microphone() as source:
            self._print("[yellow]Calibrating for ambient noise... (stay quiet)[/yellow]")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self._print("[green]✓ Calibration complete[/green]")

    def _print(self, message: str):
        """Print with or without rich formatting"""
        if RICH_AVAILABLE and console:
            console.print(message)
        else:
            # Strip rich formatting tags for plain print
            import re

            plain_message = re.sub(r"\[.*?\]", "", message)
            print(plain_message)

    def list_microphones(self):
        """Show available microphones"""
        self._print("\n[bold cyan]Available Microphones:[/bold cyan]")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            self._print(f"  [{index}] {name}")

    def capture_audio(
        self,
        timeout: int | None = None,
        phrase_time_limit: int | None = None,
    ) -> str | None:
        """Capture audio from microphone and transcribe

        Args:
            timeout: Max seconds to wait for speech to start (None = infinite)
            phrase_time_limit: Max seconds for entire phrase (None = infinite)

        """
        with sr.Microphone() as source:
            self._print("\n[bold green]🎤 Listening... (speak now)[/bold green]")

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )

                self._print("[yellow]⏳ Transcribing...[/yellow]")

                # Transcribe based on selected engine
                if self.engine == "whisper_local":
                    return self._transcribe_whisper_local(audio)
                if self.engine == "google":
                    return self._transcribe_google(audio)
                raise ValueError(f"Unknown engine: {self.engine}")

            except sr.WaitTimeoutError:
                self._print("[red]✗ No speech detected (timeout)[/red]")
                return None
            except Exception as e:
                self._print(f"[red]✗ Error: {e}[/red]")
                return None

    def _transcribe_whisper_local(self, audio: sr.AudioData) -> str:
        """Use local Whisper model (most reliable, works offline)"""
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio.get_wav_data())
            temp_path = f.name

        # Transcribe
        result = self.whisper_model.transcribe(temp_path, language=self.language)

        # Cleanup
        Path(temp_path).unlink()

        return result["text"].strip()

    def _transcribe_google(self, audio: sr.AudioData) -> str | None:
        """Use Google Speech Recognition (free, no API key needed)"""
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            self._print("[red]✗ Could not understand audio[/red]")
            return None
        except sr.RequestError as e:
            self._print(f"[red]✗ Google API error: {e}[/red]")
            return None


class VoiceUnGPTClient:
    """Desktop client that captures voice and sends to UnGPT orchestrator"""

    def __init__(
        self,
        voice_capture: VoiceCapture,
        orchestrator: Any,
        use_consensus: bool = False,
        consensus_orchestrator: Any | None = None,
    ):
        self.voice = voice_capture
        self.orchestrator = orchestrator
        self.use_consensus = use_consensus
        self.consensus_orchestrator = consensus_orchestrator

    def _print(self, message: str):
        """Print with or without rich formatting"""
        if RICH_AVAILABLE and console:
            console.print(message)
        else:
            import re

            plain_message = re.sub(r"\[.*?\]", "", message)
            print(plain_message)

    async def send_to_orchestrator(self, query: str) -> dict[str, Any]:
        """Send transcribed query to orchestrator"""
        if self.use_consensus and self.consensus_orchestrator:
            # Use multi-LLM consensus
            return await self.consensus_orchestrator.execute_full_consensus(query)
        # Use standard atomic orchestrator
        return await self.orchestrator.process_query(query)

    def run_single_query(self):
        """Capture single query and exit (useful for testing)"""
        if RICH_AVAILABLE and console:
            console.print(
                Panel.fit(
                    "[bold cyan]Voice UnGPT Orchestrator[/bold cyan]\n"
                    "[yellow]Speak your query now...[/yellow]",
                    border_style="cyan",
                ),
            )
        else:
            print("=" * 60)
            print("Voice UnGPT Orchestrator")
            print("Speak your query now...")
            print("=" * 60)

        transcript = self.voice.capture_audio(phrase_time_limit=30)

        if transcript:
            self._print(f"\n[cyan]📝 You said:[/cyan] {transcript}\n")

            self._print("[yellow]🤖 Processing with UnGPT Orchestrator...[/yellow]")
            result = asyncio.run(self.send_to_orchestrator(transcript))

            self._display_result(result)

    def run_continuous(self):
        """Run in continuous listening mode: Say wake word to activate"""
        wake_word = "hey ungpt"

        if RICH_AVAILABLE and console:
            console.print(
                Panel.fit(
                    f"[bold cyan]Voice UnGPT Orchestrator[/bold cyan]\n\n"
                    f"🎤 Mode: Continuous Listening\n"
                    f"🗣️  Wake word: '{wake_word}'\n"
                    f"🔊 Engine: {self.voice.engine}\n\n"
                    f"[yellow]Say '{wake_word}' followed by your query[/yellow]\n"
                    f"[dim]Press Ctrl+C to exit[/dim]",
                    border_style="cyan",
                ),
            )
        else:
            print("=" * 60)
            print("Voice UnGPT Orchestrator - Continuous Mode")
            print(f"Wake word: '{wake_word}'")
            print("Press Ctrl+C to exit")
            print("=" * 60)

        try:
            while True:
                self._print("\n[dim]Listening for wake word...[/dim]")

                # Capture audio
                transcript = self.voice.capture_audio(timeout=10)

                if transcript:  # noqa: SIM102
                    # Check for wake word
                    if wake_word.lower() in transcript.lower():
                        query = transcript.lower().replace(wake_word.lower(), "").strip()

                        if query:
                            self._print(f"\n[cyan]📝 Query:[/cyan] {query}\n")

                            # Process
                            self._print("[yellow]🤖 Processing with UnGPT Orchestrator...[/yellow]")
                            result = asyncio.run(self.send_to_orchestrator(query))

                            self._display_result(result)
                        else:
                            self._print(
                                "[yellow]⚠️  Wake word detected but no query provided[/yellow]",
                            )

        except KeyboardInterrupt:
            self._print("\n[yellow]Exiting...[/yellow]")

    def _display_result(self, result: dict[str, Any]):
        """Pretty-print orchestrator result"""
        self._print("\n" + "=" * 80)

        if "final_synthesis" in result:
            # Consensus result
            output = result["final_synthesis"]
            self._print("\n[bold green]✓ MULTI-LLM CONSENSUS RESULT[/bold green]\n")
        else:
            # Standard atomic result
            output = result.get("final_output", "No output generated")
            self._print("\n[bold green]✓ UNGPT ATOMIC ORCHESTRATOR RESULT[/bold green]\n")

        if RICH_AVAILABLE and console:
            console.print(Panel.fit(output, border_style="green"))
        else:
            print(output)

        # Show execution summary
        if "execution_summary" in result:
            summary = result["execution_summary"]
            self._print(
                f"\n[dim]Execution Time: {summary.get('avg_execution_time', 0):.2f}s | "
                f"Success Rate: {summary.get('success_rate', 0) * 100:.0f}% | "
                f"Threads: {result.get('audit_trail', {}).get('total_threads', 0)}[/dim]",
            )


def main():
    """Main CLI for voice-enabled UnGPT orchestrator"""
    parser = argparse.ArgumentParser(description="Voice UnGPT Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["single", "continuous"],
        default="single",
        help="Voice capture mode",
    )
    parser.add_argument(
        "--engine",
        choices=["whisper_local", "google"],
        default="whisper_local",
        help="Transcription engine",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper model size (tiny/base/small/medium/large)",
    )
    parser.add_argument(
        "--list-mics",
        action="store_true",
        help="List available microphones and exit",
    )
    parser.add_argument(
        "--consensus",
        action="store_true",
        help="Use multi-LLM consensus mode (requires API keys)",
    )

    args = parser.parse_args()

    # List microphones if requested
    if args.list_mics:
        voice = VoiceCapture(transcription_engine=args.engine)
        voice.list_microphones()
        return

    # Initialize
    print("Initializing Voice UnGPT Orchestrator...")

    voice_capture = VoiceCapture(transcription_engine=args.engine, model_size=args.model)

    # Note: In actual usage, you would initialize the orchestrator with proper API clients
    # This is a standalone script, so we'll print instructions instead
    print("\n" + "=" * 80)
    print("IMPORTANT: This is a standalone voice client.")
    print("To use with UnGPT orchestrator, you need to:")
    print("1. Set up API keys for Anthropic/OpenAI/Google/xAI")
    print("2. Import and initialize PNKLNAtomicOrchestrator or ConsensusOrchestrator")
    print("3. Pass the orchestrator instance to VoiceUnGPTClient")
    print("\nSee example_usage.py for complete integration example.")
    print("=" * 80 + "\n")

    # For demonstration, just capture and display the transcription
    transcript = voice_capture.capture_audio(phrase_time_limit=30)
    if transcript:
        print(f"\n✓ Transcribed: {transcript}\n")
        print("(In production mode, this would be sent to UnGPT orchestrator)")


if __name__ == "__main__":
    main()
