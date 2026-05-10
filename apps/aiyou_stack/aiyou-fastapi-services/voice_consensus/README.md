# Voice Consensus Orchestrator

Multi-LLM consensus system for personal research automation.

## 🎯 Never Lose Your Work Again

**GitHub Repository**: `ShadowTag-v2/shadowtag_v4-fastapi-services`
**Branch**: `claude/voice-consensus-orchestrator-01KnByRibAJhGMpXrun59rp4`

Every query is automatically saved in **3 locations**:


1. ✅ **Local archive** (`~/.consensus_archive.db`) - Instant access


2. ✅ **Git repository** (local + GitHub) - Version control


3. ✅ **Backup exports** (Markdown + JSON) - Human-readable

**Quick backup**: `./backup_consensus.sh` (pushes everything to GitHub)
**Verify backups**: `./verify_backups.sh` (checks all 3 locations)

See: `GITHUB_MIRROR.md` for complete backup strategy

---

## Two Modes Available

### 1. **Atomic Consensus** (Recommended for Complex Queries)

Combines atomic thread decomposition with multi-model consensus:


- Claude decomposes query into atomic threads (Purpose/Reasons/Brakes)


- Each thread → Gemini, Perplexity, SuperGrok


- Circular peer review (2 rounds)


- Claude stitches into execution-ready output

**Use for:** Complex multi-part questions, architecture design, business analysis

See: `QUICKSTART_ATOMIC.md`

### 2. **Simple Consensus** (For Single-Focus Queries)

Streamlined consensus without decomposition:


1. **Layer 1**: Claude Sonnet 4.5 initial reasoning


2. **Layer 2**: Parallel analysis by Gemini, Perplexity, SuperGrok


3. **Layer 2.5**: Cross-validation peer review (each model reviews others)


4. **Layer 3**: Claude final synthesis

**Use for:** Code review, quick validation, concept explanations

See: `QUICKSTART_MESSAGE.md`

## Architecture

```

Voice Input (Whisper)
    ↓
Query → Claude (Layer 1: Initial Reasoning)
    ↓
Broadcast to Layer 2 Models ↓
    ↓
┌───────────┬──────────┬──────────┐
│   Grok    │  Gemini  │  GPT-4   │
└───────────┴──────────┴──────────┘
    ↓           ↓          ↓
Cross-Validation (Peer Review)
    ↓
Claude (Layer 3: Final Synthesis)
    ↓
Final Answer

```

## Installation (MacBook Pro)

### Quick Start

```bash

# Navigate to the voice_consensus directory

cd voice_consensus

# Make setup script executable

chmod +x setup_mac.sh

# Run setup (installs dependencies)

./setup_mac.sh

# Activate virtual environment

source venv/bin/activate

# Set your API keys

export ANTHROPIC_API_KEY='your-key-here'
export GOOGLE_API_KEY='your-key-here'       # Optional
export OPENAI_API_KEY='your-key-here'       # Optional
export XAI_API_KEY='your-key-here'          # Optional

```

### Manual Installation

```bash

# Install Homebrew dependencies

brew install portaudio ffmpeg

# Create virtual environment

python3 -m venv venv
source venv/bin/activate

# Install Python packages

pip install --upgrade pip
pip install -r requirements.txt

```

## Configuration

### API Keys

The system requires at minimum:


- **ANTHROPIC_API_KEY** (required for Layer 1 and Layer 3)

Optional models for full consensus:


- **GOOGLE_API_KEY** (Gemini)


- **OPENAI_API_KEY** (GPT-4)


- **XAI_API_KEY** (Grok)

**Option 1: Environment Variables**

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
export GOOGLE_API_KEY='AIza...'
export OPENAI_API_KEY='sk-proj-...'
export XAI_API_KEY='xai-...'

```

**Option 2: .env File**

```bash
cp .env.example .env

# Edit .env with your actual keys

```

Then load in your shell:

```bash
source .env  # or: export $(cat .env | xargs)

```

## Usage

### Mode 1: Single Query (Recommended for Testing)

Speak one query, get consensus result, then exit.

```bash
python voice_client.py --mode single

```

**Example:**

```

🎤 Listening... (speak now)
📝 You said: Analyze the market opportunity for edge AI compute at cell tower sites

[Layer 1] Claude initial reasoning...
[Layer 2] Broadcasting to available models...
[Layer 2] Received 3 responses
[Layer 2.5] Cross-validation peer reviews...
[Layer 2.5] Completed 6 peer reviews
[Layer 3] Final synthesis by Claude...
[✓] Consensus complete

╭─────────────────────────────────╮
│    ✓ CONSENSUS RESULT           │
│                                 │
│ [Final synthesized answer...]   │
╰─────────────────────────────────╯

Models: 5 | Tokens: 8234 | Peer Reviews: 6

```

### Mode 2: Continuous Listening

Say wake word "hey consensus" followed by your query.

```bash
python voice_client.py --mode continuous

```

**Example:**

```

Listening for wake word...
📝 Query detected: "hey consensus, what are the advantages of multi-model consensus?"
🤖 Processing...

```

### Mode 3: Push-to-Talk

Hold `Ctrl+Shift+Space` to speak (release to stop).

```bash
python voice_client.py --mode push-to-talk

```

**Note on Mac**: Hotkeys require accessibility permissions:


1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**


2. Add your terminal app (Terminal.app, iTerm, etc.)


3. Restart terminal

### Mode Options

```bash

# List available microphones

python voice_client.py --list-mics

# Use different Whisper model (faster but less accurate)

python voice_client.py --mode single --model tiny

# Use different Whisper model (slower but more accurate)

python voice_client.py --mode single --model medium

# Use Google Speech Recognition instead of Whisper

python voice_client.py --mode single --engine google

# Custom hotkey for push-to-talk

