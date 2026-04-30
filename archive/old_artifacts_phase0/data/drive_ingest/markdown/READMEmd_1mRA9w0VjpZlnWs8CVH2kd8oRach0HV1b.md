# Tokable Gesture Streaming Platform

**"Machines will never dance"**

Silent gesture-based streaming platform with real-time AI interpretation, NFT minting, and creator economy.

---

## 🎯 Mission

Transform gesture-based performance into a scalable creator economy by:
- Removing audio dependency from streaming
- Real-time AI interpretation of movement → art
- NFT monetization of performances
- Two-sided marketplace (creators ↔ fans)

**Fundraising Target**: $2.5M seed round
**Growth Goal**: 500k MAU, $2M+ ARR
**18-month runway**: 50% eng, 30% creator acquisition, 20% marketing

---

## 🚀 Core Value Proposition

### For Creators
- **Silent streaming** - Express without words
- **AI art generation** - Real-time interpretation of gestures
- **Revenue streams**: Tips, NFT sales, subscriptions, tournaments
- **Global accessibility** - No language barriers
- **Low barrier to entry** - Just a camera, no special equipment

### For Fans
- **Unique viewing experience** - Split-screen (creator + AI art)
- **Interactive engagement** - Tips, reactions, caption clips
- **NFT ownership** - Own moments from favorite creators
- **Community building** - Tournaments, leaderboards, Discord

### vs. TikTok Live
| Feature | TikTok Live | Tokable |
|---------|------------|---------|
| Audio | Required | **Disabled by design** |
| Content Focus | Talking/trends | **Movement/gesture** |
| AI Integration | Filters only | **Real-time art generation** |
| Monetization | Tips only | Tips + NFTs + subscriptions |
| Creator differentiation | Low | **High (unique AI art style)** |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Tokable Platform (GKE)                      │
│                                                             │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Creator     │  │      AI      │  │   Fan Viewing   │ │
│  │   Streaming   │─→│ Interpreter  │─→│    Service      │ │
│  │  (WebSocket)  │  │   (Gemini)   │  │  (WebSocket)    │ │
│  └───────────────┘  └──────────────┘  └─────────────────┘ │
│         │                    │                    │         │
│         ├────────────────────┼────────────────────┘         │
│         │                    │                              │
│  ┌──────▼────────┐  ┌────────▼────────┐  ┌──────────────┐ │
│  │   Gesture     │  │   Emotion       │  │   Art        │ │
│  │  Detection    │  │  Recognition    │  │  Generator   │ │
│  │ (MediaPipe)   │  │  (Vertex AI)    │  │ (Gemini 2.0) │ │
│  └───────────────┘  └─────────────────┘  └──────────────┘ │
│         │                    │                    │         │
│         └────────────────────┼────────────────────┘         │
│                              │                              │
│  ┌───────────────────────────▼──────────────────────────┐  │
│  │              NFT Minting Layer                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │  Media   │─→│   IPFS   │─→│   Blockchain     │   │  │
│  │  │ Compiler │  │  Upload  │  │ (Polygon/ETH)    │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼──────────────────────────┐  │
│  │           Revenue Distribution Engine                │  │
│  │  Tips • NFT Sales • Subscriptions • Tournaments      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Core Features

### 1. Silent Gesture Streaming
- **No audio channel** - Forces creative expression through movement
- **Split-screen display**: Left = creator camera, Right = AI-generated art
- **Real-time interpretation**: Gestures → text captions + abstract art
- **Emotional inference**: Happiness, playfulness, excitement, confusion
- **Frame rate**: 30 FPS with <100ms AI processing latency

### 2. AI Interpretation Layer
- **Gesture detection**: MediaPipe Holistic (468 face + 33 pose + 21 hand landmarks)
- **Emotion recognition**: Vertex AI multi-modal (facial + body language)
- **Art generation**: Gemini 2.0 Pro creates abstract art inspired by movement
- **Text interpretation**: Natural language descriptions of gestures + emotions
- **Style evolution**: AI art evolves throughout stream (cumulative canvas)

### 3. NFT Marketplace
- **Auto-minting**: End stream → compile video → mint NFT → list for sale
- **Blockchain**: Polygon (default, low gas), Ethereum (premium)
- **IPFS storage**: Decentralized media hosting
- **Metadata**: Emotion summary, gesture catalog, stream duration, viewer stats
- **Royalties**: 10% to creator on secondary sales
- **Gas costs**: ~$0.01-0.10 on Polygon

### 4. Revenue Streams

| Revenue Type | Platform Fee | Creator Payout | Notes |
|--------------|--------------|----------------|-------|
| **Tips** | 20% (15% if Pro) | 80% (85%) | Real-time during stream |
| **NFT Primary Sale** | 20% | 80% | Creator sets price |
| **NFT Secondary Sale** | 5% platform + 10% creator royalty | 85% seller | Automatic distribution |
| **Subscriptions** | N/A | $9.99/mo | Tokable Pro membership |
| **Tournament Prizes** | 0% | 100% | Platform sponsors prize pool |
| **Brand Sponsorships** | 30% | 70% | Creator-brand partnerships |

