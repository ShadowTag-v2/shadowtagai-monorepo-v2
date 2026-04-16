# CLAUDE.md
## Developer Instructions
- A developer who reads every generated file before accepting it
- Auth that was designed before it was prompted
- DB schemas that considered relationships, indexes, and migrations
- Error handling that actually does something
- At least one test for the critical paths

## Orthogonal Edits Rule
- STRICT MINIMAL EDIT: You must avoid editing unrelated lines or helper files to mask context. Prevent polluting the attention mechanism. Do not add hallucinated dependencies to justify changes made in previous turns. Keep the context window focused on the actual task instead of an ever-expanding web of side effects.
