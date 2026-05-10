# 📜 Uphill Snowball: Provisional Patent Claims Strategy

The following represent the core defensible utility patents within the Uphill Snowball / Judge 6 architecture. Software patents must demonstrate a "technical solution to a technical problem" (not just an abstract business idea). We frame these around the specific cryptographic, routing, and memory-management techniques we use to achieve the legal insulation.

## 1. The Privilege Portal (Compute-to-Billable-Hour Ledger)
**The Concept:** The system maps non-deterministic AI compute (LLM inference) directly into protected attorney-client privilege silos, transforming raw agent tokens into billable legal hours.
**Patentable Method:**
*   A method for securely routing a sub-user's (client's) query through a master tenant's (attorney's) authenticated API gateway.
*   Cryptographically signing the generated LLM context window with the master tenant's enterprise key before execution.
*   Tracking the exact token consumption and inference duration of the sub-user's query.
*   Converting the token/duration metrics via a deterministic algorithm into a standardized "attorney review time" equivalent, and actively appending it to a secure, immutable billing ledger.
*   Wrapping the entire sub-user session within the master tenant's attorney work-product doctrine umbrella by cryptographically binding the session metadata to the attorney's matter ID, ensuring the research is shielded from discovery (mitigating the recent case law where unshielded client AI research was found discoverable).
*   *Why it's patentable*: It is a specific technical implementation of cryptographic routing, work-product doctrine enforcement, and compute-time transformation to enforce a legal access control layer.

## 2. The Objective Options AST Intercept (S7263 Bypass)
**The Concept:** Preventing the "unauthorized practice of law/medicine" by actively blocking an AI from making singular conclusions, forcing it to provide 3 objective paths instead.
**Patentable Method:**
*   A method for intercepting the Abstract Syntax Tree (AST) or generated token stream of an LLM prior to rendering to the user interface.
*   Executing a real-time semantic analysis (via a secondary lightweight model like Gemini Flash) to detect "assurative" or "conclusive" language matching predefined restricted vectors (e.g., medical diagnosis, legal advice).
*   Upon detection of a violation, automatically halting the output stream and executing a deterministic "Active Rewrite" protocol.
*   The protocol algorithmically restructures the response into exactly three non-assurative alternative pathways, forcing the inclusion of citation hyperlinks to verified data stores for each pathway.
*   *Why it's patentable*: It’s a dynamic, multi-model execution flow that monitors and mutates active inference streams to enforce safety bounds.

## 3. Cryptographic Memory Bead Shredding (Article 17 GDPR Native)
**The Concept:** Solving the massive technical problem of proving a cloud provider has "deleted" user data by moving the destruction mechanism to local client-side encryption.
**Patentable Method:**
*   A method for chunking active LLM session context into isolated "Memory Beads."
*   Encrypting each bead payload on the edge device (client-side) using an ephemeral, locally generated cryptographic key.
*   Transmitting the encrypted bead to the central cloud for long-term storage, while retaining the single decryption key strictly within the edge device's secure enclave (e.g., Apple Secure Enclave / local file system).
*   Enabling "Right to Erasure" by permanently destroying the local decryption key, mathematically rendering all cloud-stored beads irrevocably shattered and inaccessible, thereby satisfying data deletion regulations without requiring a cloud-side database operation.
*   *Why it's patentable*: It's a novel cryptographic architecture for decentralized data lifecycle management and compliance.

## 4. The "Bar Exam" Contextual Injection Constraint
**The Concept:** Forcing agents to define their own legal/safety boundaries based on the user's prompt *before* they are allowed to attempt solving it.
**Patentable Method:**
*   A dual-prompting execution method where a user query is first passed to a "Supervisor Node."
*   The Supervisor Node generates a strict set of domain-specific constraints (The "Call of the Question") based solely on the latent risks in the user's prompt.
*   Automatically modifying the core system prompt of the "Solver Node" by appending the dynamically generated constraints as absolute guardrails.
*   Executing the Solver Node only after the constraints have been cryptographically bound to the request hash.
*   *Why it's patentable*: A multi-agent orchestration technique that dynamically alters system prompts mid-flight based on real-time threat modeling.

## 5. The "Whiteboard" Shared Swarm State Lock
**The Concept:** Preventing multi-agent AI swarms from entering infinite hallucination loops when they disagree on complex research.
**Patentable Method:**
*   A method for establishing a centralized, immutable KV-cache or key-value store (the "Whiteboard") accessible by multiple autonomous agent nodes.
*   Forcing all agents in the swarm to read from and write to the Whiteboard utilizing a strict temporal locking mechanism (e.g., optimistic concurrency control).
*   Requiring that any conflicting data between agents be resolved by a designated Judge Node utilizing a deterministic algorithm against the Whiteboard's state.
*   Halting the swarm if consensus on the Whiteboard state is not reached by a mathematically defined deadline parameter.
*   *Why it's patentable*: Distributed systems concurrency control applied specifically to non-deterministic LLM swarm outputs.

## 6. Content-Aware Adaptive DCT Video Watermarking with Sparse Attention
**The Concept:** Embedding invisible, compression-resilient digital watermarks into video content using a Vision Language Model (VLM) to adaptively select optimal embedding locations.
**Patentable Method:**
*   A method for analyzing video frame content using a VLM (e.g., Gemini Vision) to generate a per-frame texture map, motion vector field, and brightness map.
*   Using the VLM analysis to adaptively select robust DCT coefficient blocks (mid-frequency positions, e.g., [3,4]) and dynamically adjust the QIM embedding strength (δ) per-block based on local texture density and temporal stability.
*   Applying Dual Sparse Attention (DSA) to select only 15-25% of blocks for embedding, reducing computational cost by 50% while maintaining 98%+ detection rates.
*   Enforcing temporal coherence across 3-7 frame windows to eliminate visible flicker artifacts (achieving <5% flicker rate vs. 12-18% baseline).
*   *Why it's patentable*: A novel combination of VLM-guided content analysis with adaptive frequency-domain watermarking and sparse attention — no prior art combines all three.

## 7. Cryptographic Agent Swarm Termination via KMS Key Revocation (RKILL)
**The Concept:** An emergency kill switch for a multi-agent AI swarm that uses Cloud Key Management to instantly render all cached context, world model state, and vector memory cryptographically unreadable.
**Patentable Method:**
*   A method for encrypting all active agent session data (KV-cache, Firestore world model state, vector embeddings, Memorystore cache) using tenant-specific Cloud KMS CryptoKeyVersions.
*   Upon detection of a prompt injection attack, rogue agent behavior, or an authorized kill command, programmatically disabling the tenant's CryptoKeyVersion via the KMS API.
*   The key disabling operation instantly renders all encrypted cached data, world model state, and vector memory mathematically unreadable across all active agent nodes simultaneously.
*   Purging all Memorystore prefixes for the tenant and logging the termination event to a separate, immutable audit BigQuery table with SHA-256 receipts.
*   Target execution: <15 seconds from trigger to full cryptographic sterilization.
*   *Why it's patentable*: A novel application of cloud key management infrastructure as a real-time AI safety control mechanism for multi-agent systems.
