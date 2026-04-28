# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Voice Capture Client for Multi-LLM Consensus Orchestrator
Cross-platform voice capture using Whisper for transcription
"""

import asyncio
import sys
import tempfile
import threading
from pathlib import Path

import keyboard
import speech_recognition as sr
from consensus_orchestrator import ConsensusOrchestrator
from rich.console import Console
from rich.panel import Panel

console = Console()


class VoiceCapture:
    """Cross-platform voice capture using system microphone.
    Supports push-to-talk or continuous listening.
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
            try:
                import whisper

                console.print(f"[yellow]Loading Whisper {model_size} model...[/yellow]")
                self.whisper_model = whisper.load_model(model_size)
                console.print("[green]✓ Whisper model loaded[/green]")
            except ImportError:
                console.print(
                    "[red]ERROR: openai-whisper not installed. Run: pip install openai-whisper[/red]",
                )
                sys.exit(1)
        else:
            self.whisper_model = None

        # Adjust for ambient noise
        try:
            with sr.Microphone() as source:
                console.print("[yellow]Calibrating for ambient noise... (stay quiet)[/yellow]")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                console.print("[green]✓ Calibration complete[/green]")
        except Exception as e:
            console.print(f"[red]ERROR: Could not access microphone: {e}[/red]")
            console.print(
                "[yellow]Make sure your microphone is connected and permissions are granted[/yellow]",
            )
            sys.exit(1)

    def list_microphones(self):
        """Show available microphones"""
        console.print("\n[bold cyan]Available Microphones:[/bold cyan]")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            console.print(f"  [{index}] {name}")

    def capture_audio(self, timeout: int = None, phrase_time_limit: int = None) -> str:
        """Capture audio from microphone and transcribe.

        Args:
            timeout: Max seconds to wait for speech to start (None = infinite)
            phrase_time_limit: Max seconds for entire phrase (None = infinite)

        """
        with sr.Microphone() as source:
            console.print("\n[bold green]🎤 Listening... (speak now)[/bold green]")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
                console.print("[yellow]⏳ Transcribing...[/yellow]")

                # Transcribe based on selected engine
                if self.engine == "whisper_local":
                    return self._transcribe_whisper_local(audio)
                if self.engine == "google":
                    return self._transcribe_google(audio)
                raise ValueError(f"Unknown engine: {self.engine}")

            except sr.WaitTimeoutError:
                console.print("[red]✗ No speech detected (timeout)[/red]")
                return None
            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]")
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

    def _transcribe_google(self, audio: sr.AudioData) -> str:
        """Use Google Speech Recognition (free, no API key needed)"""
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            console.print("[red]✗ Could not understand audio[/red]")
            return None
        except sr.RequestError as e:
            console.print(f"[red]✗ Google API error: {e}[/red]")
            return None


