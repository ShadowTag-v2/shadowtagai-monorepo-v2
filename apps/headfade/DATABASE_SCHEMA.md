# HeadFade Database Schema

This document outlines the Firestore database schema for the HeadFade Marketplace, including its core pillars: Forensic Detection, Creator Marketplace, and Publisher Embeds.

## Collections

### 1. `users`
Profiles for creators, publishers, and regular consumers.
- `uid` (String) - Firebase Auth UID
- `role` (String) - `CREATOR` | `PUBLISHER` | `USER` | `ADMIN`
- `displayName` (String)
- `email` (String)
- `stripeCustomerId` (String) - Reference to Stripe Connect / Customer
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

### 2. `videos`
The core media assets uploaded for forensic analysis or marketplace licensing.
- `id` (String) - Auto-generated
- `creatorId` (String) - Reference to `users.uid`
- `gcsUri` (String) - Cloud Storage location (e.g., `gs://headfade-cdn-origin/video.mp4`)
- `title` (String)
- `description` (String)
- `groundTruth` (String) - `AI` | `REAL` | `UNKNOWN` (Set by creator or admin)
- `status` (String) - `PROCESSING` | `ANALYZED` | `PUBLISHED` | `FLAGGED`
- `createdAt` (Timestamp)

### 3. `forensic_verdicts`
The Gemini AI analysis results for a given video.
- `id` (String) - Auto-generated
- `videoId` (String) - Reference to `videos.id`
- `model` (String) - e.g., `gemini-3.1-flash-lite`
- `geminiVerdict` (String) - The AI's final conclusion
- `geminiThoughts` (String) - Internal reasoning monologue
- `confidenceScore` (Number) - 0.0 to 1.0
- `latencyMs` (Number) - Time taken to analyze
- `analyzedAt` (Timestamp)

### 4. `human_telemetry`
Data collected from the "Global Turing Test" swiper interface (HDI - Human Deception Index).
- `id` (String) - Auto-generated
- `videoId` (String) - Reference to `videos.id`
- `userId` (String, Optional) - Null if anonymous
- `userVote` (String) - `AI` | `REAL`
- `actualTruth` (String) - `AI` | `REAL`
- `isCorrect` (Boolean) - Whether the human was fooled
- `latencyMs` (Number) - Time taken to vote
- `votedAt` (Timestamp)

### 5. `licenses`
Micro-licensing transactions in the Creator Marketplace.
- `id` (String) - Auto-generated
- `videoId` (String) - Reference to `videos.id`
- `buyerId` (String) - Reference to `users.uid` (Publisher)
- `sellerId` (String) - Reference to `users.uid` (Creator)
- `licenseType` (String) - `STANDARD` | `EXCLUSIVE` | `EMBED_ONLY`
- `priceAmount` (Number) - In cents
- `priceCurrency` (String) - e.g., `usd`
- `stripePaymentIntentId` (String)
- `purchasedAt` (Timestamp)

### 6. `embed_telemetry`
Analytics for the HeadFade player embedded on external publisher sites.
- `id` (String) - Auto-generated
- `videoId` (String) - Reference to `videos.id`
- `publisherId` (String) - Reference to `users.uid`
- `domain` (String) - Where it was embedded
- `views` (Number)
- `playDurationSec` (Number)
- `recordedAt` (Timestamp)

### 7. `remix_nodes`
Provenance tracking for the content remix tree.
- `id` (String) - Format: `rn_{videoId}`
- `videoId` (String) - Reference to `videos.id`
- `parentNodeId` (String, Optional) - Reference to parent `remix_nodes.id`
- `creatorId` (String) - Reference to `users.uid`
- `nodeType` (String) - `ORIGINAL` | `REMIX` | `DERIVATIVE` | `COMPILATION`
- `contentHash` (String) - SHA-256 hash for tamper detection
- `depth` (Number) - Depth in the remix tree (0 = original)
- `childCount` (Number) - Number of direct children
- `isOrphaned` (Boolean) - True if cryptographically shredded
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

### 8. `ingestion_jobs`
Pipeline state machine for content ingestion.
- `id` (String) - Format: `ingest_{videoId}`
- `videoId` (String) - Reference to `videos.id`
- `creatorId` (String) - Reference to `users.uid`
- `stage` (String) - `RECEIVED` | `UPLOADING_TO_GCS` | `JUDGE6_SCANNING` | `FORENSIC_ANALYSIS` | `REMIX_TREE_INSERTION` | `COMPLETE` | `BLOCKED` | `ERROR`
- `judge6Verdict` (Map, Optional) - Full Judge6 verdict object
- `remixNodeId` (String, Optional) - Created remix node ID
- `parentRemixNodeId` (String, Optional) - Parent node for remixes
- `error` (String, Optional) - Error message if stage is ERROR
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

## Judge6 Trust & Safety Gate
The Judge6 gate is **non-severable** — every piece of content must pass through it before entering the platform. It uses:
- **Google Cloud Video Intelligence API** — Explicit content detection across video frames
- **Google Cloud Vision API** — SafeSearch detection on thumbnails
- Verdicts: `PASS` (enter platform), `BLOCK` (quarantine), `REVIEW` (manual queue)
- Compliance: DSA Art. 16, CSAM Directive 2011/93/EU, COPPA, 18 U.S.C. § 2256

## Cryptographic Shredding
The `nuke_my_data()` endpoint performs GDPR/DSA-compliant data deletion:
1. Orphans all `remix_nodes` owned by the user (preserves graph structure)
2. Anonymizes `videos` (replaces creatorId, title, description)
3. Purges PII from `users` profile (email, displayName, stripeCustomerId)
4. Nullifies `userId` in `human_telemetry`

## Security Rules Constraints
- `users`: Read by self/admin. Write by self/admin.
- `videos`: Read by public if `status == PUBLISHED`. Write by `creatorId`.
- `forensic_verdicts`: Read by public. Write by secure backend only (Service Account).
- `human_telemetry`: Read by admin/creator. Write by public (append-only).
- `licenses`: Read by buyer/seller/admin. Write by secure backend only.
- `embed_telemetry`: Read by publisher/creator/admin. Write by public (append-only via API).
- `remix_nodes`: Read by public. Write by secure backend only.
- `ingestion_jobs`: Read by creator/admin. Write by secure backend only.