**Target Creator ARR**: $1,200-5,000/year (active creators)

### 5. Streaming Modes

#### Private Mode
- Practice only
- No viewers
- No recording
- Free

#### Charades Mode
- Invite-only game mode
- Friends guess gestures
- Light revenue (tips)
- Great for viral clips

#### Public Mode
- Full fan access
- AI art generation
- Tips + reactions
- NFT minting available

#### Tournament Mode
- Competition mode
- Leaderboard scoring
- Prize pools ($100-1,000+)
- Judged by AI + community votes

### 6. Fan Experience
- **Watch split-screen**: Creator + AI art side-by-side
- **Real-time captions**: AI-generated interpretation text
- **Interactive reactions**: Emojis, likes, fire
- **Tipping**: $1-1,000 with custom messages
- **Clip creation**: Capture 5-60 second highlights
- **NFT ownership**: Purchase stream NFTs

### 7. Creator Tools
- **Analytics dashboard**: Revenue, viewer trends, emotion insights
- **Highlight generator**: AI finds peak moments
- **Subtitle scripts**: Pre-load text for post-production (optional)
- **Tournament registration**: Compete for prizes
- **Leaderboard ranking**: Algorithm based on engagement + revenue + consistency

---

## 🛠️ Technical Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **API Server**: Uvicorn with WebSocket support
- **Database**: PostgreSQL (user data, streams, revenue)
- **Cache**: Redis (leaderboards, real-time stats)
- **Storage**: Google Cloud Storage (video frames, thumbnails)

### AI/ML
- **Gesture Detection**: MediaPipe Holistic
- **Emotion Recognition**: Vertex AI custom models
- **Art Generation**: Gemini 2.0 Pro with vision
- **Text Generation**: Gemini 2.0 Pro

### Blockchain
- **Smart Contracts**: Solidity (ERC-721 NFTs)
- **Networks**: Polygon (primary), Ethereum (premium)
- **Web3**: web3.py
- **Storage**: IPFS (Infura/Pinata)

### Infrastructure
- **Cloud Provider**: Google Cloud Platform (exclusive)
- **Container Orchestration**: GKE (Google Kubernetes Engine)
- **CI/CD**: Cloud Build
- **Monitoring**: Prometheus + Grafana
- **Logging**: Cloud Logging
- **GPU Acceleration**: NVIDIA T4 GPUs for AI inference

### Frontend (not included in this codebase)
- **Web**: React/Next.js
- **Mobile**: React Native
- **WebRTC**: For low-latency video streaming

---

## 📊 Go-To-Market Plan (First 6-9 Months)

### Phase 1: Core Build (Months 0-2)
- ✅ Finalize core tech: gesture-to-text + avatar playback
- ✅ MVP private mode + basic charades mode
- ✅ Stream module with fan-facing experience
- ✅ Add real-time emotional inference

**Engineering Priorities**:
- API endpoints (streaming, NFT, revenue)
- AI interpreter pipeline (<100ms latency)
- WebSocket infrastructure
- Basic UI (web app)

### Phase 2: Alpha Launch + Creator Pilot (Months 2-4)
- Recruit 10-20 micro-influencers to run "Tokable Tournaments"
- Incentivize early creator streams with rev share or grants
- Run closed tests with elder care partners or intergenerational testers
- Begin building Discord/Reddit community

**Success Metrics**:
- 20+ active creators
- 100+ streams completed
- 500+ registered users
- $500+ in early revenue

### Phase 3: Beta Rollout & Fan-Facing Features (Months 4-6)
- Launch public Tokable Streams (streamer discoverability, tipping)
- Launch "Fan Mode" (watch + react + caption clips)
- Begin weekly highlight recaps
- Introduce first wave of brand sponsorships

**Success Metrics**:
- 200+ active creators
- 5,000+ MAU
- 100+ NFTs minted
- $10k+ monthly revenue

### Phase 4: Scale Acquisition (Months 6-9)
- TikTok & YouTube Shorts "charades challenge" campaign
- Partner with community colleges + senior centers (free Tokable Pro trials)
- Launch creator leaderboard + fan loyalty programs
- Begin API pilot outreach to edtech / remote-work partners

**Success Metrics**:
- 1,000+ active creators
- 50,000+ MAU
- $50k+ monthly revenue
- Series A positioning ($10M+)

---

## 💰 Unit Economics (Per Active Creator)

### Assumptions
- Average stream: 20 minutes, 2x/week
- Average viewers: 50-100
- Tip rate: 5% of viewers tip $5 average
- NFT minting rate: 50% of streams
- NFT sale rate: 20% of minted NFTs
- NFT average price: $25

