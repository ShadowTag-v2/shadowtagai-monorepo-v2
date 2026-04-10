# LegalTrack

LegalTrack is a smart legal calendar and deadline engine designed for zero-trust environments.
It extracts deadlines from court notices via email/portals, maps them to jurisdictional rules, and automatically syncs them to Google/Outlook calendars.

## Architecture
- **Infrastructure**: Google Cloud Run (Serverless) + Vertex AI + Cloud Tasks + CloudSQL (PostgreSQL).
- **Backend**: Python 3.12+ with FastAPI.
- **AI Extraction**: Gemini 3.1 Pro via Vertex AI.

## Security Posture
- 100% Encryption at Rest (KMS) and in Transit.
- No unencrypted databases or local-only stores.
- Strict OAuth scope selection (least-privilege).
