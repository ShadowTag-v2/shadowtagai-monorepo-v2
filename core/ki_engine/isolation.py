# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
"""
Per-Agent Isolation — Item 11: Multi-agent KI isolation with shared namespace.

Enables multiple agents to maintain private KI stores while
sharing explicitly designated KIs.

Structure:
  ki_dir/
  ├── config.yaml          ← isolation: per-agent
  ├── agents/
  │   ├── antigravity/     ← Private store
  │   ├── claude/          ← Private store
  │   └── cursor/          ← Private store
  └── shared/              ← Explicitly shared KIs
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IsolationConfig:
    """Configuration for per-agent isolation."""

    mode: str = "shared"  # "shared" or "per-agent"
    agents: list[str] = field(default_factory=list)
    default_agent: str = "antigravity"


def load_isolation_config(ki_dir: Path) -> IsolationConfig:
    """Load isolation config from ki_dir/isolation.json."""
    config_path = ki_dir / "isolation.json"
    if not config_path.exists():
        return IsolationConfig()

    with open(config_path) as f:
        d = json.load(f)

    return IsolationConfig(
        mode=d.get("mode", "shared"),
        agents=d.get("agents", []),
        default_agent=d.get("default_agent", "antigravity"),
    )


def save_isolation_config(ki_dir: Path, config: IsolationConfig) -> None:
    """Save isolation config."""
    config_path = ki_dir / "isolation.json"
    with open(config_path, "w") as f:
        json.dump(
            {
                "mode": config.mode,
                "agents": config.agents,
                "default_agent": config.default_agent,
            },
            f,
            indent=2,
        )
        f.write("\n")


def init_isolated(ki_dir: Path, agents: list[str]) -> IsolationConfig:
    """Initialize per-agent isolation."""
    config = IsolationConfig(mode="per-agent", agents=agents)

    # Create agent directories
    for agent in agents:
        agent_dir = ki_dir / "agents" / agent
        agent_dir.mkdir(parents=True, exist_ok=True)

    # Create shared directory
    shared_dir = ki_dir / "shared"
    shared_dir.mkdir(parents=True, exist_ok=True)

    save_isolation_config(ki_dir, config)
    return config


def resolve_agent_dir(ki_dir: Path, agent_id: str) -> Path:
    """Resolve the KI directory for a specific agent."""
    config = load_isolation_config(ki_dir)
    if config.mode == "per-agent":
        return ki_dir / "agents" / agent_id
    return ki_dir  # Shared mode — everyone uses same dir


def shared_dir(ki_dir: Path) -> Path:
    """Get the shared KI directory."""
    return ki_dir / "shared"


def share_ki(
    ki_dir: Path,
    agent_id: str,
    ki_name: str,
) -> bool:
    """Copy a KI from agent store to shared store.

    Args:
        ki_dir: Root KI directory.
        agent_id: Source agent ID.
        ki_name: Name of the KI to share.

    Returns:
        True if shared successfully.
    """
    source = ki_dir / "agents" / agent_id / ki_name
    target = ki_dir / "shared" / ki_name

    if not source.exists():
        return False

    if target.exists():
        shutil.rmtree(target)

    shutil.copytree(source, target)
    return True


def unshare_ki(ki_dir: Path, ki_name: str) -> bool:
    """Remove a KI from the shared store."""
    target = ki_dir / "shared" / ki_name
    if not target.exists():
        return False

    shutil.rmtree(target)
    return True


def list_agent_kis(ki_dir: Path, agent_id: str) -> list[str]:
    """List KI names for a specific agent."""
    agent_dir = resolve_agent_dir(ki_dir, agent_id)
    if not agent_dir.exists():
        return []
    return [d.name for d in sorted(agent_dir.iterdir()) if d.is_dir() and (d / "metadata.json").exists()]


def list_shared_kis(ki_dir: Path) -> list[str]:
    """List KI names in the shared store."""
    sd = shared_dir(ki_dir)
    if not sd.exists():
        return []
    return [d.name for d in sorted(sd.iterdir()) if d.is_dir() and (d / "metadata.json").exists()]
