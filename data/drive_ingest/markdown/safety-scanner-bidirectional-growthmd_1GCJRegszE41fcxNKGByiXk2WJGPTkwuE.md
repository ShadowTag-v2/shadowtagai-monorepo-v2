# Safety Scanner Integration - Governance Lexicon Enforcement

## Grade: B+ → A+ Roadmap

**Current State**: Solid foundation with OPORD system, Elasticsearch architecture, and scholarly PDF indexing.

**Missing Critical Components**:
1. **Safety Scanner** - Governance lexicon scanning for PII, security violations, compliance
2. **Bidirectional Corpus Growth** - Agent outputs indexed → future agents search both PDFs + agent knowledge

---

## 1. Safety Scanner Architecture

### Purpose
Scan all indexed content (OPORDs, PDFs, agent outputs) for governance violations using multilingual lexicons.

**Inspired by Apertus Paper** (Section 5.2 - Safety & Harmful Content Analysis):
- Weaponized Words lexicon (slurs, toxic terms)
- LDNOOBW ("List of Dirty, Naughty, Obscene, Bad Words") - 28 languages
- Chemical weapons terms (Ledgard's Laboratory History)
- PII patterns (SSNs, credit cards, emails, addresses)

### Implementation

```python
# src/ShadowTag-v2/services/safety_scanner.py

class SafetyScanner:
    """
    Scan indexed content for governance violations.

    Lexicons:
    - PII: SSN, credit card, passport, email, phone
    - Security: API keys, passwords, secrets
    - Compliance: GDPR, HIPAA, SOX terms
    - Toxicity: Multilingual offensive terms
    - Dangerous: Chemical weapons, terrorism, CSAM
    """

    GOVERNANCE_LEXICONS = {
        "pii_patterns": [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email
            r"\b[A-Z]{1,2}\d{6,8}\b"  # Passport
        ],
        "security_violations": [
            r"api[_-]?key\s*[:=]\s*['\"]?[\w-]{20,}",
            r"password\s*[:=]\s*['\"]?\w+",
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API key
            r"ghp_[a-zA-Z0-9]{36}"   # GitHub token
        ],
        "compliance_flags": {
            "gdpr": ["data subject", "right to erasure", "consent"],
            "hipaa": ["protected health information", "phi", "medical record"],
            "sox": ["financial statement", "internal control", "audit"]
        },
        "toxicity_terms": {
            "en": ["offensive_term_1", "offensive_term_2"],  # Redacted
            "es": ["término_ofensivo"],
            "fr": ["terme_offensant"]
        }
    }

    def scan_opord(self, opord_content: str) -> Dict[str, List[Dict]]:
        """
        Scan OPORD for violations.

        Returns:
            {
                "pii_found": [{"pattern": "SSN", "count": 2, "samples": [...]}],
                "security_found": [{"pattern": "API_KEY", "count": 1}],
                "compliance_found": [],
                "toxicity_found": [],
                "severity": "HIGH" | "MEDIUM" | "LOW" | "CLEAN"
            }
        """
        violations = {
            "pii_found": self._scan_pii(opord_content),
            "security_found": self._scan_security(opord_content),
            "compliance_found": self._scan_compliance(opord_content),
            "toxicity_found": self._scan_toxicity(opord_content)
        }

        # Calculate severity
        severity = self._calculate_severity(violations)
        violations["severity"] = severity

        return violations

    def scan_pdf(self, pdf_content: str, metadata: Dict) -> Dict:
        """Scan scholarly PDF for dangerous content."""
        # Focus on chemical weapons, terrorism, CSAM
        violations = self._scan_dangerous_content(pdf_content)

        if violations:
            # Flag for Judge#6 review
            self._escalate_to_judge6(violations, metadata)

        return violations

    def scan_agent_output(self, output: str, agent_id: str) -> Dict:
        """
        Scan agent-generated content before indexing.

        Critical for bidirectional corpus - don't index toxic outputs.
        """
        violations = self.scan_opord(output)

        if violations["severity"] in ["HIGH", "CRITICAL"]:
            # Block indexing
            logger.warning(f"Blocked {agent_id} output from indexing: {violations}")
            return {"allowed": False, "violations": violations}

        return {"allowed": True, "violations": violations}
```

### Elasticsearch Integration

```python
# Add safety_score field to index mapping

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            # ... existing fields ...
            "safety_scan": {
                "type": "object",
                "properties": {
                    "severity": {"type": "keyword"},
                    "pii_count": {"type": "integer"},
                    "security_count": {"type": "integer"},
                    "scanned_at": {"type": "date"}
                }
            }
        }
    }
}

# Index with safety metadata
def index_with_safety(doc: Dict):
    scanner = SafetyScanner()
    violations = scanner.scan_opord(doc["full_text"])

    doc["safety_scan"] = {
        "severity": violations["severity"],
        "pii_count": len(violations["pii_found"]),
        "security_count": len(violations["security_found"]),
        "scanned_at": datetime.utcnow().isoformat()
    }

    # Block HIGH/CRITICAL from public search
    if violations["severity"] in ["HIGH", "CRITICAL"]:
        doc["access_level"] = "RESTRICTED"

    es.index(index="opord_contexts", body=doc)
```

---

## 2. Bidirectional Corpus Growth

### Concept
Currently: **PDFs in → agents search**
Enhanced: **PDFs in + agent outputs in → agents search both**

This creates a **compounding knowledge base** where agent discoveries enrich future agent capabilities.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  INPUT SOURCES                                      │
│  ├─ Scholarly PDFs (uploaded)                       │
│  ├─ Agent outputs (OPORD summaries, decisions)     │
│  ├─ Code repos (indexed via MCP)                   │
│  └─ Web research (rtrvr.ai extractions)            │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  SAFETY SCANNER                                     │
│  ├─ PII detection → REDACT                         │
│  ├─ Security violations → BLOCK                     │
│  ├─ Toxicity → FLAG for Judge#6                    │
│  └─ Severity: CLEAN/LOW/MEDIUM/HIGH/CRITICAL       │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  ELASTICSEARCH (Unified Knowledge Corpus)           │
│  ├─ Index: scholarly_pdfs                          │
│  ├─ Index: agent_knowledge                         │
│  ├─ Index: code_snippets                           │
│  └─ Index: web_extractions                         │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  QUERY LAYER (Agents search ALL indices)           │
│  ├─ Cross-index search                             │
│  ├─ Relevance ranking                              │
│  ├─ Safety filtering                               │
│  └─ Citation tracking                              │
└─────────────────────────────────────────────────────┘
```

### Implementation

```python
# src/ShadowTag-v2/services/knowledge_corpus.py

class KnowledgeCorpus:
    """
    Unified knowledge base with bidirectional growth.

    Sources:
    1. Scholarly PDFs (uploaded by admins)
    2. Agent outputs (OPORD summaries, research findings)
    3. Code repositories (indexed via MCP)
    4. Web extractions (rtrvr.ai automation results)
    """

    def __init__(self, es_client, safety_scanner):
        self.es = es_client
        self.scanner = safety_scanner
        self.indices = {
            "scholarly_pdfs": "papers",
            "agent_knowledge": "agent_outputs",
            "code_snippets": "code",
            "web_extractions": "web_data"
        }

    def index_agent_output(
        self,
        opord_number: int,
        agent_id: str,
        output: str,
        output_type: str  # "research_finding", "code_solution", "decision"
    ) -> Dict:
        """
        Index agent output into knowledge corpus.

        This is the KEY to bidirectional growth!
        """
        # Safety scan first
        scan_result = self.scanner.scan_agent_output(output, agent_id)

        if not scan_result["allowed"]:
            logger.error(f"Blocked agent output from indexing: {scan_result}")
            return {"indexed": False, "reason": "safety_violation"}

        # Extract key insights (using LLM summarization)
        insights = self._extract_insights(output)

        # Index in agent_knowledge
        doc = {
            "opord_number": opord_number,
            "agent_id": agent_id,
            "output_type": output_type,
            "content": output,
            "insights": insights,
            "indexed_at": datetime.utcnow().isoformat(),
            "safety_scan": scan_result["violations"]
        }

        self.es.index(index="agent_knowledge", body=doc)

        logger.info(f"Indexed agent output from OPORD {opord_number:05d}")
        return {"indexed": True, "doc_id": doc_id}

    def search_unified(
        self,
        query: str,
        indices: List[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search across ALL knowledge indices.

        Returns results from:
        - Scholarly PDFs (academic papers)
        - Agent knowledge (previous agent discoveries)
        - Code snippets (implementation examples)
        - Web extractions (real-world data)
        """
        if indices is None:
            indices = list(self.indices.keys())

        # Multi-index search
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "insights", "title", "abstract"],
                    "type": "best_fields"
                }
            },
            "highlight": {
                "fields": {"content": {}}
            },
            "size": limit
        }

        # Search across specified indices
        results = []
        for index_key in indices:
            index_name = self.indices[index_key]
            hits = self.es.search(index=index_name, body=es_query)

            for hit in hits["hits"]["hits"]:
                results.append({
                    "source": index_key,
                    "score": hit["_score"],
                    "content": hit["_source"],
                    "excerpts": hit.get("highlight", {}).get("content", [])
                })

        # Sort by relevance
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]
```

### Usage Example

```python
# Agent completes security audit, discovers new attack vector
opord_summary = """
OPORD 00143 Summary:
Discovered novel reentrancy variant in ERC-6551 token-bound accounts.
Attack exploits callback during account creation before ownership transfer.

Mitigation: Add nonReentrant modifier to TBA factory.
Reference: Applied CEI pattern from 'Analyzing Reentrancy' (Smith 2023).
"""

# Index agent's discovery
corpus = KnowledgeCorpus()
corpus.index_agent_output(
    opord_number=143,
    agent_id="agent_042",
    output=opord_summary,
    output_type="research_finding"
)

# Future agent searches for reentrancy
results = corpus.search_unified("reentrancy ERC-6551")
# Returns:
# [
#   {
#     "source": "scholarly_pdfs",
#     "content": "Analyzing Reentrancy Attacks (Smith 2023)..."
#   },
#   {
#     "source": "agent_knowledge",  # ← Previous agent's discovery!
#     "content": "OPORD 00143: Novel reentrancy in TBA creation..."
#   }
# ]
```

---

## 3. CoreWeave GPU Mesh Integration

### Unified Sky–Ground Architecture

```
┌─────────────────────────────────────────────────────┐
│  ORBITAL LAYER (Starlink LEO Satellites)            │
│  ├─ Edge inference (low-latency global)             │
│  ├─ CoreWeave GPUs on satellites ($200k/sat)       │
│  └─ Global backhaul for Context Index sync          │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  TERRESTRIAL LAYER (Cellular Towers)                │
│  ├─ CoreWeave GPUs in 100k towers ($15k/tower)     │
│  ├─ City-level compute for agent swarm              │
│  └─ Ultra-low latency (<50ms p99)                   │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  USER LAYER (Vehicles, Phones, Devices)             │
│  ├─ Tesla, Rivian with edge inference               │
│  ├─ Real-time AI with verified local caching        │
│  └─ 3M vehicles × $500/yr = $1.5B ARR               │
└─────────────────────────────────────────────────────┘
```

### Integration with Atomic Chat

**Use Case**: Agent swarm executes across distributed GPU mesh

```python
# SwarmOrchestrator routes tasks to nearest GPU node

class GPUMeshOrchestrator:
    """
    Route agent tasks to CoreWeave GPU mesh.

    Nodes:
    - Starlink satellites (orbital, global coverage)
    - Cellular towers (terrestrial, city-level)
    - Vehicles (mobile edge)
    """

    def route_task_to_gpu(self, task: Dict, agent_location: str) -> str:
        """
        Route agent task to nearest GPU node.

        Latency targets:
        - Orbital: <100ms
        - Tower: <50ms
        - Vehicle: <20ms
        """
        # Find nearest node
        if agent_location == "global":
            return "starlink_gpu_cluster"
        elif agent_location.startswith("city_"):
            return f"tower_gpu_{agent_location}"
        else:
            return "vehicle_edge_node"
```

### Revenue Impact

| Layer | Annual Revenue | EBITDA Margin | Valuation (20× EBITDA) |
|-------|----------------|---------------|------------------------|
| Infrastructure Mesh | $10B | 84% | $168B |
| ShadowTag-v2 Digital | $6B | 80% | $96B |
| Defense & PNT | $2B | 80% | $32B |
| **Total** | **$18B** | **83%** | **$300B+** |

---

## 4. Agent Builder Best Practices (From X Threads)

**Key Patterns** (rolled up from Ultrathink analysis):

1. **Start Simple**: Python + LangChain/CrewAI + OpenAI + Pinecone
2. **ReAct Loop**: Reason → Act → Observe → Repeat
3. **Memory Types**: Short-term (context window), Long-term (vector DB)
4. **Tools**: Web browse, code exec, APIs (Zapier, MCP, custom)
5. **Multi-Agent**: Planner → Researcher → Reporter → Critic
6. **Evals**: TruLens, custom metrics (speed, cost, success rate)
7. **Guardrails**: Human-in-loop for critical decisions
8. **UI**: Streamlit for MVP, custom React for production

**Politically Incorrect Truth**: 80% of "agents" are glorified API wrappers that hallucinate without proper error handling and human oversight.

**Our Advantage**: OPORD format + safety scanning + swarm consensus = production-grade from day 1.

---

## 5. Next Steps (B+ → A+)

- [ ] **Implement SafetyScanner** - PII, security, compliance lexicons
- [ ] **Enable Bidirectional Indexing** - Agent outputs → searchable knowledge
- [ ] **Integrate CoreWeave GPU Mesh** - Starlink + tower routing
- [ ] **Build E2B Integration** - Secure code execution sandbox
- [ ] **Add rtrvr.ai MCP** - Browser automation for web tasks
- [ ] **Deploy Trial Phase** - 10 async jobs with kill-switch monitoring
- [ ] **Elasticsearch Production** - GKE 3-node cluster deployment
- [ ] **Revenue Experiments** - ShadowTag monitored tier + Sauron's Panorama

**Timeline**: 4 weeks to A+ (safety + bidirectional + trial phase complete)

**Revenue Unlock**: $300B+ valuation path with infrastructure mesh + digital platform

---

**Status**: B+ foundation → A+ with safety + bidirectional growth + GPU mesh integration