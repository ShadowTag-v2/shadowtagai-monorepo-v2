# Antigravity Architecture Analysis

## 1. Browser DNA: Jetski vs. Antigravity

The difference is between a **Tool** and a **Cognitive Extension**.

### Jetski (OSS / "The Mechanical Arm")

- **Nature**: A Python wrapper around `Playwright`.
- **Vision**: Sees the **DOM** (HTML Source). It sees `<div><span class="btn">...</span></div>`.
- **Action**: "Click selector `#submit-btn`".
- **Pros**: Standard, widely supported, deterministic.
- **Cons**: **Fragile**. If the `id` changes, it breaks. **High Cognitive Load**: The LLM must read 100kb of HTML to find one button.
- **Implementation**: Currently installed in `uphillsnowball`. Ready to use.

### Antigravity ("The Leaked DNA" / "The Bionic Eye")

- **Nature**: A "Computer Use" paradigm derived from Claude/Gemini system prompts.
- **Vision**: Sees the **Accessibility Tree**. It filters out the noise and sees clean objects: `Button(name="Submit", id=42)`.
- **Action**: "Click object `42`".
- **Pros**: **Robust**. Semantic addressing survives layout changes. **Low Token Cost**: Sends ~50 lines of tree structure instead of 5000 lines of HTML.
- **Implementation Status**:
  - ✅ **DNA**: We injected the System Prompts (`system_prompts_leaks`) into `/opt/antigravity`. The Model _knows_ how to behave.
  - ✅ **Driver**: **SOLVED**. The `browser-use` repository (cloned to `src/browser-use`) contains the specific Python implementation needed (`DomService`, `EnhancedSnapshotNode`) to map CDP Accessibility Trees to the coordinate system expected by the DNA prompts.
  - **Next Step**: Integrate `browser_use.dom.service.DomService` into `antigravity_workstation`.

## 2. Kosmos Actual & The Whiteboard

Where does your `src/whiteboard` fit into the rigorous Kosmos scientific machine?

### Kosmos "World Model" (The Database)

- **Location**: `src/kosmos/kosmos/world_model/`
- **Format**: Structured JSON Artifacts ("Findings", "Hypotheses") + (Optional) Neo4j Knowledge Graph.
- **Role**: The "Long-Term Memory" and "Truth Source". Rigorous, validated, immutable history.

### The Whiteboard (The Canvas)

- **Location**: `src/whiteboard`
- **Role**: The "Workspace" / "Presentation Layer". Mutable, human-centric, messy.

### Integration Strategy: "The Live Feed"

We should not merge them, but **wire them together**.

1.  **Input (Context)**:
    - Configure Kosmos `SkillLoader` or `LiteratureAnalyzer` to treat `src/whiteboard/*.md` as **User Context**.
    - _Effect_: If you doodle an idea on the whiteboard, the Swarm reads it as a "Assumption" or "Hypothesis" to test.

2.  **Output (Reporting)**:
    - Update `flying_monkeys.py` (or `ArtifactStateManager`) to mirror **Validated Findings** to the Whiteboard.
    - _Effect_: When Kosmos proves a hypothesis, it "pins" a card to your `src/whiteboard/findings/` directory.

3.  **The Driver**:
    - Once `antigravity_browser.py` is built, Kosmos Agents can use it to _browse_ your Whiteboard (if it's a web app) or _edit_ the markdown files directly to update status.
