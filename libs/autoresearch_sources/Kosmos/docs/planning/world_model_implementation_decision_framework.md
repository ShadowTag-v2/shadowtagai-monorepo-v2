# World Model Implementation Decision Framework

**Status:** Decision Made - "All Three" Goals
**Date:** November 2025
**Context:** GitHub Issue #4 + World Model Architecture Research Analysis
**Decision:** Path 3 with Architectural Discipline

---

## Executive Summary

### The Fundamental Disconnect

A critical gap exists between the Kosmos paper's vision and the current codebase implementation:

**What Andrew White Designed:**
- Structured world models as **queryable databases** (not expanded context windows)
- Information persists across millions of tokens and 200+ agent rollouts
- Enables "coherent pursuit" over extended research cycles
- **This is the core innovation** that made Kosmos work

**What the Current Codebase Has:**
- Ephemeral knowledge graphs that reset each run
- No persistence between research sessions
- Knowledge graph feature **disabled by default** (`use_knowledge_graph = False`)
- Infrastructure code exists but no accumulated knowledge

**Analogy:** We've built a brain that forgets everything each night. The coherence White describes is impossible without persistence.

### The Revelation: Pursuing All Three Goals

**The Core Question:** *"What is jimmc414/Kosmos trying to be?"*

**The Answer:** **ALL THREE:**

- **Goal A:** Faithful reproduction of FutureHouse's production system architecture
- **Goal B:** Practical tool individual researchers can actually use today
- **Goal C:** Educational reference implementation showing concepts at multiple scales

**This is not a compromise - it's a strength.** By pursuing all three goals simultaneously through phased implementation, we create:
- A usable tool NOW (Goal B)
- That teaches architectural patterns (Goal C)
- While building toward production-grade system (Goal A)

### The Implementation Strategy

**Path 3: Hybrid Incremental with Architectural Discipline**

**Simple Mode (Default):** Works great for 90% of users
- Persistent Neo4j
- Local deployment
- Low operational complexity
- Practical and usable immediately

**Production Mode (Optional):** For organizations and power users
- Full polyglot architecture (PostgreSQL + Neo4j + Elasticsearch + ChromaDB)
- Enterprise features and scale
- Opt-in via configuration
- Faithful to paper's vision

**Educational Value:** Throughout
- Architecture documentation explaining the why
- Code shows patterns at multiple scales
- Examples demonstrate progression
- Clear upgrade paths teach scaling decisions

**Timeline:**
- **6 weeks:** Simple mode working (Phase 1)
- **3 months:** Full simple mode features (Phases 1-3)
- **5 months:** Production mode available (Phase 4)
- **Ongoing:** Both modes maintained and improved

---

## How "All Three" Changes The Approach

### What Stays The Same

- **Path 3 (Hybrid Incremental) is still the foundation**
- **Deliver practical value first** (Phase 1 in 2-3 weeks)
- **Validate with users** before heavy investment
- **Incremental phases** justified by demand

### What Changes Significantly

#### 1. Architecture Must Be "Upgrade-Friendly"

Design with abstraction layers from Day 1:

```python
# Abstract interface all phases use
class WorldModelStorage(ABC):
    """
    World model storage abstraction.

    Current: Neo4j simple implementation (Phase 1-3)
    Future: Polyglot persistence (Phase 4+ production mode)
    Paper: White et al. "structured world models" principle
    """
    @abstractmethod
    def add_entity(self, entity: Entity) -> str:
        """Add entity to world model."""
        pass

    @abstractmethod
    def query(self, query: str, **kwargs) -> Results:
        """Query world model."""
        pass

# Phase 1-3: Simple implementation
class Neo4jWorldModel(WorldModelStorage):
    """Simple Neo4j-based world model for individual researchers."""
    def add_entity(self, entity: Entity) -> str:
        # Direct Neo4j operations
        return self.neo4j.create_node(entity)

    def query(self, query: str, **kwargs) -> Results:
        # Cypher queries
        return self.neo4j.execute(query)

# Phase 4+: Production implementation
class PolyglotWorldModel(WorldModelStorage):
    """Production polyglot world model."""
    def __init__(self):
        self.postgres = PostgresClient()    # Transactions
        self.neo4j = Neo4jClient()          # Relationships
        self.elasticsearch = ESClient()     # Provenance
        self.vector_db = ChromaDBClient()   # Semantic search

    def add_entity(self, entity: Entity) -> str:
        # Route to appropriate backend
        entity_id = self.postgres.insert(entity)
        self.neo4j.create_node(entity, entity_id)
        self.elasticsearch.index_event(entity)
        self.vector_db.embed(entity)
        return entity_id
```

**Key Principle:** Write Phase 1 so Phase 4 can swap implementations without breaking user code.

#### 2. Documentation Becomes First-Class

Since we're aiming for educational value:

