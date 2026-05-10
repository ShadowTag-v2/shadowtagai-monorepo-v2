# KOSMOS: LEAKED TECH SYNTHESIS

> **CLASSIFICATION**: TIER 1 // XENOTECH
> **SOURCE**: `github.com/asgeirtj/system_prompts_leaks` (Anthropic)
> **STATUS**: REVERSE ENGINEERED

## 1. THE "THINKING" PROTOCOL (METACOGNITION)
**Discovery**: Claude 3.7+ uses an explicit `<antml:thinking>` block *after* tool results but *before* the final answer.
**Why it matters**: This forces the model to "reason" over the data it just fetched, preventing hallucinations and "lazy" answers.

### Implementation Pattern
```xml
<antml:thinking_mode>interleaved</antml:thinking_mode>
<antml:max_thinking_length>16000</antml:max_thinking_length>

<!-- After Tool Output -->
<antml:thinking>
1. Analyze the search results from [tool_name].
2. Identify conflicts between Source A and Source B.
3. Determine if sufficient information exists to answer.
4. Plan next step: [Final Answer] or [More Research].
</antml:thinking>
```

## 2. CITATION ENGINE (ANTML)
**Discovery**: A rigorous `DOC_INDEX-SENTENCE_INDEX` citation format.
**Why it matters**: Eliminates "fake links". Every claim MUST be backed by a specific sentence index.

### Logic
- **Single Source**: `<antml:cite index="DOC_0-SENT_5">Claim</antml:cite>`
- **Span**: `<antml:cite index="DOC_0-SENT_5:SENT_8">Claim spanning sentences</antml:cite>`

## 3. SEARCH BRAKES (QUERY COMPLEXITY)
**Discovery**: A decision tree for *when* to search.
- **NEVER SEARCH**: "Capital of France", "Python loop syntax".
- **SINGLE SEARCH**: "Weather in Tokyo", "Who won the game yesterday".
- **RESEARCH (5+ Calls)**: "Compare our Q3 revenue to industry".
**Action**: We will implement this `QueryComplexity` logic in `KosmosMonkeys`.

## 4. ARTIFACTS v2 (MODERN AESTHETICS)
**Discovery**: Explicit instruction to "Wow" the user.
- **Directives**: "Glassmorphism", "Micro-animations", "Vibrant Gradients".
- **Anti-Pattern**: No "Placeholders". No `localStorage`.

## 5. USER PREFERENCES (CONTEXTUAL ADAPTATION)
**Discovery**: Separation of `Behavioral` vs `Contextual` preferences.
- **Rule**: Only apply "Contextual" (e.g., "I am a doctor") if the query is *relevant* to that context.
- **Rule**: "Behavioral" (e.g., "Speak Japanese") is *always* applied.

## 6. NEXT STEPS (INTEGRATION)
1.  **Inject**: Add `<antml:thinking>` blocks to `KosmosMonkeys` system prompt.
2.  **Enforce**: Update `Judge6` to punish "lazy citations" (require spans).
3.  **Refine**: Update `Cockpit` artifacts to default to "Modern/Glassmorphism".

## 7. THE OPENAI "AUTOMATIONS" PROTOCOL (TIME TRAVEL)
**Discovery**: `gpt-5-thinking.md` includes an `automations` tool.
**Why it matters**: It allows the agent to "schedule" itself.
- **Mechanism**: Agents can create iCal (`BEGIN:VEVENT`) tasks.
- **Gain**: We will add a `SchedulerMonkey` that uses this protocol to handle "Remind me to check X tomorrow" autonomously.

## 8. THE "RICH UI" WIDGETS (VISUAL DENSITY)
**Discovery**: OpenAI has specific "Rich UI" protocols for Stocks, Weather, Sports.
**Why it matters**: Standardizes "Widget" responses instead of text dumps.
- **Protocol**:
  - Stock: `<antml:widget name="stock_chart" ticker="NVDA">`
  - Weather: `<antml:widget name="weather_forecast" location="SF">`
- **Action**: Update `Cockpit` to render these specific tags as React components.

## 9. THE PERPLEXITY "COMET" PROTOCOL (BROWSER CONTROL)
**Discovery**: `comet-browser-assistant.md` reveals a rigorous browser control schema.
**Techniques**:
- **Parallelism**: Explicit instruction to "Use parallel tasks for truly independent actions" (e.g., "add iPhone AND Mac to cart").
- **ID System**: Uses `{type}:{index}` (e.g., `tab:2`, `email:5`) to reference context cleanly.
- **Action**: Upgrade our `Jetski` browser agent to use this ID system and parallel execution logic.

## 10. THE "ROBOT" PERSONALITY (EFFICIENCY)
**Discovery**: `gpt-5-robot-personality.md`.
**Core Trait**: "Zero anthropomorphism. Slice away verbal fat."
**Directives**:
- "No fluff, calm always."
- "Systems thinking, user priority."
- "Quotations on demand" (only when comfort is asked for).
- **Gain**: This is the perfect personality for our "Level 2" background workers (e.g., `CodePMCS`). They should not chat; they should execute.

## 11. STRATEGIC INTEGRATION MAP
| Tech | Source | Target Component |
| :--- | :--- | :--- |
| **Thinking Mode** | Claude 3.7 | `KosmosMonkeys` (Deep Thinkers) |
| **Automations** | OpenAI GPT-5 | `Trinity` (Orchestrator) |
| **Rich UI** | OpenAI GPT-5 | `Cockpit` (Frontend) |
| **Comet Protocol** | Perplexity | `Jetski` (Browser Agent) |
| **Robot Persona** | OpenAI | `CodePMCS` (Background Workers) |
