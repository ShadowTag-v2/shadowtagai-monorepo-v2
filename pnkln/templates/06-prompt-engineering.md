# Template 06: Prompt Engineering & Craft

## Purpose
Create high-performance, consistent AI prompts for any task.

## When to Use
- Building AI-powered features
- Creating agent instructions
- Optimizing LLM outputs
- Standardizing AI workflows
- Reducing prompt iteration time

---

## Copy-Paste Prompt

```
@prompt Create a prompt for the following task

**Task Description**:
[What the prompt should accomplish - be specific]

**Target Model**: [GPT-4 / Claude / Gemini / Generic]

**Desired Output Format**:
[Describe the structure you want - JSON, markdown, plain text, etc.]

**Task Complexity**: [Simple / Moderate / Complex / Expert]

**Input Variables**:
1. [Variable 1]: [Type and description]
2. [Variable 2]: [Type and description]

**Special Constraints**:
- [Constraint 1]
- [Constraint 2]

**Quality Requirements**:
- Consistency: [How consistent should outputs be?]
- Creativity: [How creative should it be?]
- Accuracy: [Accuracy requirements]

**Edge Cases to Handle**:
1. [Edge case 1]
2. [Edge case 2]

**Deliverables**:
1. Primary prompt (copy-paste ready)
2. System message (if applicable)
3. Few-shot examples (3-5 examples)
4. Usage notes (best practices)
5. Prompt variations (concise/detailed/chain-of-thought)
6. Performance expectations (consistency, quality, failure modes)
```

---

## Example Usage

```
@prompt Create a prompt for the following task

**Task Description**:
Generate product feature descriptions from technical specs that are:
- Customer-benefit focused (not tech-focused)
- Scannable (short paragraphs, bullet points)
- Conversion-optimized (emphasize value, not features)

**Target Model**: Claude

**Desired Output Format**:
Markdown with structure:
- Feature Name
- One-line benefit statement
- 2-3 sentence description
- Bullet list of key capabilities
- Call-to-action suggestion

**Task Complexity**: Moderate

**Input Variables**:
1. technical_spec: String - Raw technical specification
2. target_audience: String - Customer persona
3. product_category: String - Product type

**Special Constraints**:
- No jargon unless target_audience is technical
- Max 150 words per feature description
- Must include at least one metric/number if available

**Quality Requirements**:
- Consistency: High (same format every time)
- Creativity: Medium (engaging but not quirky)
- Accuracy: High (must not misrepresent technical capabilities)

**Edge Cases to Handle**:
1. Technical spec is vague or incomplete
2. Target audience is unclear
3. Feature has no obvious customer benefit

**Deliverables**:
1. Primary prompt (copy-paste ready)
2. System message (if applicable)
3. Few-shot examples (3-5 examples)
4. Usage notes (best practices)
5. Prompt variations (concise/detailed/chain-of-thought)
6. Performance expectations (consistency, quality, failure modes)
```

---

## Expected Output Structure