### Monthly Revenue (Per Creator)
```
Tips:        8 streams × 75 viewers × 5% × $5 =  $150
NFT Sales:   4 NFTs × 20% sold × $25 =           $20
Subscription: (if Pro) =                         $0-10
─────────────────────────────────────────────────────
Total Creator Revenue:                           $170-180/mo
Platform Revenue (20%):                          $34-36/mo
```

### Platform Economics (at 500k MAU, 10k Active Creators)
```
Creators:        10,000 × $34/mo =    $340k/mo revenue
Fans (Pro):      5,000 × $10/mo =     $50k/mo revenue
Brand Sponsors:  50 × $2,000/mo =     $100k/mo revenue
─────────────────────────────────────────────────────
Total Monthly Revenue:                $490k/mo
Annual Run Rate (ARR):                $5.9M
```

**Target ARR**: $2M+ by Month 18 → $5M+ by Month 24

---

## 🚢 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- GCP account with credits
- PostgreSQL
- Redis

### Local Development

1. **Clone repository**:
   ```bash
   git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
   cd ShadowTag-v2-fastapi-services
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Start Tokable API**:
   ```bash
   uvicorn src.api.tokable:app --reload --host 0.0.0.0 --port 8001
   ```

5. **Access API**:
   - Swagger UI: http://localhost:8001/tokable/docs
   - ReDoc: http://localhost:8001/tokable/redoc

### GKE Deployment

1. **Build Docker images**:
   ```bash
   docker build -t gcr.io/PROJECT_ID/tokable-api:latest .
   docker push gcr.io/PROJECT_ID/tokable-api:latest
   ```

2. **Deploy to GKE**:
   ```bash
   kubectl apply -f k8s/tokable-deployment.yaml
   ```

3. **Verify deployment**:
   ```bash
   kubectl get pods -n tokable
   kubectl get services -n tokable
   ```

---

## 📖 API Endpoints

### Streaming

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/streams/create` | Create new streaming session |
| `POST` | `/streams/start` | Start live streaming |
| `POST` | `/streams/end` | End stream & optionally mint NFT |
| `GET` | `/streams/{stream_id}` | Get stream details |
| `GET` | `/streams/live` | Browse live streams |
| `WS` | `/ws/stream/{stream_id}/creator` | WebSocket for creator |
| `WS` | `/ws/stream/{stream_id}/fan` | WebSocket for fans |

### NFT Marketplace

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/nfts` | Browse NFT marketplace |
| `POST` | `/nfts/{nft_id}/list` | List NFT for sale |
| `POST` | `/nfts/{nft_id}/buy` | Purchase NFT |

### Revenue

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tips/send` | Send tip to creator |
| `GET` | `/revenue/creator/{creator_id}` | Creator revenue dashboard |

### Tournaments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tournaments` | Get active tournaments |
| `POST` | `/tournaments/{tournament_id}/register` | Register for tournament |
| `GET` | `/leaderboard` | Creator leaderboard |

### Platform

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/metrics` | Platform-wide metrics (MAU, ARR, etc.) |
| `GET` | `/users/{user_id}` | User profile |
| `POST` | `/users/{user_id}/subscribe` | Subscribe to Tokable Pro |

---

## 📈 Success Metrics (Investor Dashboard)

### North Star Metrics
1. **MAU Growth**: Track to 500k target
2. **ARR Growth**: Track to $2M+ target
3. **Creator Retention**: 60%+ monthly retention
4. **Fan Engagement**: 40%+ viewers tip or purchase NFTs

### Operational Metrics
- **Streams per day**: Target 500+ by Month 9
- **NFT mint rate**: 50%+ of streams
- **NFT sell-through**: 20%+ within 30 days
- **Average tip per stream**: $15-30
- **Creator revenue (median)**: $150-300/month
- **Platform revenue per creator**: $30-60/month

### Technical Metrics
- **AI processing latency**: <100ms (p95)
- **WebSocket uptime**: >99.5%
- **NFT minting success**: >98%
- **Platform uptime**: >99.9%

---

## 🔐 Security & Compliance

- **Data Privacy**: GDPR compliant, PII encryption
- **Payment Security**: PCI-DSS compliant (Stripe)
- **Blockchain Security**: Multi-sig wallets, audit reports
- **Content Moderation**: AI-based NSFW detection
- **DMCA**: Takedown process for copyright violations

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 📞 Contact

- **Website**: https://tokable.ai
- **Email**: founders@tokable.ai
- **Twitter**: @TokableAI
- **Discord**: https://discord.gg/tokable

---

## 🙏 Acknowledgments

Part of **PNKLN Core Stack™**
Powered by Gemini 2.0 Pro, Vertex AI, MediaPipe
Built with FastAPI, GKE, and Claude Agent SDK

---

**Status**: ✅ MVP Ready (v2.0.0)
**Last Updated**: 2025-11-17

**"Machines will never dance"** 💃
