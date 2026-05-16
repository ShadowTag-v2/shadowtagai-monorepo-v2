# ShadowTag OS

**Unified orchestration package integrating the PNKLN stack with Google external repositories.**

## Architecture

```
packages/shadowtag_os/
├── core/               # CoreOrchestrator — central dispatch
│   └── orchestrator.py # Routes operations to subsystems
├── kernels/            # Kernel chain (from src/kernels/)
├── judges/             # Judge #6 HITL enforcement (from src/judges/)
├── gates/              # Quality gates (from src/gates/)
├── skills_bridge/      # Integration with google/skills
│   └── bridge.py       # SKILL.md discovery + invocation
├── zx_runner/          # Shell automation via google/zx
│   └── runner.py       # Python ↔ zx adapter
└── a2ui_adapter/       # Declarative UI via google/A2UI
    └── adapter.py      # Component tree rendering
```

## External Repositories

| Repo | Purpose | Path |
|------|---------|------|
| [google/skills](https://github.com/google/skills) | Agent skill definitions | `external_repos/skills/` |
| [google/zx](https://github.com/google/zx) | Shell scripting automation | `external_repos/zx/` |
| [google/a2ui](https://github.com/google/a2ui) | Agent-to-User Interface | `external_repos/A2UI/` |

## Usage

```python
from shadowtag_os.core import CoreOrchestrator
from shadowtag_os.skills_bridge import SkillsBridge
from shadowtag_os.zx_runner import ZxRunner
from shadowtag_os.a2ui_adapter import A2UIAdapter

# Wire up subsystems
orchestrator = CoreOrchestrator(
    skills_bridge=SkillsBridge(),
    zx_runner=ZxRunner(),
    a2ui_adapter=A2UIAdapter(),
)

# Dispatch an operation
result = await orchestrator.dispatch(
    OperationContext(
        operation_id="op-001",
        op_type=OperationType.SKILL_INVOKE,
        payload={"skill_name": "deep-research", "args": {...}},
    )
)
```

## Development

```bash
# Install in dev mode
pip install -e "packages/shadowtag_os[dev]"

# Run lint
ruff check packages/shadowtag_os/

# Run tests
pytest packages/shadowtag_os/tests/
```
