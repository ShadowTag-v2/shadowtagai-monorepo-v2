# Getting Started with Claude Master All-Agent Framework

This guide will walk you through building your first production-ready Claude agent in under 30 minutes.

---

## Prerequisites

### Software Requirements
- Node.js 18+ (for TypeScript/JavaScript) OR Python 3.9+
- Git
- Text editor or IDE
- Anthropic API key

### Get an API Key

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Navigate to API Keys
3. Create a new key
4. Save it securely (you'll use it as `ANTHROPIC_API_KEY`)

---

## Quick Start (5 minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services

# Choose your path:

# TypeScript/JavaScript
npm install

# Python
pip install -r requirements.txt
```

### 2. Set API Key

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-key-here'

# Windows
set ANTHROPIC_API_KEY=your-key-here
```

### 3. Run Your First Agent

**TypeScript:**
```bash
npx tsx examples/typescript/workflow/simple-validation.ts
```

**Python:**
```bash
python examples/python/workflow/simple_validation.py
```

You should see output showing the agent processing a data validation task.

---

## Build Your First Agent (20 minutes)

We'll build a simple but production-ready coding assistant agent.

### Step 1: Choose Your Pattern

Use the [Decision Tree](../framework/decision-tree.md) to choose the right pattern.

For a coding assistant that helps with code review and refactoring:
- ✅ Dynamic decision-making required
- ✅ Single agent can handle it
- **Pattern**: Single-Agent

### Step 2: Define the Prompt

Create `my-coding-agent.ts` (or `.py`):

**TypeScript:**
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const codingAgentPrompt = `
<agent_configuration>
  <metadata>
    <agent_name>Code Review Assistant</agent_name>
    <version>1.0.0</version>
    <pattern>single-agent</pattern>
  </metadata>

  <role>
You are a senior software engineer with 10 years of experience in TypeScript,
Python, and system design. You specialize in code review, identifying bugs,
security issues, and performance problems. You provide constructive feedback
with specific, actionable recommendations.
  </role>

  <core_capabilities>
Primary Capabilities:
- Code analysis and bug detection
- Security vulnerability identification
- Performance optimization recommendations
- Best practices enforcement
- Refactoring suggestions

Analysis Focus:
1. Correctness: Logic errors, edge cases, type safety
2. Security: Injection attacks, data validation, auth issues
3. Performance: Complexity, inefficient algorithms, memory leaks
4. Maintainability: Code clarity, documentation, testing
  </core_capabilities>

  <quality_standards>
Every code review must:
- Identify all critical bugs and security issues
- Provide specific line numbers for issues
- Suggest concrete fixes with code examples
- Prioritize issues by severity (Critical/High/Medium/Low)

Before finalizing review:
1. Check all code paths analyzed
2. Verify recommendations are actionable
3. Ensure explanations are clear
  </quality_standards>

  <constraints>
Must NOT:
- Suggest changes without explanation
- Make assumptions about requirements
- Recommend over-engineering
- Ignore security concerns

Focus on:
- Production-ready code quality
- Practical, implementable suggestions
- Clear communication
  </constraints>
</agent_configuration>
`;

async function reviewCode(code: string): Promise<string> {
  const result = await query({
    prompt: `
Review this code for bugs, security issues, and improvements:

\`\`\`typescript
${code}
\`\`\`

Provide:
1. Critical issues (must fix)
2. High priority improvements
3. Medium priority suggestions
4. Low priority enhancements
    `,
    options: {
      systemPrompt: codingAgentPrompt,
      maxTokens: 4000,
      model: "claude-sonnet-4.5-20250514"
    }
  });

  return result;
}

// Test it
const testCode = `
function processUser(user: any) {
  const sql = "SELECT * FROM users WHERE id = " + user.id;
  return db.query(sql);
}
`;

reviewCode(testCode).then(console.log);
```

**Python:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

coding_agent_prompt = """
<agent_configuration>
  <metadata>
    <agent_name>Code Review Assistant</agent_name>
    <version>1.0.0</version>
    <pattern>single-agent</pattern>
  </metadata>

  <role>
You are a senior software engineer with 10 years of experience in TypeScript,
Python, and system design. You specialize in code review, identifying bugs,
security issues, and performance problems. You provide constructive feedback
with specific, actionable recommendations.
  </role>

  <core_capabilities>
Primary Capabilities:
- Code analysis and bug detection
- Security vulnerability identification
- Performance optimization recommendations
- Best practices enforcement
- Refactoring suggestions

Analysis Focus:
1. Correctness: Logic errors, edge cases, type safety
2. Security: Injection attacks, data validation, auth issues
3. Performance: Complexity, inefficient algorithms, memory leaks
4. Maintainability: Code clarity, documentation, testing
  </core_capabilities>

  <quality_standards>
Every code review must:
- Identify all critical bugs and security issues
- Provide specific line numbers for issues
- Suggest concrete fixes with code examples
- Prioritize issues by severity (Critical/High/Medium/Low)

Before finalizing review:
1. Check all code paths analyzed
2. Verify recommendations are actionable
3. Ensure explanations are clear
  </quality_standards>

  <constraints>
Must NOT:
- Suggest changes without explanation
- Make assumptions about requirements
- Recommend over-engineering
- Ignore security concerns

Focus on:
- Production-ready code quality
- Practical, implementable suggestions
- Clear communication
  </constraints>
</agent_configuration>
"""

async def review_code(code: str) -> str:
    result = None
    async for message in query(
        prompt=f"""
Review this code for bugs, security issues, and improvements:

```python
{code}
```

Provide:
1. Critical issues (must fix)
2. High priority improvements
3. Medium priority suggestions
4. Low priority enhancements
        """,
        options=ClaudeAgentOptions(
            system_prompt=coding_agent_prompt,
            max_tokens=4000,
            model="claude-sonnet-4.5-20250514"
        )
    ):
        result = message
    return result

# Test it
test_code = """
def process_user(user):
    sql = "SELECT * FROM users WHERE id = " + str(user['id'])
    return db.query(sql)
"""

import asyncio
result = asyncio.run(review_code(test_code))
print(result)
```

### Step 3: Run and Test

```bash
# TypeScript
npx tsx my-coding-agent.ts

# Python
python my-coding-agent.py
```

You should see a detailed code review identifying the SQL injection vulnerability!

### Step 4: Add Tools (Optional)

Let's add a tool to read files from the codebase:

**TypeScript:**
```typescript
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { readFile } from "fs/promises";

const readCodeFileTool = tool({
  name: "read_code_file",
  description: "Read a code file from the project. Use when you need to review actual project files.",
  parameters: {
    type: "object",
    properties: {
      filePath: {
        type: "string",
        description: "Path to the file to read (e.g., 'src/utils/validator.ts')"
      }
    },
    required: ["filePath"]
  },
  execute: async ({ filePath }) => {
    // Security: restrict to src/ directory
    if (!filePath.startsWith("src/")) {
      throw new Error("Can only read files in src/ directory");
    }

    const content = await readFile(filePath, "utf-8");
    return { filePath, content, lines: content.split("\n").length };
  }
});

// Add to query options
const result = await query({
  prompt: "Review the validator.ts file for issues",
  options: {
    systemPrompt: codingAgentPrompt,
    tools: [readCodeFileTool],
    maxTokens: 4000
  }
});
```

### Step 5: Add Validation

Add self-validation to ensure quality:

```typescript
async function reviewCodeWithValidation(code: string): Promise<string> {
  let review = await reviewCode(code);

  // Self-validation
  const validation = await query({
    prompt: `
Validate this code review:

${review}

Check:
1. Are all critical security issues identified?
2. Are recommendations specific and actionable?
3. Is severity classification appropriate?
4. Are code examples provided for fixes?

If ANY check fails, provide an improved review.
    `,
    options: {
      systemPrompt: codingAgentPrompt,
      maxTokens: 2000
    }
  });

  // If validation suggests improvements, use them
  if (validation.includes("IMPROVED REVIEW:")) {
    review = validation.split("IMPROVED REVIEW:")[1];
  }

  return review;
}
```

### Step 6: Add Observability

Add logging for production:

```typescript
interface LogEntry {
  timestamp: string;
  event: string;
  details: any;
}

function log(event: string, details: any): void {
  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    event,
    details
  };
  console.log(JSON.stringify(entry));
}

async function reviewCodeProduction(code: string): Promise<string> {
  log("review_start", { codeLength: code.length });

  try {
    const review = await reviewCodeWithValidation(code);
    log("review_complete", { reviewLength: review.length });
    return review;
  } catch (error) {
    log("review_error", { error: error.message });
    throw error;
  }
}
```

---

## Next Steps

### Learn More

1. **Explore Patterns**: Read [Architecture Patterns](../framework/patterns.md)
2. **Add Components**: Check [Modular Components](../framework/components.md)
3. **See Examples**: Browse [Examples](../examples/)
4. **Production Deployment**: Read [Production Guide](production-deployment.md)

### Improve Your Agent

1. **Add More Tools**: File search, code execution, testing
2. **Implement Caching**: Use prompt caching for system prompt
3. **Add Error Handling**: Implement retry logic and fallbacks
4. **Create Tests**: Write comprehensive test suite
5. **Monitor Performance**: Track token usage and latency

### Production Checklist

Before deploying to production:

- [ ] Self-validation implemented
- [ ] Error handling comprehensive
- [ ] Security checklist passed
- [ ] Observability in place
- [ ] Tests written and passing
- [ ] Documentation complete
- [ ] Performance optimized
- [ ] Cost budget established

---

## Common Issues

### Issue: "API Key not found"

**Solution:**
```bash
# Verify key is set
echo $ANTHROPIC_API_KEY  # Linux/Mac
echo %ANTHROPIC_API_KEY%  # Windows

# Set it if missing
export ANTHROPIC_API_KEY='your-key-here'
```

### Issue: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
npm install  # TypeScript
pip install -r requirements.txt  # Python
```

### Issue: "Rate limit exceeded"

**Solution:**
```typescript
// Add retry logic with exponential backoff
async function queryWithRetry(prompt, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await query({ prompt, options });
    } catch (error) {
      if (error.message.includes("rate_limit") && i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);  // 1s, 2s, 4s
        continue;
      }
      throw error;
    }
  }
}
```

---

## Resources

### Official Documentation
- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)
- [Building Effective Agents](https://anthropic.com/research/building-effective-agents)
- [Prompt Engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering)

### Framework Resources
- [Master Prompt](../framework/master-prompt.md)
- [Decision Tree](../framework/decision-tree.md)
- [Patterns](../framework/patterns.md)
- [Components](../framework/components.md)

### Community
- [GitHub Issues](https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues)
- [Discussions](https://github.com/ehanc69/ShadowTag-v2-fastapi-services/discussions)

---

**Congratulations!** You've built your first production-ready Claude agent. Continue learning by exploring more advanced patterns and components.