```
docs/
├── architecture/
│   ├── world_model_vision.md          # Full vision (Goal A)
│   ├── design_principles.md           # Why decisions made (Goal C)
│   ├── simple_mode_architecture.md    # Phase 1-3 design
│   ├── production_mode_architecture.md # Phase 4 design
│   ├── migration_paths.md             # Phase transitions
│   └── decision_records/              # ADRs for key choices
├── guides/
│   ├── getting_started.md             # Quick start (Goal B)
│   ├── building_knowledge_base.md     # Using simple mode
│   ├── production_deployment.md       # Using production mode (Goal A)
│   └── troubleshooting.md
└── tutorials/
    ├── understanding_world_models.md  # Concepts (Goal C)
    ├── from_ephemeral_to_persistent.md # Evolution story
    └── scaling_architecture.md        # When and how (Goal A+C)
```

Each phase document explains:
- What we're building
- Why this architecture choice
- How it maps to paper's vision
- What we're deferring and why
- How to migrate to next phase

#### 3. Each Phase Must Be Production-Quality

Not prototypes - real implementations:
- **Phase 1:** "Persistent world models at small scale" (not toy)
- **Phase 2:** "User control and quality patterns" (not hacks)
- **Phase 3:** "Multi-project architecture" (not workaround)

Each phase:
- Thoroughly tested
- Well documented
- Usable in production at that scale
- A learning resource showing patterns

#### 4. Progressive Enhancement Pattern

Same interfaces, different capabilities:

```python
class WorldModel:
    def __init__(self, mode: str = "simple"):
        if mode == "simple":
            self.storage = Neo4jWorldModel()
        else:  # production
            self.storage = PolyglotWorldModel()

    def query(self, question: str) -> Results:
        """Query world model with appropriate backend."""
        if self.config.mode == "simple":
            # Direct Cypher query
            return self.storage.simple_query(question)
        else:
            # Full GraphRAG with semantic search
            return self.storage.advanced_query(question)
```

#### 5. Clear Migration Paths

Tools for transitions:

```bash
# Migrate between phases
kosmos migrate phase1-to-phase2
kosmos migrate simple-to-production

# Export for different targets
kosmos export --format simple           # Phase 1-3 format
kosmos export --format production       # Phase 4 format
kosmos export --format paper-supplement # Research publication

# Validate compatibility
kosmos validate-migration --target production
```

---

## Research Analysis Summary

[Content remains the same as original document through "Critical Gaps Identified" section - lines 46-117]

### What the Polyglot Architecture Research Reveals

**Source:** `docs/planning/optimal_world_model_architecture_research.md`

**Key Findings:**
- Kosmos paper describes a production system coordinating 200 parallel agents
- Processes 42,000 lines of code per run across 20+ cycles
- Costs $200 per investigation with $5,700-6,500/month infrastructure
- Requires polyglot persistence: PostgreSQL (transactions), Neo4j (relationships), Elasticsearch (provenance), ChromaDB/Pinecone (semantic search)

**Critical Insight:**
This architecture solves for **production-scale multi-agent coordination** at FutureHouse, not individual researcher workflows.

**What It Doesn't Address:**
- Individual researcher workflows (weeks/months, not 12-hour runs)
- Multiple concurrent projects per user
- Knowledge sharing between researchers
- Local laptop deployment
- Minimal operational complexity for open-source users

### What Andrew White's Blog Insights Reveal

**Source:** `docs/planning/optimal_world_model_architecture_research_from_blog.md`

**Key Principles Extracted:**
1. **Structured world models enable persistence beyond context limits**
2. **Simplicity beats complexity**
3. **Small specialized models exceed large generalists**
4. **Complete provenance is mandatory**
5. **Demonstration trajectories are more valuable than training data**
6. **Parallel execution with shared memory beats sequential chaining**
7. **Iterative cycles with world model updates enable progressive refinement**

**Critical Insight:**
White describes **design principles** and **why** they matter, not **how** to implement them for end users.

### Critical Gaps Identified

**1. Scale Mismatch**
- Research describes 200-agent production system
- Open-source users need single-researcher local tool

**2. User Workflow Mismatch**
- Research assumes one 12-hour continuous run
- Real users work over weeks/months with interruptions

**3. Mental Model Mismatch**
- Research focuses on system architecture
- Users think in terms of projects and expertise

**4. Operational Complexity Mismatch**
- Research recommends 4 database systems
- Open-source users want simple setup

---

## Architectural Principles for "All Three" Goals

### Principle 1: Interface-Based Design

Every major component has a clean interface allowing implementation swaps:

```python
from abc import ABC, abstractmethod

class WorldModelStorage(ABC):
    """Storage abstraction - simple or polyglot."""
    @abstractmethod
    def add_entity(self, entity: Entity) -> str: ...
    @abstractmethod
    def get_entity(self, entity_id: str) -> Entity: ...
    @abstractmethod
    def query(self, query: str) -> List[Entity]: ...

class ProvenanceTracker(ABC):
    """Provenance tracking - basic or PROV-O standard."""
    @abstractmethod
    def record_derivation(self, output: str, inputs: List[str]): ...
    @abstractmethod
    def trace_lineage(self, entity_id: str) -> ProvenanceChain: ...

class SemanticSearch(ABC):
    """Semantic search - keywords or vector embeddings."""
    @abstractmethod
    def find_similar(self, query: str, top_k: int) -> List[Entity]: ...

class QueryEngine(ABC):
    """Query engine - Cypher or GraphRAG."""
    @abstractmethod
    def execute_query(self, natural_language: str) -> Results: ...
```

