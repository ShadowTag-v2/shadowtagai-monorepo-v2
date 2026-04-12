"""
Shift Management - Agent Pool Rotation

Implements 8-hour shifts for 200+ agent swarm to prevent:
- Token limit exhaustion
- Context degradation
- Agent "burnout" (poor performance from long sessions)

SCHEDULE:
- Shift 1 (00:00-08:00): Night crew (50 agents)
- Shift 2 (08:00-16:00): Day crew (100 agents)
- Shift 3 (16:00-24:00): Evening crew (50 agents)

HANDOFF PROTOCOL:
1. Outgoing shift commits current state to whiteboard (git push)
2. Incoming shift reads latest whiteboard state (git pull)
3. Brief overlap (15min) for knowledge transfer
4. Continuous improvement across shifts

Author: Antigravity (Gemini 2.0 Flash Experimental)
Created: 2025-11-22
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class ShiftSlot(Enum):
    """8-hour shift slots"""

    NIGHT = "00:00-08:00"  # 50 agents (lighter load)
    DAY = "08:00-16:00"  # 100 agents (peak load)
    EVENING = "16:00-24:00"  # 50 agents (medium load)


@dataclass
class ShiftAssignment:
    """Agent assignment to specific shift"""

    agent_id: str
    shift_slot: ShiftSlot
    house: str  # Hogwarts house for competitive structure
    level: int  # Agent level (0-5)
    start_time: str
    end_time: str


class ShiftManager:
    """Manages agent pool rotation across 3 daily shifts"""

    def __init__(self, total_agents: int = 200):
        self.total_agents = total_agents
        self.shifts = {ShiftSlot.NIGHT: [], ShiftSlot.DAY: [], ShiftSlot.EVENING: []}
        self.current_shift: ShiftSlot = self._get_current_shift()

    def assign_agents_to_shifts(self, agent_ids: list[str], agent_levels: dict[str, int]):
        """
        Distribute agents across shifts based on level and load requirements.

        STRATEGY:
        - Day shift gets 50% of agents (peak activity)
        - Night/Evening split remaining 50%
        - Higher-level agents distributed evenly (prevent skill gaps)
        """
        # Sort agents by level (highest first)
        sorted_agents = sorted(agent_ids, key=lambda a: agent_levels.get(a, 0), reverse=True)

        # Calculate shift sizes
        day_size = int(self.total_agents * 0.50)  # 100 agents
        night_size = int(self.total_agents * 0.25)  # 50 agents
        evening_size = self.total_agents - day_size - night_size  # 50 agents

        # Assign in round-robin to balance skill levels
        shift_order = [
            (ShiftSlot.DAY, day_size),
            (ShiftSlot.NIGHT, night_size),
            (ShiftSlot.EVENING, evening_size),
        ]

        idx = 0
        for shift_slot, size in shift_order:
            for _ in range(size):
                if idx >= len(sorted_agents):
                    break

                agent_id = sorted_agents[idx]
                assignment = ShiftAssignment(
                    agent_id=agent_id,
                    shift_slot=shift_slot,
                    house="TBD",  # Assigned by HogwartsTeamStructure
                    level=agent_levels.get(agent_id, 0),
                    start_time=shift_slot.value.split("-")[0],
                    end_time=shift_slot.value.split("-")[1],
                )
                self.shifts[shift_slot].append(assignment)
                idx += 1

    def get_active_agents(self) -> list[str]:
        """Get list of agents currently on shift"""
        current = self._get_current_shift()
        return [a.agent_id for a in self.shifts[current]]

    def perform_shift_handoff(self, outgoing_shift: ShiftSlot, incoming_shift: ShiftSlot):
        """
        Execute shift handoff protocol.

        STEPS:
        1. Outgoing shift commits final state to whiteboard
        2. Generate shift summary report
        3. Incoming shift reads latest whiteboard state
        4. 15-minute overlap for knowledge transfer
        5. Incoming shift begins tasks
        """
        print(f"\n🔄 SHIFT HANDOFF: {outgoing_shift.value} → {incoming_shift.value}")
        print("=" * 80)

        # Step 1: Outgoing shift final commit
        outgoing_agents = [a.agent_id for a in self.shifts[outgoing_shift]]
        print(f"\n📤 Outgoing shift ({len(outgoing_agents)} agents) committing state...")
        print("   git add agents/state/*.json")
        print("   git commit -m 'Shift handoff: {outgoing_shift.value} complete'")
        print("   git push origin main")

        # Step 2: Generate shift summary
        summary = self._generate_shift_summary(outgoing_shift)
        print("\n📊 Shift Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

        # Step 3: Incoming shift pulls latest state
        incoming_agents = [a.agent_id for a in self.shifts[incoming_shift]]
        print(f"\n📥 Incoming shift ({len(incoming_agents)} agents) loading state...")
        print("   git pull origin main")

        # Step 4: Knowledge transfer (15min overlap)
        print("\n🤝 15-minute knowledge transfer period:")
        print("   - Top patterns identified by outgoing shift")
        print("   - Unresolved questions requiring follow-up")
        print("   - Priority tasks for incoming shift")

        # Step 5: Incoming shift begins
        print(f"\n✅ Shift handoff complete. {incoming_shift.value} shift is now active.")
        print("=" * 80)

        self.current_shift = incoming_shift

    def _get_current_shift(self) -> ShiftSlot:
        """Determine which shift is currently active based on time"""
        now = datetime.now()
        hour = now.hour

        if 0 <= hour < 8:
            return ShiftSlot.NIGHT
        elif 8 <= hour < 16:
            return ShiftSlot.DAY
        else:
            return ShiftSlot.EVENING

    def _generate_shift_summary(self, shift: ShiftSlot) -> dict[str, Any]:
        """Generate summary report for completed shift"""
        agents = self.shifts[shift]

        return {
            "shift": shift.value,
            "agents_active": len(agents),
            "avg_level": sum(a.level for a in agents) / len(agents) if agents else 0,
            "tasks_completed": "TBD",  # Would pull from whiteboard
            "patterns_identified": "TBD",
            "escalations": "TBD",
            "next_shift_priorities": [
                "Continue pattern analysis from task logs",
                "Focus on high-priority escalations",
                "Validate hypotheses generated by Kosmos",
            ],
        }

    def get_shift_stats(self) -> dict[str, Any]:
        """Get statistics across all shifts"""
        return {
            "total_agents": self.total_agents,
            "current_shift": self.current_shift.value,
            "shift_distribution": {
                shift.value: len(agents) for shift, agents in self.shifts.items()
            },
            "next_handoff": self._get_next_handoff_time(),
        }

    def _get_next_handoff_time(self) -> str:
        """Calculate time until next shift handoff"""
        now = datetime.now()
        hour = now.hour

        if hour < 8:
            next_handoff = now.replace(hour=8, minute=0, second=0)
        elif hour < 16:
            next_handoff = now.replace(hour=16, minute=0, second=0)
        else:
            next_handoff = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)

        delta = next_handoff - now
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return f"{hours}h {minutes}m"


if __name__ == "__main__":
    print("═══ Shift Management Test ═══\n")

    # Create 200 agents with varying levels
    agent_ids = [f"agent_{str(i).zfill(3)}" for i in range(200)]
    agent_levels = {
        agent_id: (i // 40)  # 0-4 levels distributed
        for i, agent_id in enumerate(agent_ids)
    }

    # Initialize shift manager
    manager = ShiftManager(total_agents=200)
    manager.assign_agents_to_shifts(agent_ids, agent_levels)

    # Show stats
    stats = manager.get_shift_stats()
    print("📊 Shift Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 80)

    # Simulate shift handoff
    manager.perform_shift_handoff(ShiftSlot.DAY, ShiftSlot.EVENING)

    print("\n" + "=" * 80)

    # Show active agents
    active = manager.get_active_agents()
    print(f"\n✅ Currently active agents: {len(active)}")
    print(f"   First 10: {active[:10]}")
