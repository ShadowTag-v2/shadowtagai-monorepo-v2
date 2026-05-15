# Quick Start - Text Input Only

Test the multi-LLM consensus system with simple text input (no voice/microphone needed).

## 1. Install Minimal Dependencies

```bash

# Create virtual environment

python3 -m venv venv

# Activate it

source venv/bin/activate  # Mac/Linux

# OR on Windows: venv\Scripts\activate

# Install minimal dependencies

pip install --upgrade pip
pip install -r requirements-text-only.txt

```

## 2. Set Your API Key(s)

**Minimum required:**

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'

```

**Optional (for full consensus):**

```bash
export GOOGLE_API_KEY='AIza...'        # Gemini
export OPENAI_API_KEY='sk-proj-...'   # GPT-4
export XAI_API_KEY='xai-...'           # Grok

```

### How to Get API Keys



- **Anthropic (Claude)**: https://console.anthropic.com/


- **Google (Gemini)**: https://aistudio.google.com/app/apikey


- **OpenAI (GPT-4)**: https://platform.openai.com/api-keys


- **xAI (Grok)**: https://x.ai/api

## 3. Run Text-Only Test

```bash
python test_consensus_text.py

```

**Example session:**

```

Multi-LLM Consensus Orchestrator - Text Mode

Enter your query (or press Enter for default test query):
> What are the key advantages of edge AI compute?

Processing...

[Layer 1] Claude initial reasoning...
[Layer 2] Broadcasting to available models...
[Layer 2] Received 3 responses
[Layer 2.5] Cross-validation peer reviews...
[Layer 2.5] Completed 6 peer reviews
[Layer 3] Final synthesis by Claude...
[✓] Consensus complete

================================================================================
FINAL CONSENSUS SYNTHESIS
================================================================================

[Your synthesized answer here...]

================================================================================
EXECUTION METADATA
================================================================================

Models Used:


  - Layer 1 (Claude): Initial reasoning


  - Layer 2: 3 models
    • gemini-2.0-flash-exp
    • grok-2-latest
    • gpt-4-turbo-preview


  - Layer 3 (Claude): Final synthesis

Token Usage:


  - Input: 4,521


  - Output: 3,713


  - Total: 8,234

Peer Reviews: 6

```

## 4. Cost-Saving Tip

**Start with Claude only:**

```bash

# Only set Anthropic key

export ANTHROPIC_API_KEY='sk-ant-...'

# Run test - will use Claude only (cheaper)

python test_consensus_text.py

```

This makes **2 API calls** instead of 11.

**Add other models later** for important queries where you want full consensus.

## 5. Common Issues

### "No module named 'anthropic'"

```bash
pip install -r requirements-text-only.txt

```

### "API key not found"

```bash

# Make sure you exported the key in the SAME terminal session

echo $ANTHROPIC_API_KEY  # Should print your key

# If empty, export it again

export ANTHROPIC_API_KEY='your-key-here'

```

### "Module not found" errors

```bash

# Make sure virtual environment is activated

source venv/bin/activate

# Verify with:

which python  # Should show path to venv/bin/python

```

## 6. Next Steps

Once text mode works:



1. **Add more models** (optional):
   ```bash
   pip install google-generativeai openai
   export GOOGLE_API_KEY='...'
   export OPENAI_API_KEY='...'
   ```



2. **Install voice support** (optional):
   ```bash
   # On Mac:
   brew install portaudio ffmpeg
   pip install -r requirements.txt

   # Test voice mode:
   python voice_client.py --mode single
   ```

## 7. Example Queries to Test

```

"Compare the tradeoffs between monolithic and microservices architectures"

"What are the key risks in deploying edge AI infrastructure at cell tower sites?"

"Analyze the business model opportunities for AI-powered research tools"

"What are the main challenges in building multi-model consensus systems?"

```

---

**Need help?** Check the main README.md or test with the default query first (just press Enter when prompted).