### Principle 2: Configuration-Driven Mode Selection

One codebase, multiple deployment modes:

```yaml
# config.yaml
world_model:
  mode: simple  # or "production"

  simple:
    backend: neo4j
    path: ~/.kosmos/neo4j_data
    provenance: basic
    semantic_search: keyword

  production:
    postgres:
      url: postgresql://REDACTED_USER:REDACTED_PASS@WangRentu,

Thank you for the kind words and excellent question!

**Current State:**
Kosmos doesn't include a pre-built world-model knowledge graph. Instead, it builds
knowledge graphs dynamically during research runs using Neo4j. Currently these graphs
are ephemeral (reset each run), though all infrastructure exists to make them persistent.

**What We're Building:**
We're implementing persistent world models through a phased approach that achieves
three simultaneous goals:

1. **Practical tool you can use TODAY** - Simple persistent graphs that accumulate knowledge
2. **Educational reference** - Clear documentation showing how to build and scale world models
3. **Production-grade system** - Path to full architecture matching the Kosmos paper

**Timeline:**
- **6 weeks:** Simple mode working (persistent Neo4j, export/import, project management)
- **3 months:** Full curation features (verification, quality analysis, duplicate management)
- **5 months:** Production mode available (optional polyglot architecture for enterprise scale)

**How This Helps You:**
- Build domain expertise over weeks/months
- Export and share knowledge graphs
- Choose simple local deployment OR enterprise production deployment
- Learn architectural patterns through documented progression

**Your Input Matters:**
Before finalizing the design, we'd love your feedback:

1. Would you use this for ongoing research, or one-time investigations?
2. One unified graph, or separate graphs per project?
3. Individual use, or collaboration with colleagues?
4. What would make a sample/snapshot most useful to you?

**Next Steps:**
We're in Phase 0 (architecture planning and validation). Your feedback directly shapes
the implementation. Want to influence the design? We'd love your thoughts in the
discussion thread we're creating.

**See the Code:**
- `kosmos/knowledge/graph.py` - Current Neo4j implementation
- `docs/planning/world_model_implementation_decision_framework.md` - Full design

Thanks for your interest! This is exactly the kind of feature that makes Kosmos more powerful.
```

---

## Conclusion: The "All Three" Strategy

### Why This Works

**Goal A (Faithful Reproduction):**
- Production mode implements full paper architecture
- Clear documentation of polyglot persistence
- Proven path from simple to sophisticated
- **Achieved:** Month 5, maintained ongoing

**Goal B (Practical Tool):**
- Simple mode works immediately
- Low barrier to entry
- 90% of users never need complexity
- **Achieved:** Week 6, enhanced months 2-3

**Goal C (Educational Reference):**
- Architecture docs explain the journey
- Code shows patterns at multiple scales
- Tutorials teach scaling decisions
- **Achieved:** Ongoing throughout

### The Core Insight

**You don't have to choose.** With proper architectural discipline:
- Build the simple path first (Goal B)
- Document the sophisticated destination (Goal A)
- Explain the journey between them (Goal C)

Each phase delivers standalone value while building toward the complete vision.

### Updated Recommendation

**Implement Path 3 with Architectural Discipline:**

**Weeks 1-2:**
- Validate user interest
- Create architecture vision documents
- Design abstract interfaces

**Weeks 3-6:**
- Implement Simple Mode with abstraction layer
- Deliver immediate user value
- Document both what and why

**Months 2-3:**
- Add curation and multi-project features
- Refine based on user feedback
- Enhance educational materials

**Months 4-5:**
- Refine simple mode
- Add production mode as opt-in
- Complete the full vision

**Ongoing:**
- Maintain both simple and production modes
- Grow user community
- Enhance based on real usage

### The Final Answer

**"What is jimmc414/Kosmos trying to be?"**

**ALL THREE:**
- A faithful reproduction of FutureHouse's vision (eventually)
- A practical tool researchers use daily (immediately)
- An educational reference showing the way (continuously)

**Different users get different value:**
- Students learn from the architecture
- Researchers use the simple mode
- Organizations deploy the production mode

**Same codebase, same vision, multiple audiences.**

### Next Steps

1. **This week:** Respond to Issue #4, validate interest
2. **Weeks 1-2:** Architecture planning and documentation
3. **Weeks 3-6:** Implement Phase 1 (Simple Mode + abstractions)
4. **Month 2+:** Iterate based on user feedback
5. **Month 5:** Production mode available for those who need it

**Start with abstraction. Build for today. Plan for tomorrow.**

---

**Document Status:** Ready for requirements.md, architecture.md, implementation.md derivation
**Recommended Review:** Architecture team, UX team, Community feedback
**Next Document:** requirements.md (derive user stories and acceptance criteria)
