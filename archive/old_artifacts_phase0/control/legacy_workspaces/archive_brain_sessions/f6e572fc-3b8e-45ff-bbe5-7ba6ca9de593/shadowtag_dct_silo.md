# ShadowTag DCT Implementation Silo

```
///▞ SWARM: ShadowTag DCT Silo | RISK: L | BRAKES: 1 → A 92%
```

**STATUS**: SILOED — This code is preserved as canonical reference.
**NOT IN**: Cor.56 or Kosmos/BioAgents architecture.
**SOURCE**: Past conversations (Nov 2025), extracted verbatim.
**REASON**: ShadowTag DCT watermarking is a separate product vertical from the Kosmos/BioAgents governance engine. Mixing them creates architectural coupling that violates the modular/portable core principle.

---

## 1. SHADOWTAG PROCESSOR — Full Implementation

Source: Chat `2f91c35e` (Nov 5, 2025)

```python
# shadowtag_core.py - DCT watermarking with GPU acceleration
import torch
import numpy as np
from scipy.fftpack import dct, idct
import ffmpeg
from vllm import LLM, SamplingParams

class ShadowTagProcessor:
    def __init__(self):
        # Load Qwen2-VL for content analysis
        self.vlm = LLM(
            model="Qwen/Qwen2-VL-72B-Instruct",
            tensor_parallel_size=2,
            gpu_memory_utilization=0.95
        )
        self.watermark_key = torch.randn(64, device='cuda')  # Secret key

    def embed_watermark(self, video_path: str, metadata: dict) -> str:
        """Embed DCT watermark into video."""
        # 1. Extract frames with GPU acceleration
        frames = self._extract_frames_gpu(video_path)

        # 2. Generate content-aware watermark using VLM
        content_signature = self._analyze_content(frames[0])
        watermark_bits = self._generate_watermark(metadata, content_signature)

        # 3. Embed in DCT coefficients (frequency domain)
        watermarked_frames = []
        for frame in frames:
            # Convert to YCbCr (watermark in luminance)
            ycbcr = self._rgb_to_ycbcr(frame)
            y_channel = ycbcr[:,:,0]

            # DCT transform (8x8 blocks)
            dct_blocks = self._apply_dct_8x8(y_channel)

            # Embed watermark in mid-frequency coefficients (robust to compression)
            watermarked_dct = self._embed_in_dct(dct_blocks, watermark_bits)

            # Inverse DCT
            watermarked_y = self._apply_idct_8x8(watermarked_dct)
            ycbcr[:,:,0] = watermarked_y

            watermarked_frames.append(self._ycbcr_to_rgb(ycbcr))

        # 4. Reconstruct video with FFmpeg GPU encoding
        output_path = self._reconstruct_video_gpu(
            watermarked_frames, video_path
        )
        return output_path
```

---

## 2. QIM EMBEDDING — δ=10 Mid-Frequency Coefficient Modification

Source: Chat `b2736b91` (Nov 6, 2025) — Investor demo code

```python
def embed_shadowtag(video_path, watermark_payload):
    """
    Embeds watermark into DCT coefficients of video frames.
    Invisible, unremovable, survives compression.

    QIM (Quantization Index Modulation):
      delta = 10 (embedding strength)
      Position [3,4] in 8x8 DCT block (mid-frequency)
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output_watermarked.mp4', fourcc, fps, (width, height))

    # Convert watermark to binary array
    watermark_bits = ''.join(format(ord(c), '08b') for c in watermark_payload)
    bit_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to YCrCb (work in luminance channel)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y_channel = ycrcb[:,:,0].astype(np.float32)

        # Apply 8x8 block DCT
        h, w = y_channel.shape
        for i in range(0, h-8, 8):
            for j in range(0, w-8, 8):
                block = y_channel[i:i+8, j:j+8]
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')

                # QIM embedding: position [3,4], delta=10
                if bit_index < len(watermark_bits):
                    bit = int(watermark_bits[bit_index])
                    alpha = 10  # δ = embedding strength
                    dct_block[3,4] = (dct_block[3,4] // alpha) * alpha + (alpha * bit)
                    bit_index += 1

                # Inverse DCT
                idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                y_channel[i:i+8, j:j+8] = idct_block

        # Reconstruct frame
        ycrcb[:,:,0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        watermarked_frame = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        out.write(watermarked_frame)

    cap.release()
    out.release()
    return 'output_watermarked.mp4'
```

---

## 3. DSA SPARSE ATTENTION — 4K/8K Video Processing

Source: Chat `3d16191a` (Nov 4, 2025) — Technical analysis

```python
def sparse_dct_watermark_embed(video_frames, watermark_bits):
    """
    DSA-enhanced ShadowTag embedding for 4K/8K video.

    Stage 1: Lightning Indexer identifies robust DCT blocks
    Stage 2: Fine-grained token selection within blocks
    Stage 3: QIM embedding with adaptive strength
    """
    # Stage 1: Lightning Indexer — select 15-25% of blocks
    robust_blocks = lightning_indexer(
        video_frames,
        criteria=['low_temporal_variance', 'mid_frequency_energy']
    )

    # Stage 2: Fine-grained selector — 40-60% sparsity within blocks
    embedding_coefficients = fine_grained_selector(
        robust_blocks,
        target_coefficients=[15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        watermark_bits=watermark_bits
    )

    # Stage 3: QIM with adaptive delta (8-12 vs fixed 10)
    watermarked_frames = qim_embed(
        frames=video_frames,
        coefficients=embedding_coefficients,
        delta=adaptive_delta(compression_likelihood)
    )

    return watermarked_frames
```

---

## 4. FLICKER REDUCTION — Temporal Coherence

Source: Chat `3d16191a` (Nov 4, 2025)

