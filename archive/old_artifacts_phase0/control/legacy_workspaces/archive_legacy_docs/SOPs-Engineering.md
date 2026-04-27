### Engineering SOPs

**Principles**
- Fail fast on invalid input with clear exceptions.
- Keep functions < 40 lines; favor guard clauses and early returns.
- Use explicit type hints and docstrings for public functions/classes.
- Prefer simple, robust solutions over cleverness.

**Naming & API design**
- Descriptive names; avoid abbreviations; verbs for functions, nouns for variables.
- Small, cohesive modules; minimize hidden coupling.

**Errors & Logging**
- Raise specific exceptions; never silently swallow errors.
- Log actionable context; never log secrets or PII.

**Testing**
- Pytest for unit and behavior tests; cover edge cases.
- Tests define expected errors for invalid input.

**Style & Tooling**
- ruff and black enforce style; mypy enforces types; all run in CI.
- Pre-commit hooks required for contributors.

**Security & IP**
- Secrets via env/secure stores; principle of least privilege.
- Respect licenses/DMCA; avoid proprietary scraping.
