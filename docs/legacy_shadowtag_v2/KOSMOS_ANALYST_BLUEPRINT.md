# KOSMOS ANALYST: THE "DEEP RESEARCH" UPGRADE

> **INSPIRATION**: Gombocz Agentic ETL
> **GOAL**: Turn Kosmos from a "Task Executor" into a "Research Scientist".
> **METHOD**: Recursive Context + Headless Browsing + Dynamic Artifacts.

## 1. THE GAP (How to make it better)

The article describes a **Linear Flow** (Scrape -> Analyze -> Report).
**Kosmos will utilize a Recursive Loop**:

1.  **Hypothesize**: "I think pattern X exists."
2.  **Hunt**: Scrape data (Jetski Heavy).
3.  **Prove**: Run analysis.
4.  **Visualize**: Generate interactive dashboard (Artifact).
5.  **Refine**: If data is weak, _change the search parameters_ and hunt again. (Autonomy).

## 2. THE STACK UPGRADE

### A. "Jetski Heavy" (The Harpoon)

- **Old**: `requests` (Static HTML).
- **New**: `playwright` (Dynamic JS, Infinite Scroll, Screenshots).
- **Sovereign Twist**: Run headlessly in the `https://github.com/karpathy/autoresearchs` container or via a specific Cloud Run sidecar.

### B. "Context Reactor" (The Brain)

- Instead of just reading a file, Kosmos will **maintain a live SQL/JSON database** of its findings (`src/data/knowledge_graph.json`).
- It will write its own "Learnings" into `GEMINI.md` to prevent future Amnesia.

### C. "Artifact Engine" (The Display)

- Kosmos will be trained to output single-file HTML/React dashboards (using `recharts` or `d3`) that the user can open immediately.

## 3. IMPLEMENTATION PLAN

### Phase 1: The Tooling

- [ ] Install `playwright`.
- [ ] Create `src/tools/jetski_heavy.py` (The Browser).

### Phase 2: The Logic

- [ ] Create `src/functions/kosmos_analyst/main.py`.
- [ ] Define the "Deep Research" prompt chain.

### Phase 3: The Visualization

- [ ] Create `src/templates/dashboard_template.html`.

## 4. EXAMPLE WORKFLOW

**User**: "Analyze the trends in AI Agents from my bookmarks."
**Kosmos**:

1.  Spins up `Jetski Heavy`.
2.  Logins to source (if needed) & scrolls.
3.  Extracts 1000+ items.
4.  Clustering Analysis (Python/Scikit).
5.  **Generates**: `trends_dashboard.html` (Interactive chart).
6.  **Updates**: `GEMINI.md` with "Key Insignt: Agents are moving from Chat to Action."
