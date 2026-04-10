# agents/bar_exam_protocol.py
from src.agents.legal_whiteboard import whiteboard


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
            # Logic: All requirements for this level must be met
            # Special handling for _accuracy suffix which applies to patterns
            met_requirements = []
            for key, val in reqs.items():
                if key.endswith("pattern_accuracy"):
                    # Check if any pattern meets the accuracy threshold
                    patterns = state.get("patterns", [])
                    has_accurate = any(p.get("accuracy", 0) >= val for p in patterns)
                    met_requirements.append(has_accurate)
                else:
                    # Direct comparison
                    current_val = state.get(key.replace("min_", ""), 0)
                    # Note: "min_knowledge" maps to len(knowledge) effectively,
                    # but the whiteboard state stores lists.
                    # We need to adapt the check to count list items if key implies a count.
                    if key == "min_knowledge":
                        current_val = len(state.get("knowledge", []))
                    elif key == "min_patterns":
                        current_val = len(state.get("patterns", []))
                    elif key == "min_optimizations":
                        current_val = len(state.get("optimizations", []))
                    elif key == "applied_optimizations":
                        # Count where applied=True
                        opts = state.get("optimizations", [])
                        current_val = sum(1 for o in opts if o.get("applied"))
                    elif key == "spawned_agents":
                        current_val = len(state.get("spawned_agents", []))

                    met_requirements.append(current_val >= val)

            if all(met_requirements):
                state["level"] = level
                whiteboard._save()
                print(f"🎓 Bar Exam passed – Agent promoted to Level {level}")
                return level
        return current

    @staticmethod
    def can_spawn_new_agent() -> bool:
        return whiteboard.state["level"] >= 4

    @staticmethod
    def can_orchestrate_swarm() -> bool:
        return whiteboard.state["level"] >= 5


# Auto-evaluate on import (so every task can trigger promotion)
BarExamProtocol.evaluate()