```
## Primary Prompt

[ROLE/CONTEXT]
You are a product marketing expert who translates technical specifications into customer-facing feature descriptions.

[TASK]
Your task is to transform technical specs into compelling feature descriptions that focus on customer benefits, not technical implementation.

[INSTRUCTIONS]
1. Read the technical specification carefully
2. Identify the core customer benefit (what problem does this solve?)
3. Translate technical terms into customer-friendly language
4. Highlight measurable outcomes where possible
5. Structure the description for scannability

[CONSTRAINTS]
- Do not use jargon unless the target audience is explicitly technical
- Maximum 150 words per feature description
- Always include at least one metric/number if available in the spec
- Ensure accuracy - do not overstate capabilities

[OUTPUT FORMAT]
Deliver your response as:

**Feature Name**: [Benefit-focused name]

**One-Line Benefit**: [Single sentence value proposition]

**Description**:
[2-3 sentences explaining what this does for the customer and why it matters]

**Key Capabilities**:
- [Capability 1]: [Specific outcome]
- [Capability 2]: [Specific outcome]
- [Capability 3]: [Specific outcome]

**Suggested CTA**: [Action-oriented next step]

[EXAMPLES - See below]

---

## System Message (if applicable)

You are a product marketing expert specializing in translating technical features into customer benefits. Your communication style is clear, benefit-focused, and conversion-oriented. You avoid jargon and always tie features back to customer outcomes.

---

## Few-Shot Examples

### Example 1: Technical to Consumer Audience

**Input**:
- technical_spec: "Implements WebSocket connection pooling with automatic reconnection and exponential backoff retry logic"
- target_audience: "Non-technical business users"
- product_category: "Team collaboration tool"

**Output**:
**Feature Name**: Always-On Connectivity

**One-Line Benefit**: Stay connected to your team without interruptions, even when your internet hiccups.

**Description**:
Never lose your work or miss a message again. Our intelligent connection system automatically keeps you online even when your network is unstable. If you do get disconnected, you'll be back online in seconds without lifting a finger.

**Key Capabilities**:
- Automatic reconnection: No manual refresh needed
- Zero data loss: All messages and changes are saved
- Seamless experience: You won't even notice brief disconnections

**Suggested CTA**: See it in action - Try free for 14 days

---

### Example 2: Technical to Technical Audience

**Input**:
- technical_spec: "GraphQL API with real-time subscriptions, automatic batching, and client-side caching"
- target_audience: "Frontend developers"
- product_category: "API platform"

**Output**:
**Feature Name**: High-Performance GraphQL API

**One-Line Benefit**: Build faster frontends with 10x fewer network requests and instant real-time updates.

**Description**:
Stop wrestling with REST endpoints and complex state management. Our GraphQL API gives you exactly the data you need, automatically batches requests to reduce network overhead, and provides built-in real-time subscriptions. Client-side caching means your app feels instant.

**Key Capabilities**:
- Request batching: Combine multiple queries into one network call
- Real-time subscriptions: Live data updates with zero polling
- Automatic caching: 10x faster repeat queries

**Suggested CTA**: View API docs and quickstart

---

### Example 3: Vague Spec (Edge Case)

**Input**:
- technical_spec: "Enhanced security features"
- target_audience: "IT decision makers"
- product_category: "SaaS platform"

**Output**:
**Feature Name**: Enterprise-Grade Security

**One-Line Benefit**: Protect your data with security measures that meet compliance requirements.

**Description**:
We've strengthened our security infrastructure to give you peace of mind. Your data is protected with industry-standard encryption, access controls, and monitoring. [Note: Request more specific technical details from stakeholder to strengthen this description with concrete security measures like SOC 2, encryption standards, etc.]

**Key Capabilities**:
- Enhanced encryption: [Pending spec details]
- Access controls: [Pending spec details]
- Compliance ready: [Pending spec details]

**Suggested CTA**: Schedule security review call

**[Prompt flags incomplete input and requests more details]**

---

## Usage Notes

### Best Practices:
1. **Always provide all three input variables** for best results
2. **Include metrics in technical_spec** when available (e.g., "50% faster", "reduces errors by 80%")
3. **Be specific about target_audience** - "CTOs at Series A startups" not "technical people"
4. **Review output for accuracy** - ensure no technical capabilities are overstated

### Common Pitfalls to Avoid:
1. Vague technical specs → vague output (garbage in, garbage out)
2. Unclear audience → tone mismatch
3. Missing metrics → less compelling copy

### How to Adjust for Different Use Cases:
- **More technical audience**: Add "include technical details" to input
- **More creative output**: Add "use analogies and storytelling" to instructions
- **Shorter output**: Reduce word limit constraint

---

## Prompt Variations

### Version A: Concise (for simple features)
[Simplified version with fewer instructions, good for straightforward features]

### Version B: Detailed (for complex features)
[Extended version with more examples and edge case handling]

### Version C: Chain-of-Thought (for nuanced positioning)
[Version that thinks through customer psychology and messaging angles before writing]

---

## Performance Expectations

### Consistency Score: 85%
- Same format every time
- Occasional variation in tone based on input complexity

### Quality Level: High
- Output is ready to use with minimal editing
- Captures customer benefits accurately
- Scannable and conversion-focused

### Failure Modes:
1. **Vague technical specs** → Prompt will flag and request more details
2. **Contradictory constraints** → Prompt will ask for clarification
3. **Highly technical spec + non-technical audience** → May oversimplify; review needed

### Mitigation Strategies:
- Provide detailed technical specs with metrics
- Be specific about audience technical level
- Include competitor examples for reference
```

---

## Tips for Best Results

1. **Be Specific About Task**: "Generate product descriptions" not "write copy"
2. **Define Output Format**: Show exact structure you want
3. **Provide Examples**: Few-shot examples dramatically improve consistency
4. **List Edge Cases**: What could go wrong? Handle it in the prompt
5. **Test and Iterate**: Try the prompt, find failures, refine

---

## Related Templates
- [03: High-Converting Copy](#) - For marketing copy generation
- [05: Workflow Optimization](#) - To build prompts into workflows
