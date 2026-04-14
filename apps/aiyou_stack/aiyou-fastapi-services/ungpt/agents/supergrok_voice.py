"""L7: SuperGrok.4 - Voice (Static)

Role: The Announcer
- Converts executive briefing to speech-ready text
- Optimized for TTS delivery

Output: voice_script, audio (optional)
"""

from typing import Any

import httpx

VOICE_PROMPT = """You are the ANNOUNCER for a multi-model research pipeline.

Convert this executive briefing into a natural, conversational voice script.

EXECUTIVE BRIEFING:
{briefing}

Requirements:
1. Use natural speech patterns
2. Spell out abbreviations (e.g., "API" -> "A P I")
3. Use pauses where appropriate (marked with "...")
4. Keep under 60 seconds when spoken (~150 words)
5. Start with "Research complete." and end with "End of briefing."

VOICE SCRIPT:
"""


async def generate_voice(
    briefing: str, model: str, api_key: str, generate_audio: bool = False,
) -> dict[str, Any]:
    """Generate voice-ready script from briefing.

    Args:
        briefing: Executive briefing from L5
        model: SuperGrok model ID
        api_key: xAI API key
        generate_audio: Whether to generate actual audio (requires TTS service)

    Returns:
        {
            'script': str,
            'word_count': int,
            'estimated_duration_sec': float,
            'audio_url': str or None,
            'cost': float
        }

    """
    prompt = VOICE_PROMPT.format(briefing=briefing)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "max_tokens": 400,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Clean up the script
    script = content.replace("VOICE SCRIPT:", "").strip()

    # Ensure proper start/end
    if not script.startswith("Research complete"):
        script = "Research complete. " + script
    if not script.endswith("End of briefing."):
        script = script.rstrip(".") + ". End of briefing."

    # Calculate metrics
    word_count = len(script.split())
    estimated_duration = word_count / 2.5  # ~150 words per minute

    # Calculate cost
    input_tokens = len(prompt.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000

    result = {
        "script": script,
        "word_count": word_count,
        "estimated_duration_sec": estimated_duration,
        "audio_url": None,
        "cost": cost,
    }

    # Generate audio if requested
    if generate_audio:
        audio_url = await _generate_tts(script)
        result["audio_url"] = audio_url

    return result


async def _generate_tts(script: str) -> str | None:
    """Generate TTS audio from script.

    Placeholder - would integrate with:
    - ElevenLabs
    - Google Cloud TTS
    - Amazon Polly
    - Local Piper TTS
    """
    # TODO: Implement TTS integration
    # For now, return None (script is still usable for manual TTS)
    return None
