Refactor the targeted file or feature into a cleaner modular structure.

Rules:
- preserve behavior
- split by concern, not by arbitrary line count
- prefer components under 150 lines
- extract stateful logic into custom hooks
- extract business logic into services or actions
- keep atoms, molecules, sections, and features distinct
- avoid unnecessary file explosion
- after refactor, run or describe lint, typecheck, and test verification

Required output:
1. current concerns mixed in the file
2. proposed target tree
3. ordered refactor steps
4. final code changes
5. verification summary
