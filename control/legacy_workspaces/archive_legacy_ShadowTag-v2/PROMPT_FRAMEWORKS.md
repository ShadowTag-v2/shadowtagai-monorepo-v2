# Prompt Framework Templates

## Overview
This document contains 5 powerful prompt engineering frameworks designed to help you create effective, structured prompts for AI interactions. Each framework serves different use cases and provides a systematic approach to prompt construction.

---

## 1. R-T-F Framework
**Role - Task - Format**

### Structure
- **ROLE**: Define who the AI should act as
- **TASK**: Specify what needs to be accomplished
- **FORMAT**: Clarify the desired output format

### When to Use
- Creating structured outputs with specific deliverables
- When you need a professional persona with clear deliverables
- Marketing, design, and creative projects

### Example

```
Role: Act as a Facebook Ad Marketer

Task: Design a compelling Facebook ad campaign to promote a new line of fitness apparel for a sports brand

Format: Create a storyboard outlining the sequence of ad creatives, including ad copy, visuals, and targeting strategy
```

---

## 2. T-A-G Framework
**Task - Action - Goal**

### Structure
- **TASK**: Define the task to be performed
- **ACTION**: State the specific action to take
- **GOAL**: Clarify the measurable goal or outcome

### When to Use
- Performance evaluation and improvement scenarios
- When you need measurable, goal-oriented outcomes
- Team management and business optimization

### Example

```
Task: The task is to evaluate the performance of team members

Action: Act as a Direct Manager and assess the strengths and weaknesses of team members

Goal: Improve team performance so that the average user satisfaction score moves from 6 to 7.5 in the next quarter
```

---

## 3. B-A-B Framework
**Before - After - Bridge**

### Structure
- **BEFORE**: Explain the current problem or situation
- **AFTER**: State the desired outcome or end state
- **BRIDGE**: Ask for the plan/solution to get from Before to After

### When to Use
- Problem-solving scenarios
- Strategic planning and transformation projects
- SEO, marketing, and growth initiatives

### Example

```
Before: We're nowhere to be seen on SEO rankings

After: We want to be in top 10 SEO ranking in our niche in 90 days

Bridge: Develop a detailed plan mentioning all the measures we should take, also include a list of top 20 keywords
```

---

## 4. C-A-R-E Framework
**Context - Action - Result - Example**

### Structure
- **CONTEXT**: Give the background and situation
- **ACTION**: Describe what needs to be done
- **RESULT**: Clarify the desired outcome
- **EXAMPLE**: Provide a reference example of similar success

### When to Use
- Marketing campaigns and brand initiatives
- When you have successful case studies to reference
- Projects requiring contextual understanding

### Example

```
Context: We are launching a new line of sustainable clothing

Action: Can you assist us in creating a targeted advertising campaign that emphasizes our environmental commitment?

Result: Our desired outcome is to drive product awareness and sales

Example: A good example of a similar successful initiative is Patagonia's "Don't Buy This Jacket" campaign, which highlighted their commitment to sustainability while enhancing their brand image
```

---

## 5. R-I-S-E Framework
**Role - Input - Steps - Expectation**

### Structure
- **ROLE**: Specify the role or persona
- **INPUT**: Describe the data/information you're providing
- **STEPS**: Ask for a step-by-step approach
- **EXPECTATION**: Describe the expected outcome or metrics

### When to Use
- Content strategy and planning
- Multi-step processes requiring detailed planning
- When you have specific data to provide as input
- Projects with measurable KPIs

### Example

```
Role: Imagine you are a content strategist

Input: I've gathered detailed information about our target audience, including their interests and common questions related to our industry

Steps: Provide a step-by-step content strategy plan:
1. Identify key topics based on our audience insights
2. Create an editorial calendar
3. Draft engaging content that aligns with our brand message

Expectation: The aim is to increase our blog's monthly visitors by 40% and enhance our brand's position as a thought leader in our industry
```

---

## Quick Reference Chart

| Framework | Best For | Key Strength |
|-----------|----------|--------------|
| **R-T-F** | Creative deliverables | Clear role + structured output |
| **T-A-G** | Performance optimization | Measurable goals |
| **B-A-B** | Problem solving | Clear transformation path |
| **C-A-R-E** | Campaigns with precedent | Context + proven examples |
| **R-I-S-E** | Strategic planning | Detailed step-by-step guidance |

---

## Tips for Using These Frameworks

1. **Choose the Right Framework**: Match the framework to your specific use case
2. **Be Specific**: The more detail you provide, the better the output
3. **Provide Context**: Background information helps AI understand nuances
4. **Set Clear Expectations**: Define success metrics when applicable
5. **Iterate**: Refine your prompts based on the responses you get
6. **Combine Frameworks**: You can mix elements from different frameworks as needed

---

## Integration with Claude Agent SDK

These frameworks work seamlessly with the Claude Agent SDK. Here's how to use them:

### TypeScript/JavaScript Example

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// Using R-T-F Framework
const result = await query({
  prompt: `
    Role: Act as a Senior Software Architect

    Task: Design a microservices architecture for a real-time chat application

    Format: Provide a detailed system design document including:
    - Service breakdown and responsibilities
    - Communication patterns
    - Data flow diagrams
    - Technology stack recommendations
  `,
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" }
  }
});
```

### Python Example

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Using B-A-B Framework
async for message in query(
    prompt="""
    Before: Our API response times are averaging 2000ms, causing user frustration

    After: We need API response times under 200ms with 99.9% reliability

    Bridge: Analyze our current FastAPI service and provide a detailed optimization plan
    """,
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"}
    )
):
    print(message)
```

---

## Version History

- **v1.0** (2025-11-08): Initial documentation with 5 core frameworks

---

## Contributing

When adding new frameworks or examples:
1. Follow the established structure
2. Provide clear, practical examples
3. Explain when to use each framework
4. Include code examples where applicable

---

## Resources

- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Best Practices for Prompting](https://docs.anthropic.com/claude/docs/intro-to-prompting)
