# SHADOWTAG ARCHITECTURE (v1.0)
## "The Truth Layer" | Uncensored AI Search

### 1. The Wedge: "Uncensored & Searchable"
**Philosophy**: Fill the gap left by TikTok/YouTube censorship.
*   **Target**: Deepfakes, Satire, "Raw" AI outputs.
*   **Mechanic**: "AI Presumed" (Legal Shield) + "Shadow Search" (Prompt indexing).

### 2. The Core: 7-Cluster LLM Brain
We chain 7 heavy-hitter models to create the smartest, uncensored engine.
*   **Orchestrator**: LangChain (Edge-deployed).
*   **The Cluster**:
    1.  **GPT-5** (Reasoning)
    2.  **Grok** (Real-time/Unfiltered)
    3.  **Claude Opus** (Code/Architecture)
    4.  **Gemini 1.5 Pro** (Multimodal/Video Analysis)
    5.  **Quiddo/Sun** (Wildcards/Creative)
    6.  **Llama 3 (405B)** (Open weights fallback)
    7.  **Private Moderator LLM** (The "Judge" - Self-hosting on H100s)

### 3. The Infrastructure: "Edge Compute" (Cloudflare + CoreWeave)
*   **Strategy**: No central servers. Code runs at the edge.
*   **Layer 1 (Routing)**: **Cloudflare Workers**. 0ms cold start. Handles traffic globally.
*   **Layer 2 (Inference)**: **CoreWeave** (K8s on bare metal GPUs). Hosts the 7-LLM Cluster and Stable Diffusion/Sora endpoints.
*   **Layer 3 (China Mirror)**: **AliExpress/Alibaba Cloud**. Host `AIU.cn` for global regulatory arbitrage.

### 4. The Secret Weapon: "ShadowTag" (Steganography)
**Goal**: Track content provenance across the internet even if metadata is stripped.
*   **Technique A (Visual)**: 1x1 invisible pixel hash or LSB (Least Significant Bit) steganography in video frames.
*   **Technique B (Audio)**: Spread-spectrum audio watermarking (inaudible frequency embedding).
*   **Value**: We scrape TikTok/Instagram for these hashes. When we find them, we attribute the view to the Creator (and sell the data to brands).
*   **Blockchain**: Every hash is timestamped on Solana (low cost, high speed) for immutable proof of creation.

### 5. Implementation Roadmap
1.  **Refactor Main**: `main.py` -> `shadow_orchestrator.py`.
2.  **Edge Deploy**: Port logic to `worker.js` (Cloudflare).
3.  **Watermark Engine**: Build `watermark.py` using `wavmark` (audio) and `stegano` (image).
4.  **Cluster Connect**: Setup API gateways for the 7 LLMs.

---
**Status**: APPROVED by Board (IQ 160).
**Directives**: Ultrathink Mode. Simplify Ruthlessly.