```yaml
FLICKER REDUCTION PERFORMANCE:
═══════════════════════════════════════════════════════

BASELINE (Frame-Independent):
├─ Each frame processed separately
├─ No inter-frame dependency modeling
├─ Visible flicker: ~12-18% of watermarked videos
└─ User complaints: Moderate

WITH SPARSE ATTENTION (Temporal Modeling):
├─ DSA spans multiple frames (3-7 frame windows)
├─ Attention links temporally-stable DCT coefficients
├─ Embedding strength varies smoothly across frames
├─ Visible flicker: ~2-5% of videos
└─ User complaints: Negligible

PERFORMANCE GAIN: +60-85% flicker reduction
UX IMPROVEMENT: Imperceptible watermarks in 95-98% of cases
```

---

## 5. QWEN2-VL CONTENT ANALYSIS PIPELINE

Source: Chat `2f91c35e` (Nov 5, 2025)

```python
# Content-aware watermark generation using VLM
class ContentAnalyzer:
    """
    Qwen2-VL analyzes video content to generate content-aware
    watermark placement strategy.

    Why content-aware:
    - Textured regions hide watermarks better than flat regions
    - Action sequences need temporal coherence
    - Dark/light regions need different delta values
    """

    def __init__(self):
        self.vlm = LLM(
            model="Qwen/Qwen2-VL-72B-Instruct",
            tensor_parallel_size=2,
            gpu_memory_utilization=0.95
        )

    def analyze_frame(self, frame: np.ndarray) -> dict:
        """Analyze frame content for optimal watermark placement."""
        # Returns: texture_map, motion_vectors, brightness_map
        # Used to adapt QIM delta per-block
        pass

    def generate_placement_strategy(self, frames: list) -> dict:
        """Generate watermark placement strategy for video."""
        # Content-aware block selection
        # Adaptive delta per region
        # Temporal coherence windows
        pass
```

---

## 6. DOCKER/DEPLOYMENT (GPU-Accelerated)

Source: Chat `2f91c35e` (Nov 5, 2025)

```dockerfile
# shadowtag.Dockerfile
FROM nvcr.io/nvidia/pytorch:24.11-py3

# vLLM for Qwen2-VL inference
RUN pip install vllm==0.6.3 \
    transformers==4.46.0 \
    accelerate==0.34.2

# FFmpeg with NVIDIA codec support
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nvidia-codec-headers \
    && rm -rf /var/lib/apt/lists/*

COPY shadowtag_core.py /app/
COPY dct_embedding.py /app/

WORKDIR /app

CMD ["python", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "Qwen/Qwen2-VL-72B-Instruct", \
     "--tensor-parallel-size", "2", \
     "--gpu-memory-utilization", "0.95", \
     "--max-num-seqs", "256"]
```

**Deployment note**: ShadowTag requires GPU (L4 minimum, H100 recommended).
Region: `us-central1` (Cloud Run with GPU) or dedicated GCE.
This is the ONE exception to the "Cloud Run us-west1 no-GPU" rule.

---

## 7. STRATEGIC POSITIONING

Source: Chat `2309e2d2` (Nov 5, 2025)

```
RECOMMENDED: Option B — C2PA Wrapper + DCT Core

┌─────────────────────────────────────────┐
│ C2PA Manifest (ISO Standard)            │
│ ├─ Hardware attestation                 │
│ ├─ Provenance chain                     │
│ └─ ShadowTag DCT watermark as payload   │ ← YOUR MOAT
└─────────────────────────────────────────┘

WHY:
- Platform compatible (YouTube/Meta gates)
- Standards compliant (enterprise procurement)
- Differentiation: DCT = forensic-grade
- Dual protection: C2PA custody + DCT post-edit detection
```

---

## 8. TECHNICAL SPECIFICATIONS SUMMARY

| Parameter | Value | Source |
|-----------|-------|--------|
| DCT block size | 8×8 | JPEG standard |
| QIM delta (δ) | 10 (adaptive: 8-12) | Embedding strength |
| Coefficient position | [3,4] mid-frequency | Compression resilience |
| Color space | YCbCr luminance only | Perceptual invisibility |
| Detection rate | 98%+ at JPEG Q=50 | Tree-Ring validation |
| VMAF impact | <5% (>95 VMAF) | Quality threshold |
| Flicker rate (w/ DSA) | 2-5% | Temporal coherence |
| 4K processing | DSA sparse attention | 50% cost reduction |
| Content analysis | Qwen2-VL-72B-Instruct | VLM for placement strategy |
| GPU requirement | L4 minimum, H100 recommended | Inference + DCT |
| Semantic compression | 487 bytes vs 50KB | Governance decisions |

---

## 9. SILO BOUNDARY

```
SILOED FROM:
├─ Cor.56 (definitive source — ShadowTag referenced but NOT implemented there)
├─ Kosmos/BioAgents Runtime (governance engine — no watermarking code)
├─ Judge #6 (enforcement — may CALL ShadowTag API but doesn't contain it)
└─ JR Engine (decision framework — evaluates ShadowTag ROI, doesn't implement)

INTERFACES WITH (via API only):
├─ POST /shadowtag/embed  → Embed watermark in video
├─ POST /shadowtag/detect → Detect/extract watermark from video
├─ GET  /shadowtag/verify → Verify watermark integrity
└─ POST /shadowtag/batch  → Batch processing for enterprise

DEPLOYMENT: Separate Cloud Run service (us-central1, GPU)
REPO: Separate repository from Kosmos/BioAgents
PORT: 8700 (ShadowTag canonical port)
```

This silo ensures ShadowTag DCT implementation can evolve independently of the governance stack, be licensed separately, and be deployed to GPU infrastructure without pulling the CPU-only BioAgents services into expensive GPU regions.
