"""
dream_consolidation.py — Monorepo OS v4.0 (The Epistemic Airgap Release)
Fuses 3-Tier Gate + consolidationLock.ts with SpreadingActivationCore # (WanderEngine)
and SafeToAutoRun Read-Only Bash Constraints.
Data Plane: PostgreSQL (until MRR) and Firestore (replacing Redis).
"""
from __future__ import annotations
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

# Serverless Data Plane
# from google.cloud import firestore

# =====================================================================
# STUBS & MOCKS (To prevent NameError/ModuleNotFoundError crashes)
# =====================================================================
class SpreadingActivationCore:
    def __init__(self, db_path, decay_lambda, lateral_inhibition, top_k, conflict_threshold, promotion_threshold):
        pass
    def wander(self, graph, base_activations, seed, steps):
        return []
    def detect_conflicts(self, store, results):
        return []
    def promote_to_memory(self, store, results):
        return []

def generate_memory_views(store, results): pass
def log_consolidation_event(**kwargs): pass

def _build_ki_relation_graph(ki_store: Dict[str, Dict[str, Any]]) -> Any: return {}
def _compute_base_activations(ki_store: Dict[str, Dict[str, Any]]) -> Any: return {}
def _prune_low_confidence(ki_store: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]: return ki_store
def _apply_temporal_decay(ki_store: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]: return ki_store

# =====================================================================
# 1. PID MUTEX (consolidationLock.ts)
# =====================================================================
LOCK_FILE = ".beads/.consolidate-lock"

def try_acquire_consolidation_lock() -> bool:
    """PID-based file lock preventing multi-window race conditions."""
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r') as f:
            pid_str = f.read().strip()
        if pid_str.isdigit():
            try:
                os.kill(int(pid_str), 0)
                return False  # Process is alive, lock held
            except OSError:
                pass  # Process is dead, steal stale lock

    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    return True

def release_consolidation_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# =====================================================================
# 2. COST/VOLUME CONTROL GATING (autoDream.ts)
# =====================================================================
def check_autodream_gates(last_consolidated_at: datetime, transcript_count: int, min_hours: int = 24, min_sessions: int = 5) -> bool:
    """3-Tier execution gate: Time -> Sessions -> Lock"""
    now = datetime.now(timezone.utc)
    hours_since = (now - last_consolidated_at).total_seconds() / 3600

    if hours_since < min_hours:
        print(f"💤 [AutoDream] Time gate not met ({hours_since:.1f}h < {min_hours}h). Yielding.")
        return False

    if transcript_count < min_sessions:
        print(f"💤 [AutoDream] Volume gate not met ({transcript_count} < {min_sessions} sessions). Yielding.")
        return False

    return True

# =====================================================================
# 3. ANTIGRAVITY SECURITY: SafeToAutoRun
# =====================================================================
DESTRUCTIVE_PATTERNS = ["rm ", "sed -i", "mv ", ">", ">>", "chmod ", "chown ", "sudo "]

def enforce_read_only_bash(command: str) -> bool:
    """Hard Read-Only constraint for unattended background Triad runs."""
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern in command:
            print(f"🛑 [SafeToAutoRun] Destructive pattern blocked during dream phase: '{pattern}'")
            return False
    return True

# =====================================================================
# 4. CORE CONSOLIDATION + SPREADING ACTIVATION
# =====================================================================
def dream_consolidation(
    ki_store: Dict[str, Dict[str, Any]],
    current_context: List[str],
    last_consolidated_at: datetime,
    transcript_count: int,
    decay_lambda: float = 0.038,
    confidence_boost: float = 0.18,
    db_connection: str = "postgresql://user:pass@localhost:5432/agnt_memory" # PostgreSQL until MRR
) -> Dict[str, Dict[str, Any]]:

    print("🧠 [Dream Consolidation v4.0] Evaluating AutoDream Gates...")

    if not check_autodream_gates(last_consolidated_at, transcript_count):
        return ki_store

    if not try_acquire_consolidation_lock():
        print("🔒 [ConsolidationLock] Concurrency lock active. Yielding.")
        return ki_store

    try:
        print("🚀 [Dream Consolidation] Gates passed. Initiating SpreadingActivationCore...")

        # Initialize Spreading Activation on PostgreSQL backend
        wander = SpreadingActivationCore(
            db_path=db_connection,
            decay_lambda=decay_lambda,
            lateral_inhibition=0.32,
            top_k=18,
            conflict_threshold=0.72,
            promotion_threshold=0.88
        )

        ki_graph = _build_ki_relation_graph(ki_store)
        base_activations = _compute_base_activations(ki_store)

        activated_results = []
        for seed_ki in current_context:
            results = wander.wander(ki_graph, base_activations, seed_ki, steps=3)
            activated_results.extend(results)

        for result in activated_results:
            ki = ki_store.get(getattr(result, 'ki_id', ''))
            if ki and getattr(result, "activation", 0) > 0.70:
                current_conf = float(ki.get("confidence", 0.5))
                ki["confidence"] = min(1.0, current_conf + confidence_boost)
                ki["last_activated"] = datetime.now(timezone.utc).isoformat()
                ki["activation_score"] = getattr(result, "activation", 0)
                ki["related_from_wander"] = getattr(result, "related_kis", [])

        conflicts = wander.detect_conflicts(ki_store, activated_results)
        if conflicts:
            print(f"⚠️  Detected {len(conflicts)} memory conflicts.")

        promoted = wander.promote_to_memory(ki_store, activated_results)
        if promoted:
            print(f"🚀 Promoted {len(promoted)} KIs to Core Memory atoms.")

        pruned = _prune_low_confidence(ki_store)
        final_store = _apply_temporal_decay(pruned)

        generate_memory_views(final_store, activated_results)
        log_consolidation_event(
            num_kis=len(final_store),
            activated_count=len(activated_results),
            high_activation_count=sum(1 for r in activated_results if getattr(r, 'activation', 0) > 0.75),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        print(f"✅ Consolidation complete → {len(final_store)} KIs active.")
        return final_store

    finally:
        release_consolidation_lock()
