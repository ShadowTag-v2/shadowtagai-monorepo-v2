# Digital Freeway Coordination API

Pure software coordination layer for autonomous vehicles.

## Concept

"Waze-for-machines" - a single API that coordinates ALL autonomous vehicles.

- No CapEx, no hardware, no sensors

- 85-92% software margins

- Profitable in 12 months

## Quick Start

```bash

# Install dependencies

pip install -r requirements.txt

# Run locally

python main.py

# Or with uvicorn

uvicorn main:app --reload --port 8080

```

## API Endpoints

| Endpoint     | Method | Description                                           |
| ------------ | ------ | ----------------------------------------------------- |
| `/health`    | GET    | Health check                                          |
| `/telemetry` | POST   | Receive vehicle telemetry, return coordination vector |
| `/vehicles`  | GET    | List tracked vehicles                                 |
| `/metrics`   | GET    | Get coordination metrics                              |

## Telemetry Generator

Simulate 10K vehicles:

```bash
python utils/telemetry_generator.py --vehicles 1000 --url http://localhost:8080 --duration 60

```

## Architecture

```

Telemetry Stream (10K vehicles × 10Hz)
         │
         ▼
┌─────────────────────────────────────────┐
│     DIGITAL FREEWAY COORDINATION API    │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐      │
│  │ Ingest Agent│──│Optimize Agent│      │
│  │ (normalize) │  │ (Graph RL)  │      │
│  └─────────────┘  └─────────────┘      │
│         └────────┬───────┘              │
│                  ▼                      │
│         ┌─────────────┐                │
│         │Output Agent │                │
│         │(V2X vectors)│                │
│         └─────────────┘                │
└─────────────────────────────────────────┘
         │
         ▼
    OEM Fleet APIs (Tesla, GM, Waymo)

```

## Deploy to Cloud Run

```bash
gcloud run deploy digital-freeway-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

```

## License

Proprietary - ShadowTag-v2 Technologies
