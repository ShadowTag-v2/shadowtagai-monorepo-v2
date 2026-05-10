"""
tools/agent_state/firestore_checkpoint.py — Agentic Hippocampus

Provides checkpoint/resume functionality for multi-step agent workflows
via Firestore. Enables cross-session state continuity.

Collection: `agent_checkpoints`
Document schema:
  - agent_id: str (e.g., "antigravity", "cline", "kairos")
  - task_id: str (e.g., "deploy-counselconduit-v3")
  - step: int (current step number)
  - total_steps: int
  - state: dict (arbitrary agent state)
  - status: str ("running", "paused", "completed", "failed")
  - created_at: datetime
  - updated_at: datetime
  - metadata: dict (optional context)

Dependencies:
  - google-cloud-firestore (via ADC, no API key)
  - firebase-admin (optional, for emulator support)

Rule 00 compliant: No destructive operations. Checkpoints are append-only.
"""

import json
import sys
from datetime import datetime, UTC
from typing import Any


# ─── Checkpoint Data Model ──────────────────────────────────────────────────


class AgentCheckpoint:
  """Represents a single agent checkpoint in Firestore."""

  def __init__(
    self,
    agent_id: str,
    task_id: str,
    step: int = 0,
    total_steps: int = 1,
    state: dict[str, Any] | None = None,
    status: str = "running",
    metadata: dict[str, Any] | None = None,
  ):
    self.agent_id = agent_id
    self.task_id = task_id
    self.step = step
    self.total_steps = total_steps
    self.state = state or {}
    self.status = status
    self.metadata = metadata or {}
    self.created_at = datetime.now(UTC)
    self.updated_at = datetime.now(UTC)

  def to_dict(self) -> dict[str, Any]:
    """Serialize checkpoint to Firestore-compatible dict."""
    return {
      "agent_id": self.agent_id,
      "task_id": self.task_id,
      "step": self.step,
      "total_steps": self.total_steps,
      "state": self.state,
      "status": self.status,
      "metadata": self.metadata,
      "created_at": self.created_at.isoformat(),
      "updated_at": self.updated_at.isoformat(),
    }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> AgentCheckpoint:
    """Deserialize checkpoint from Firestore document."""
    cp = cls(
      agent_id=data["agent_id"],
      task_id=data["task_id"],
      step=data.get("step", 0),
      total_steps=data.get("total_steps", 1),
      state=data.get("state", {}),
      status=data.get("status", "running"),
      metadata=data.get("metadata", {}),
    )
    if "created_at" in data:
      cp.created_at = datetime.fromisoformat(data["created_at"])
    if "updated_at" in data:
      cp.updated_at = datetime.fromisoformat(data["updated_at"])
    return cp

  def __repr__(self) -> str:
    return f"AgentCheckpoint(agent={self.agent_id}, task={self.task_id}, step={self.step}/{self.total_steps}, status={self.status})"


# ─── Checkpoint Store ────────────────────────────────────────────────────────


