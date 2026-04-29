# Tool Discipline
<rules>
  - Use `GlobTool` BEFORE assuming a file doesn't exist.
  - Use `ViewTool` to read the file BEFORE writing to it with `EditTool`.
  - Never use `ReplaceTool` for multi-line logic changes; rewrite the whole file via `EditTool` if complexity exceeds 5 lines.
  - If `BashTool` returns exit code > 0, YOU MUST FIX IT before responding to the user.
</rules>
