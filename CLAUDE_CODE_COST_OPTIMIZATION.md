# Claude Code Cost Optimization Guide

**Save 90%+ on Claude Code costs by following these 16 battle-tested habits.**

From $400/week to $15/week with simple workflow changes and automation.

---

## Quick Wins (Implement Today)

### 1. Use Haiku for 80% of Your Work
**Cost Savings: $0.80 per session**

```bash
# Set Haiku as your default model
claude --model haiku
```

**When to use Haiku:**
- Bug fixes
- File reads
- Simple edits
- Code formatting
- Basic refactoring

**When to use Sonnet:**
- Complex architectural changes
- Multi-file refactoring
- Advanced debugging
- System design

**Why:** Haiku costs 5x less than Sonnet and handles routine tasks just as fast.

---

### 2. Search First, Read Second
**Cost Savings: 100x cheaper (50MB log: $0.05 vs $5)**

```bash
# ❌ Expensive
"read error.log"

# ✅ Cheap
"search for ERROR in error.log"
"grep 'exception' in logs/"
```

**Best Practices:**
- Use `grep` or `search` for large files
- Only read files after finding what you need
- Filter before loading

---

### 3. Read Files in Chunks
**Cost Savings: 100x cheaper (10MB file: $0.10 vs $10)**

```bash
# ❌ Expensive
"read database.ts"

# ✅ Cheap
"read lines 1-100 from database.ts"
"read lines 100-200 from database.ts"
```

**Pro Tips:**
- Start with first 50-100 lines
- Jump to specific line ranges
- Use line numbers from search results

---

### 4. Run Tasks in Parallel
**Time & Cost Savings: 3x faster, same cost**

```bash
# ❌ Slow (sequential)
"read auth.ts, then read db.ts, then read api.ts"

# ✅ Fast (parallel)
"run these in parallel: read auth.ts, read db.ts, read api.ts"
```

**When to parallelize:**
- Independent file reads
- Multiple searches
- Separate lint/test runs
- Unrelated tasks

---

### 5. Use the Explore Agent for Unfamiliar Code
**Cost Savings: $5 vs $20-30 in trial-and-error**

```bash
# ❌ Expensive trial-and-error
"search for auth"
"search for login"
"search for authentication"
"read auth.ts"
"read login.ts"

# ✅ One-shot exploration
"explore this codebase for authentication logic"
```

**Best for:**
- New codebases
- Finding patterns
- Understanding architecture
- Locating features

---

### 6. Plan Major Changes First
**Cost Savings: $0.50 to plan, saves $50 in rework**

```bash
# ❌ Expensive (dive in blindly)
"refactor the authentication system"

# ✅ Cheap (plan first)
"create a plan for refactoring the authentication system"
# Review the plan
"implement step 1 of the plan"
```

**When to plan:**
- Changing 5+ files
- Refactoring systems
- Adding major features
- Database migrations

**Most people skip this. Don't.**

---

### 7. Turn On Budget Alerts
**Never overspend again**

Use the setup script (see below) to get automatic warnings at:
- 70% of monthly budget
- 90% of monthly budget

---

### 8. Limit Search Results
**Cost Savings: $0.50 vs $5 for full search**

```bash
# ❌ Expensive
"find all matches for TODO"

# ✅ Cheap
"find first 50 matches for TODO"
"show top 20 results for FIXME"
```

**Reality:** You only need the first few results anyway.

---

### 9. Be Specific in Requests
**Cost Savings: 3x fewer back-and-forth rounds**

```bash
# ❌ Vague (3+ rounds)
"help me fix this"
"there's a bug"
"it's not working"

# ✅ Specific (1 round)
"fix the login bug in auth.ts line 45"
"the API returns 500 on POST /users"
"TypeError in database.ts:234"
```

**Include:**
- File name
- Line number (if known)
- Error message
- Expected vs actual behavior

---

### 10. Use Path Shortcuts
**Faster = Cheaper**

Setup script creates shortcuts automatically:

```bash
# Before
/src/lib/utilities/helpers/index.ts

# After (with shortcuts)
utils
```

**Common shortcuts:**
- `utils` → `/src/lib/utilities/helpers/index.ts`
- `components` → `/src/components`
- `config` → `/src/config`
- `tests` → `/tests`

---

### 11. Create Task Checklists at the Start
**Savings: Finish 40% faster**

```bash
# ✅ Start with this
"create a todo list for migrating from Express to FastAPI"

# Then work through it
"implement task 1"
"implement task 2"
```

**Benefits:**
- No forgotten steps
- No re-reading files
- Clear progress tracking
- Prevents rework

---

### 12. Read Smart: Load Only What You Need
**Cost Savings: Pennies vs dollars**