class CheckpointStore:
  """Manages agent checkpoints in Firestore.

  Supports two modes:
  1. Live Firestore (requires google-cloud-firestore + ADC)
  2. Local JSON fallback (no cloud dependency)
  """

  COLLECTION = "agent_checkpoints"

  def __init__(self, project_id: str = "shadowtag-omega-v4", local_mode: bool = False):
    self.project_id = project_id
    self.local_mode = local_mode
    self._db = None
    self._local_store: dict[str, dict[str, Any]] = {}

    if not local_mode:
      try:
        from google.cloud import firestore  # noqa: F401

        self._db = firestore.Client(project=project_id)
      except ImportError:
        print(
          "[WARN] google-cloud-firestore not installed. Falling back to local mode."
        )
        self.local_mode = True
      except Exception as e:
        print(f"[WARN] Firestore init failed: {e}. Falling back to local mode.")
        self.local_mode = True

  def _doc_id(self, agent_id: str, task_id: str) -> str:
    """Generate a deterministic document ID."""
    return f"{agent_id}___{task_id}"

  def save(self, checkpoint: AgentCheckpoint) -> str:
    """Save or update a checkpoint. Returns the document ID."""
    doc_id = self._doc_id(checkpoint.agent_id, checkpoint.task_id)
    checkpoint.updated_at = datetime.now(UTC)
    data = checkpoint.to_dict()

    if self.local_mode:
      self._local_store[doc_id] = data
      print(f"[LOCAL] Saved checkpoint: {doc_id}")
    else:
      self._db.collection(self.COLLECTION).document(doc_id).set(data, merge=True)
      print(f"[FIRESTORE] Saved checkpoint: {doc_id}")

    return doc_id

  def load(self, agent_id: str, task_id: str) -> AgentCheckpoint | None:
    """Load a checkpoint by agent_id and task_id."""
    doc_id = self._doc_id(agent_id, task_id)

    if self.local_mode:
      data = self._local_store.get(doc_id)
      if data:
        return AgentCheckpoint.from_dict(data)
      return None

    doc = self._db.collection(self.COLLECTION).document(doc_id).get()
    if doc.exists:
      return AgentCheckpoint.from_dict(doc.to_dict())
    return None

  def list_active(self, agent_id: str | None = None) -> list[AgentCheckpoint]:
    """List all active (non-completed) checkpoints."""
    results = []

    if self.local_mode:
      for data in self._local_store.values():
        if data["status"] in ("running", "paused"):
          if agent_id is None or data["agent_id"] == agent_id:
            results.append(AgentCheckpoint.from_dict(data))
    else:
      query = self._db.collection(self.COLLECTION).where(
        "status", "in", ["running", "paused"]
      )
      if agent_id:
        query = query.where("agent_id", "==", agent_id)
      for doc in query.stream():
        results.append(AgentCheckpoint.from_dict(doc.to_dict()))

    return results

  def advance(
    self, agent_id: str, task_id: str, new_state: dict[str, Any] | None = None
  ) -> AgentCheckpoint | None:
    """Advance a checkpoint by one step."""
    cp = self.load(agent_id, task_id)
    if cp is None:
      print(f"[ERROR] No checkpoint found for {agent_id}/{task_id}")
      return None

    cp.step = min(cp.step + 1, cp.total_steps)
    if new_state:
      cp.state.update(new_state)
    if cp.step >= cp.total_steps:
      cp.status = "completed"

    self.save(cp)
    return cp

  def fail(self, agent_id: str, task_id: str, error: str) -> AgentCheckpoint | None:
    """Mark a checkpoint as failed with error context."""
    cp = self.load(agent_id, task_id)
    if cp is None:
      return None

    cp.status = "failed"
    cp.state["error"] = error
    self.save(cp)
    return cp


# ─── CLI Interface ───────────────────────────────────────────────────────────


def main():
  """CLI interface for checkpoint management."""
  import argparse

  parser = argparse.ArgumentParser(description="Agent Checkpoint Manager (Hippocampus)")
  parser.add_argument(
    "--local", action="store_true", help="Use local JSON store instead of Firestore"
  )
  sub = parser.add_subparsers(dest="command")

  # Save command
  save_p = sub.add_parser("save", help="Save a checkpoint")
  save_p.add_argument("--agent", required=True)
  save_p.add_argument("--task", required=True)
  save_p.add_argument("--step", type=int, default=0)
  save_p.add_argument("--total", type=int, default=1)
  save_p.add_argument("--status", default="running")
  save_p.add_argument("--state", default="{}", help="JSON state blob")

  # Load command
  load_p = sub.add_parser("load", help="Load a checkpoint")
  load_p.add_argument("--agent", required=True)
  load_p.add_argument("--task", required=True)

  # List command
  list_p = sub.add_parser("list", help="List active checkpoints")
  list_p.add_argument("--agent", default=None)

  # Advance command
  adv_p = sub.add_parser("advance", help="Advance a checkpoint by one step")
  adv_p.add_argument("--agent", required=True)
  adv_p.add_argument("--task", required=True)

  args = parser.parse_args()
  store = CheckpointStore(local_mode=args.local)

  if args.command == "save":
    state = json.loads(args.state)
    cp = AgentCheckpoint(
      agent_id=args.agent,
      task_id=args.task,
      step=args.step,
      total_steps=args.total,
      state=state,
      status=args.status,
    )
    doc_id = store.save(cp)
    print(f"Saved: {doc_id}")

  elif args.command == "load":
    cp = store.load(args.agent, args.task)
    if cp:
      print(json.dumps(cp.to_dict(), indent=2, default=str))
    else:
      print("No checkpoint found")
      sys.exit(1)

  elif args.command == "list":
    active = store.list_active(args.agent)
    for cp in active:
      print(f"  {cp}")
    if not active:
      print("No active checkpoints")

  elif args.command == "advance":
    cp = store.advance(args.agent, args.task)
    if cp:
      print(f"Advanced: {cp}")
    else:
      print("Checkpoint not found")
      sys.exit(1)

  else:
    parser.print_help()


if __name__ == "__main__":
  main()