class VoiceConsensusClient:
    """Desktop client that captures voice and sends to consensus orchestrator."""

    def __init__(
        self,
        voice_capture: VoiceCapture,
        orchestrator: ConsensusOrchestrator,
        hotkey: str = "ctrl+shift+space",
    ):
        self.voice = voice_capture
        self.orchestrator = orchestrator
        self.hotkey = hotkey

    async def send_to_orchestrator(self, query: str) -> dict:
        """Send transcribed query to consensus orchestrator"""
        result = await self.orchestrator.execute_full_consensus(query)
        return result

    def run_push_to_talk(self):
        """Run in push-to-talk mode: Hold hotkey to speak.
        Note: Keyboard hotkeys may require elevated permissions on Mac.
        """
        console.print(
            Panel.fit(
                f"[bold cyan]Voice Consensus Orchestrator[/bold cyan]\n\n"
                f"🎤 Mode: Push-to-Talk\n"
                f"⌨️  Hotkey: {self.hotkey}\n"
                f"🔊 Engine: {self.voice.engine}\n\n"
                f"[yellow]Press and hold {self.hotkey} to speak[/yellow]\n"
                f"[dim]Press Ctrl+C to exit[/dim]",
                border_style="cyan",
            ),
        )

        try:
            while True:
                console.print(f"\n[dim]Waiting for {self.hotkey}...[/dim]")
                # Wait for hotkey press
                keyboard.wait(self.hotkey)
                console.print("\n[bold green]🔴 RECORDING (release to stop)...[/bold green]")

                # Capture while holding
                audio_chunks = []

                def record():
                    with sr.Microphone() as source:
                        while keyboard.is_pressed(self.hotkey):
                            try:
                                chunk = self.voice.recognizer.listen(
                                    source,
                                    timeout=0.5,
                                    phrase_time_limit=0.5,
                                )
                                audio_chunks.append(chunk)  # noqa: B023
                            except sr.WaitTimeoutError:
                                continue

                record_thread = threading.Thread(target=record)
                record_thread.start()

                # Wait for release
                keyboard.wait(self.hotkey, suppress=True)
                record_thread.join()

                if audio_chunks:
                    # Combine chunks
                    combined = sr.AudioData(
                        b"".join([chunk.get_raw_data() for chunk in audio_chunks]),
                        audio_chunks[0].sample_rate,
                        audio_chunks[0].sample_width,
                    )

                    console.print("[yellow]⏳ Transcribing...[/yellow]")
                    transcript = self.voice._transcribe_whisper_local(combined)

                    if transcript:
                        console.print(f"\n[cyan]📝 You said:[/cyan] {transcript}\n")

                        # Send to orchestrator
                        console.print(
                            "[yellow]🤖 Processing with Consensus Orchestrator...[/yellow]",
                        )
                        result = asyncio.run(self.send_to_orchestrator(transcript))

                        # Display result
                        self._display_result(result)

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
        except Exception as e:
            console.print(f"\n[red]ERROR: {e}[/red]")
            console.print(
                "[yellow]Note: On Mac, hotkeys may require accessibility permissions.[/yellow]",
            )
            console.print(
                "[yellow]Try running in single-query mode instead: --mode single[/yellow]",
            )

    def run_continuous(self):
        """Run in continuous listening mode: Say wake word to activate"""
        wake_word = "hey consensus"

        console.print(
            Panel.fit(
                f"[bold cyan]Voice Consensus Orchestrator[/bold cyan]\n\n"
                f"🎤 Mode: Continuous Listening\n"
                f"🗣️  Wake word: '{wake_word}'\n"
                f"🔊 Engine: {self.voice.engine}\n\n"
                f"[yellow]Say '{wake_word}' followed by your query[/yellow]\n"
                f"[dim]Press Ctrl+C to exit[/dim]",
                border_style="cyan",
            ),
        )

        try:
            while True:
                console.print("\n[dim]Listening for wake word...[/dim]")

                # Capture audio
                transcript = self.voice.capture_audio(timeout=10)

                if transcript:  # noqa: SIM102
                    # Check for wake word
                    if wake_word.lower() in transcript.lower():
                        query = transcript.lower().replace(wake_word.lower(), "").strip()

                        if query:
                            console.print(f"\n[cyan]📝 Query:[/cyan] {query}\n")

                            # Process
                            console.print(
                                "[yellow]🤖 Processing with Consensus Orchestrator...[/yellow]",
                            )
                            result = asyncio.run(self.send_to_orchestrator(query))
                            self._display_result(result)
                        else:
                            console.print(
                                "[yellow]⚠️  Wake word detected but no query provided[/yellow]",
                            )

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")

    def run_single_query(self):
        """Capture single query and exit (useful for testing)"""
        console.print(
            Panel.fit(
                "[bold cyan]Voice Consensus Orchestrator[/bold cyan]\n"
                "[yellow]Speak your query now...[/yellow]",
                border_style="cyan",
            ),
        )

        transcript = self.voice.capture_audio(phrase_time_limit=30)

        if transcript:
            console.print(f"\n[cyan]📝 You said:[/cyan] {transcript}\n")
            console.print("[yellow]🤖 Processing with Consensus Orchestrator...[/yellow]\n")

            result = asyncio.run(self.send_to_orchestrator(transcript))
            self._display_result(result)

    def _display_result(self, result: dict):
        """Pretty-print orchestrator result"""
        console.print("\n" + "=" * 80)
        console.print(
            Panel.fit(
                result["final_synthesis"],
                title="[bold green]✓ CONSENSUS RESULT[/bold green]",
                border_style="green",
            ),
        )

        # Show execution summary
        result.get("execution_summary", {})
        layer1_tokens = result["token_usage"]["layer1"]
        total_input = layer1_tokens["input"] + result["token_usage"]["layer3"]["input"]
        total_output = layer1_tokens["output"] + result["token_usage"]["layer3"]["output"]

        console.print(
            f"\n[dim]Models: {len(result['layer2_responses']) + 2} | "
            f"Tokens: {total_input + total_output} | "
            f"Peer Reviews: {sum(len(v) for v in result['peer_reviews'].values()) if result['peer_reviews'] else 0}[/dim]",
        )


# === MAIN ENTRY POINT ===


def main():
    """Main CLI for voice-enabled consensus orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Consensus Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["push-to-talk", "continuous", "single"],
        default="single",
        help="Voice capture mode (default: single)",
    )
    parser.add_argument(
        "--engine",
        choices=["whisper_local", "google"],
        default="whisper_local",
        help="Transcription engine (default: whisper_local)",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper model size: tiny/base/small/medium/large (default: base)",
    )
    parser.add_argument(
        "--list-mics",
        action="store_true",
        help="List available microphones and exit",
    )
    parser.add_argument(
        "--hotkey",
        default="ctrl+shift+space",
        help="Hotkey for push-to-talk mode (default: ctrl+shift+space)",
    )

    args = parser.parse_args()

    # List microphones if requested
    if args.list_mics:
        voice = VoiceCapture(transcription_engine=args.engine)
        voice.list_microphones()
        return

    # Initialize
    console.print("[bold cyan]Initializing Voice Consensus Orchestrator...[/bold cyan]")

    voice_capture = VoiceCapture(transcription_engine=args.engine, model_size=args.model)

    orchestrator = ConsensusOrchestrator()

    client = VoiceConsensusClient(
        voice_capture=voice_capture,
        orchestrator=orchestrator,
        hotkey=args.hotkey,
    )

    # Run selected mode
    if args.mode == "push-to-talk":
        client.run_push_to_talk()
    elif args.mode == "continuous":
        client.run_continuous()
    elif args.mode == "single":
        client.run_single_query()


if __name__ == "__main__":
    main()
