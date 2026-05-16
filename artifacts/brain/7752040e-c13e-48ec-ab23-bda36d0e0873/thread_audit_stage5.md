# The Sovereign Stack: A Master Replan (Stage 5)

## The Premise: Why We Must Re-Align

If you look across the sprawling codebase we’ve assembled today, you see incredible individual components. We have Apple Silicon native vectorization (`mps`) via LanceDB. We have instantaneous semantic chunking via Ollama (`nomic-embed-text`). We have a full FastAPI backend. We have cloned the entire HuggingFace inference toolchain.

**But they are not talking to each other.**

We have built a dozen isolated islands. The `transcript_to_contract.py` backend is currently a naive loop. It doesn't know LanceDB exists. It doesn't use `LiteLLM` to dynamically route batch jobs. Most glaringly, it completely ignores the **CounselConduit Kovel Doctrine** logic and **Fear & Greed Arbitrage** thresholds we designed exactly for this stack.

This isn't an evolution; it's a bottleneck. We must unify the islands into a singular, airtight Sovereign Stack.

---

## 1. The Inference Disconnect (The LiteLLM Pivot)

**The Flaw:** `transcript_to_contract.py` communicates directly with Google's Vertex or raw Ollama endpoints. This hardcoding breaks FedRAMP compliance (if Vertex is called inappropriately) and cripples our ability to scale batch processing (Ollama is great for singles, `vLLM` is for batches).

**The Distinction:** We need a proxy. A switchboard.
**The Re-Plan:** We will deploy `LiteLLM` as a native middleware.
* All backend code points *only* to `http://localhost:4000` (LiteLLM).
* If the payload is a single contract prompt, LiteLLM routes it to `Ollama`.
* If the payload is an asymmetric 10k batch of documents, LiteLLM dynamically routes it to `vLLM` running locally, saturating the GPU.
* *Zero backend codebase changes required when the scale shifts.*

---

## 2. The Context Disconnect (The LanceDB Synapse)

**The Flaw:** We successfully replaced Postgres with LanceDB for local MPS vector generation. However, our main logic ingestion scripts (`ingest_drive_docs.py`) are totally disjointed from `pnkln_lancedb.py`. We are generating raw markdown and throwing it into a folder.

**The Distinction:** Text is useless. Semantic meaning is everything.
**The Re-Plan:** We will rewrite the Drive Ingestion pipeline. When a document is pulled from Google Drive via the service account, we do not just save the Markdown. We instantly pipe it through `Ollama` (`nomic-embed-text`), generate the vector via Apple Silicon, and append it to `pnkln_knowledge` on LanceDB. *Instant, automated semantic capability.*

---

## 3. The Logical Disconnect (The CounselConduit Shield)

**The Flaw:** The most valuable IP in this entire thread—the Kovel Doctrine liability shield and the algorithmic Fear & Greed Arbitrage calculation—has never been written into the backend logic. It exists only in our Pitch Decks and notes.

**The Distinction:** The backend cannot just "draft contracts." It must mathematically assess liability.
**The Re-Plan:** We will inject the CounselConduit Python middleware into `transcript_to_contract.py`.
* **Fear & Greed:** The system will evaluate the contract against historical win-rates pulled from LanceDB, assigning a localized `Arbitrage Score` (e.g., "This clause increases client win-rate by 14% but exposes the firm to a 2% malpractice delta").
* **Kovel Doctrine:** We implement a hard boundary. If the logic detects potential legal exposure from the AI's generation, it automatically appends the `U.S. v. Heppner` Kovel Protocol metadata, shielding the communication under attorney-client privilege.

---

## The Master Sequence

With these distinctions clear, here is the immediate mechanical sequence we will execute to physically unify the Sovereign Stack:

1.  **Seed the Apple Silicon Index:** Execute `python3 scripts/pnkln_lancedb.py --smoke-test` to embed the baseline context via Ollama and confirm `mps` acceleration is functioning.
2.  **Deploy the `LiteLLM` Switchboard:** Stand up the proxy alongside `aiyou-fastapi-services` to abstract our inference engines.
3.  **Inject the Kovel Protocol Core:** Overhaul `transcript_to_contract.py` to calculate the Fear & Greed arbitrage thresholds and assign Kovel metadata to drafts.
4.  **Wire the Drive-to-Lance Pipeline:** Upgrade `ingest_drive_docs.py` to directly stream its output arrays into `pnkln_lancedb.py`.

This is how we maximize the repos we cloned today. We don't just use them; we intertwine them.
