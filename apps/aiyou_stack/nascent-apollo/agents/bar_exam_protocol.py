# agents/bar_exam_protocol.py
import os
import sys

# Ensure we can import from local agents package
sys.path.append(os.getcwd())

from agents.legal_whiteboard import whiteboard


class BarExamProtocol:
    """Never resting, ever vesting – qualification engine."""

    LEVEL_REQUIREMENTS = {
        0: {"min_knowledge": 0},
        1: {"min_patterns": 10, "pattern_accuracy": 0.88},
        2: {"min_optimizations": 5, "avg_roi_projection": 3.0},
        3: {"applied_optimizations": 3, "self_improvement_cycles": 2},
        4: {"spawned_agents": 1},
        5: {"swarm_orchestration_demo": True},
    }

    @staticmethod
    def evaluate() -> int:
        state = whiteboard.state
        current = state["level"]

        for level, reqs in BarExamProtocol.LEVEL_REQUIREMENTS.items():
            if level <= current:
                continue

            # Check requirements
            passed = True
            for key, val in reqs.items():
                if key == "pattern_accuracy":
                    # Check if any pattern meets accuracy
                    if not any(p.get("accuracy", 0) >= val for p in state.get("patterns", [])):
                        passed = False
                        break
                elif key == "avg_roi_projection":
                    # Calculate avg
                    opts = state.get("optimizations", [])
                    if not opts:
                        passed = False
                        break
                    avg = sum(o.get("projected_roi", 0) for o in opts) / len(opts)
                    if avg < val:
                        passed = False
                        break
                elif key == "swarm_orchestration_demo":
                    if not state.get("swarm_orchestration_demo", False):
                        passed = False
                        break
                else:
                    # Simple count check (min_knowledge, min_patterns, etc)
                    # Mapping key names to state keys crudely if needed, but assuming direct match for simplicity or mapping logic
                    # The prompt implied simple counts. Let's map strict keys:
                    state_key_map = {
                        "min_knowledge": "knowledge",
                        "min_patterns": "patterns",
                        "min_optimizations": "optimizations",
                        "applied_optimizations": "optimizations",  # logic diff
                        "self_improvement_cycles": "self_improvements",
                        "spawned_agents": "spawned_agents",
                    }

                    real_key = state_key_map.get(key)
                    if real_key:
                        count = len(state.get(real_key, []))
                        # Special handling for applied
                        if key == "applied_optimizations":
                            count = sum(
                                1 for o in state.get("optimizations", []) if o.get("applied")
                            )

                        if count < val:
                            passed = False
                            break

            if passed:
                state["level"] = level
                whiteboard._save()
                print(f"Bar Exam passed – Agent promoted to Level {level}")
                return level

        return current

    @staticmethod
    def can_spawn_new_agent() -> bool:
        return whiteboard.state["level"] >= 4

    @staticmethod
    def can_orchestrate_swarm() -> bool:
        return whiteboard.state["level"] >= 5


# Auto-evaluate on import (so every task can trigger promotion)
try:
    BarExamProtocol.evaluate()
except Exception as e:
    print(f"Bar Exam Init Check Skipped: {e}")
