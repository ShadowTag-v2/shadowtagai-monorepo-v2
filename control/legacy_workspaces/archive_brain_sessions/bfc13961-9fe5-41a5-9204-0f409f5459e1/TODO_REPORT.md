# Outstanding TODOs Report
**Total Found**: 400+ markers.
**Critical Areas**:

## 1. AI Interpreter (`src/services/ai_interpreter.py`)
- [ ] Implement MediaPipe Holistic processing (C++/Python bindings)
- [ ] Implement gesture classification
- [ ] Implement emotion detection
- [ ] Implement text generation
- [ ] Implement art generation & NFT compilation

## 2. Calendar Integration (`src/services/calendar_integration.py`)
- [ ] Implement Google Calendar API integration
- [ ] Implement Microsoft Graph API integration
- [ ] Implement Email/SMS/Slack/Push notifications
- [ ] Implement review queue logic

## 3. NFT Minter (`src/services/nft_minter.py`)
- [ ] Implement actual IPFS upload
- [ ] Implement actual blockchain minting
- [ ] Implement NFT transfer & price setting
- [ ] Implement marketplace search & analytics

## 4. Contractual (`src/services/contractual/`)
- [ ] Implement reconstruction logic (`multi_agent_debate.py`)
- [ ] Call Anthropic Claude API (`conflict_detection.py`)

## 5. Orchestrator (`src/orchestrator/`)
- [ ] Integrate with actual metrics provider (Prometheus/GCP)
- [ ] Use Gemini function calling for candidate scoring

## 6. General
- [ ] `src/services/rule_engine.py`: Implement database loading
- [ ] `src/services/deadline_extractor.py`: PDF/DOCX extraction & OCR
