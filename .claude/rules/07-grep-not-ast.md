# Rule 07: grep Is Not an AST

You rename a function. The agent greps for callers, updates 8 files, misses 4 that use dynamic imports, re-exports, or string references. The code compiles in the files it touched. Of course, it breaks everywhere else.

The reason is that Claude Code has no semantic code understanding. GrepTool is raw text pattern matching. It can't distinguish a function call from a comment, or differentiate between identically named imports from different modules.

## The Override
On any rename or signature change, you MUST search separately for:
1. Direct calls and references
2. Type-level references (interfaces, generics)
3. String literals containing the name
4. Dynamic imports and require() calls
5. Re-exports and barrel file entries
6. Test files and mocks

Assume grep missed something. Verify manually or eat the regression.

Do not assume a single grep caught everything. Ever.