```bash
# ❌ Load everything
"read database.ts"  # 5,000 lines = $$$

# ✅ Load what you need
"read lines 100-200 from database.ts"  # 100 lines = $
```

**Strategies:**
- Search first to find line numbers
- Read in 100-line chunks
- Jump to specific functions
- Use grep to preview

---

### 13. Don't Ask the Same Question Twice
**Session memory is free, re-running costs money**

```bash
# ❌ Expensive
"search for errors"
# ... later ...
"search for errors again"

# ✅ Free
"use the errors we found earlier"
"check the previous search results"
```

**Remember:** Claude remembers the session context.

---

### 14. Let the System Filter First
**Cost Savings: 95% cheaper**

```bash
# ❌ Expensive
"show all data from logs"
# Then you manually filter

# ✅ Cheap
"show only ERROR lines from logs"
"filter for status=500 in access.log"
```

**Get 5 rows with errors instead of loading 10,000 rows.**

---

### 15. Make These Habits Automatic
**Install once, save forever**

Use the setup script included in this repo (see below).

**What it does:**
- Sets up path shortcuts
- Configures budget alerts
- Creates command aliases
- Optimizes default settings

---

### 16. Engineer Prompts Strategically
**Cost Savings: 50-90% through targeted prompts**

```bash
# ❌ Expensive (vague, wrong model)
claude --model sonnet "help me fix this auth issue"

# ✅ Cheap (specific, right model)
claude --model haiku "fix TypeError in auth.ts:234 - user.token is undefined. Add null check before accessing user.token."
```

**Prompt Engineering Strategies:**
- Match model to task complexity (Haiku for routine, Sonnet for complex)
- Provide specific file:line references
- Define exact output format needed
- Set realistic confidence targets
- Use templates for repetitive tasks

**Advanced Techniques:**
- Two-stage prompts: plan with Haiku, implement with Sonnet
- Scope reduction: analyze only relevant sections
- Context prioritization: include only what's needed
- Incremental refinement: start small, expand if needed

**Real Example - Gemini Ingestion Layer:**
- Before: Generic "analyze this system" → 7 rounds → $15
- After: Targeted 6-dimension prompt → 1 round → $2
- **Savings: 87%**

**Deep Dive:**
See [PROMPT_ENGINEERING_COST_OPTIMIZATION.md](./PROMPT_ENGINEERING_COST_OPTIMIZATION.md) for:
- Model-specific prompt design
- Case study: Gemini Ingestion Layer analysis
- Prompt templates for common tasks
- Measuring prompt efficiency

**Key Insight:**
Strategic prompt engineering is the "force multiplier" that pushes savings from 90% to 95%+.

---

## Setup Script

Run once to automate these optimizations:

```bash
chmod +x setup-cost-optimization.sh
./setup-cost-optimization.sh
```

---

## Cost Comparison Examples

| Task | Expensive Way | Cheap Way | Savings |
|------|---------------|-----------|---------|
| Search 50MB log | Read entire file ($5) | Search for pattern ($0.05) | **100x** |
| Read 10MB file | Read all ($10) | Read 100 lines ($0.10) | **100x** |
| Find errors | Trial & error ($20-30) | Explore agent ($5) | **4-6x** |
| Refactor 5+ files | No plan ($50 wasted) | Plan first ($0.50) | **100x** |
| Search results | All 10k matches ($5) | First 50 ($0.50) | **10x** |
| Load data | All rows ($5) | Filtered rows ($0.25) | **20x** |
| System analysis | Generic prompt, 7 rounds ($15) | Targeted prompt, 1 round ($2) | **7.5x** |
| Bug fix | Vague on Sonnet ($0.50) | Specific on Haiku ($0.10) | **5x** |

---

## Quick Reference Card

**Before every task, ask yourself:**

1. ✅ Can I use Haiku instead of Sonnet?
2. ✅ Can I search instead of read?
3. ✅ Can I read a chunk instead of the whole file?
4. ✅ Can I run these tasks in parallel?
5. ✅ Should I use the explore agent?
6. ✅ Should I create a plan first?
7. ✅ Can I limit search results?
8. ✅ Am I being specific enough?
9. ✅ Can I use a path shortcut?
10. ✅ Should I create a checklist?
11. ✅ Can I load less data?
12. ✅ Can I use previous results?
13. ✅ Can I filter first?
14. ✅ Is my prompt optimized for this model and task?

---

## Real Impact

**Before:** $400/week
**After:** $15/week
**Savings:** $385/week = $1,540/month = $18,480/year

**Time saved:** ~40% faster completion on multi-step tasks

---

## Next Steps

1. Read this guide
2. Run the setup script
3. Print the Quick Reference Card
4. Practice with your next 5 tasks
5. Watch your costs drop

**Questions?** Check the setup script comments for details.

**Track your savings:** Monitor your Claude Code usage dashboard.