python voice_client.py --mode push-to-talk --hotkey "ctrl+alt+v"

```

## Whisper Model Sizes

| Model  | Speed | Accuracy | Size | Recommended Use |
|--------|-------|----------|------|-----------------|
| tiny   | ⚡⚡⚡⚡ | ⭐⭐     | 75 MB | Quick testing |
| base   | ⚡⚡⚡   | ⭐⭐⭐   | 142 MB | **Default** |
| small  | ⚡⚡    | ⭐⭐⭐⭐ | 466 MB | Better accuracy |
| medium | ⚡     | ⭐⭐⭐⭐⭐ | 1.5 GB | Best accuracy |
| large  | 🐌    | ⭐⭐⭐⭐⭐ | 2.9 GB | Research quality |

**First run downloads model (one-time, 30-60 seconds)**

## Cost Considerations

Full consensus (all 4 models) makes **11 API calls per query**:


- Claude: 2x (Layer 1 + Layer 3)


- Grok: 3x (1 analysis + 2 peer reviews)


- Gemini: 3x (1 analysis + 2 peer reviews)


- GPT-4: 3x (1 analysis + 2 peer reviews)

**Estimated cost per query**: $0.10 - $0.50 depending on query complexity

**To reduce costs**:


- Use only required models (e.g., Claude + Gemini = 7 calls)


- Start with Claude only (set only `ANTHROPIC_API_KEY`)


- Add other models only for high-stakes queries

## Programmatic Usage

### Python Script

```python
import asyncio
from consensus_orchestrator import ConsensusOrchestrator

async def main():
    orchestrator = ConsensusOrchestrator()

    query = "Analyze the viability of edge AI compute infrastructure"

    result = await orchestrator.execute_full_consensus(query)

    print(result["final_synthesis"])
    print(f"Models consulted: {len(result['layer2_responses']) + 2}")
    print(f"Peer reviews: {sum(len(v) for v in result['peer_reviews'].values())}")

asyncio.run(main())

```

### CLI without Voice

```python

# test_consensus.py

import asyncio
from consensus_orchestrator import ConsensusOrchestrator

async def main():
    orchestrator = ConsensusOrchestrator()

    # Direct text query
    query = input("Enter your query: ")
    result = await orchestrator.execute_full_consensus(query)

    print("\n" + "="*80)
    print(result["final_synthesis"])
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())

```

Run with:

```bash
python test_consensus.py

```

## Troubleshooting

### "No module named 'pyaudio'"

**Mac:**

```bash
brew install portaudio
pip install pyaudio

```

**Ubuntu/Debian:**

```bash
sudo apt-get install portaudio19-dev
pip install pyaudio

```

**Windows:**

```bash
pip install pipwin
pipwin install pyaudio

```

### "Could not access microphone"



1. Check microphone is connected


2. Grant permissions: **System Preferences** → **Security & Privacy** → **Microphone**


3. Add terminal app to allowed list


4. Test with: `python voice_client.py --list-mics`

### "Hotkey doesn't work" (Mac)



1. **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**


2. Add Terminal.app (or iTerm, etc.)


3. Restart terminal


4. Or use `--mode single` or `--mode continuous` instead

### "Whisper model download stalls"



1. Check internet connection


2. Check disk space (models are 75MB - 2.9GB)


3. Try smaller model: `--model tiny`

### "Rate limiting errors"



1. Some API keys have rate limits


2. Add delays between queries


3. Check API usage dashboards

## Advanced Configuration

### Custom Model Selection

Edit `consensus_orchestrator.py` to customize which models to use:

```python

# In layer2_parallel_analysis method:

tasks = []

# Pick only the models you want

if self.xai_key:
    tasks.append(self._query_grok(base_prompt))
if self.gemini_model:
    tasks.append(self._query_gemini(base_prompt))

# Comment out to skip GPT-4:

# if self.openai_key:

#     tasks.append(self._query_gpt4(base_prompt))

```

### Audio Settings

Edit `voice_client.py` to adjust recording settings:

```python

# Increase phrase time limit for longer queries

transcript = self.voice.capture_audio(
    phrase_time_limit=60  # Allow up to 60 seconds
)

# Adjust ambient noise calibration

self.recognizer.adjust_for_ambient_noise(
    source,
    duration=3  # Longer calibration
)

# Adjust energy threshold for quieter environments

self.recognizer.energy_threshold = 300  # Lower = more sensitive

```

## File Structure

```

voice_consensus/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── setup_mac.sh                 # Mac setup script
├── .env.example                 # API key template
├── consensus_orchestrator.py    # Core multi-LLM logic
├── voice_client.py              # Voice capture + CLI
└── venv/                        # Virtual environment (created by setup)

```

## Research Use Cases

This system is designed for personal research automation:



- **Literature analysis**: Synthesize insights from multiple AI perspectives


- **Business analysis**: Get diverse viewpoints on market opportunities


- **Technical architecture**: Cross-validate design decisions


- **Risk assessment**: Identify blind spots through peer review


- **Hypothesis generation**: Explore ideas from multiple angles

## Limitations



1. **Cost**: Full consensus is expensive (~$0.20-0.50 per query with all models)


2. **Latency**: Sequential processing takes 30-90 seconds per query


3. **Voice accuracy**: Whisper works best with clear audio and minimal background noise


4. **API dependencies**: Requires active API keys and internet connection


5. **Mac hotkeys**: May require accessibility permissions

## Contributing

This is a personal research tool. Fork and modify as needed for your use case.

## License

MIT License - Use freely for personal research.

## Support

For issues:


1. Check troubleshooting section above


2. Verify API keys are set correctly


3. Test with `--mode single` first


4. Check model availability (some may have waitlists)

---

**Built for personal research automation. Query responsibly.**
