# GEMINI COMMAND PROTOCOL (The "Whiteboard" Method)

## The Problem: Why it Crashes
Gemini Code Assist (The Infantry) crashes when you overload it with "General" context.
- **Bad Prompt:** "Refactor the entire repo to use the new architecture." (Context Overflow -> Crash)
- **Bad context:** Having 50 files open in VS Code.

## The Solution: The Whiteboard
Antigravity (The General) writes the orders. Gemini Code Assist (The Infantry) executes the specific file.

### Procedure
1. **Antigravity Writes:** I create a file called `.gemini/orders.md`.
2. **You Point:** You open `.gemini/orders.md` and type in the chat: "Execute these orders."
3. **Gemini Executes:** The agent reads the concise instructions and changes the *specific* files mentioned.

### Example Order (I will generate this for you)
```markdown
# TASK: Fix Lint Errors in main.py
1. Open `apps/server/main.py`.
2. Fix the missing import on line 10.
3. Add a docstring to the `startup` function.
4. Do NOT touch any other file.
```

## How to Test It
I will generate a `.gemini/orders.md` file now to fix a small issue. You will then ask your local Code Assist to "Run the orders".
