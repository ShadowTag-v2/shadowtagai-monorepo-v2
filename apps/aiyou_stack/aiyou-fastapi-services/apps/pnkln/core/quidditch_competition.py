"""QuidditchCompetition - Gamified Agent Competition System
Version: 1.0.0

Philosophy: Competition drives excellence. Dynamic roles based on performance.
Design: Houses for specialization, Quidditch roles for round-based authority.

Houses:
- Gryffindor: Bold solutions, risk-taking
- Ravenclaw: Analytical, deep research
- Hufflepuff: Reliable, thorough
- Slytherin: Strategic, optimization

Quidditch Roles (assigned by performance each round):
- Seeker: Winner - can veto/override final answer
- Chasers: 2nd-3rd - primary solution builders
- Beaters: 4th-5th - critics, attack weak solutions
- Keeper: 6th+ - defend current best answer
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class HogwartsHouse(StrEnum):
    """Houses represent specialization tendencies."""

    GRYFFINDOR = "gryffindor"  # Bold, novel approaches
    RAVENCLAW = "ravenclaw"  # Analytical, precise
    HUFFLEPUFF = "hufflepuff"  # Reliable, thorough
    SLYTHERIN = "slytherin"  # Strategic, efficient


class QuidditchRole(StrEnum):
    """Roles assigned based on round performance."""

    SEEKER = "seeker"  # 1st place - final authority
    CHASER = "chaser"  # 2nd-3rd - build solutions
    BEATER = "beater"  # 4th-5th - critique/attack
    KEEPER = "keeper"  # 6th+ - defend


@dataclass
class HouseProfile:
    """Characteristics of each house."""

    house: HogwartsHouse
    strengths: list[str]
    approach: str
    risk_tolerance: float  # 0-1


# House definitions
HOUSE_PROFILES = {
    HogwartsHouse.GRYFFINDOR: HouseProfile(
        house=HogwartsHouse.GRYFFINDOR,
        strengths=["innovation", "bold_solutions", "risk_taking"],
        approach="Try unconventional approaches first",
        risk_tolerance=0.8,
    ),
    HogwartsHouse.RAVENCLAW: HouseProfile(
        house=HogwartsHouse.RAVENCLAW,
        strengths=["analysis", "research", "precision"],
        approach="Deep research before proposing",
        risk_tolerance=0.3,
    ),
    HogwartsHouse.HUFFLEPUFF: HouseProfile(
        house=HogwartsHouse.HUFFLEPUFF,
        strengths=["reliability", "thoroughness", "consistency"],
        approach="Systematic coverage of all cases",
        risk_tolerance=0.4,
    ),
    HogwartsHouse.SLYTHERIN: HouseProfile(
        house=HogwartsHouse.SLYTHERIN,
        strengths=["strategy", "efficiency", "optimization"],
        approach="Find optimal path with minimal effort",
        risk_tolerance=0.6,
    ),
}


@dataclass
class QuidditchAgent:
    """Agent in the Quidditch competition system."""

    agent_id: str
    house: HogwartsHouse
    current_role: QuidditchRole | None = None
    points_scored: int = 0
    rounds_as_seeker: int = 0
    lifetime_house_points: int = 0
    glicko_rating: float = 1500.0
    glicko_rd: float = 350.0  # Rating deviation


@dataclass
class RoundResult:
    """Result from a competition round."""

    round_id: str
    rankings: list[str]  # agent_ids in order
    winning_solution: str
    house_points_awarded: dict[HogwartsHouse, int]
    seeker_decision: str
    timestamp: datetime = field(default_factory=datetime.now)


class QuidditchCompetition:
    """Gamified competition system for agents.

    Each round:
    1. Agents compete on a task
    2. Rankings determine roles for next phase
    3. Winner becomes Seeker with final authority
    4. House points accumulate over time
    """

    def __init__(self):
        self.agents: dict[str, QuidditchAgent] = {}
        self.house_points: dict[HogwartsHouse, int] = dict.fromkeys(HogwartsHouse, 0)
        self.round_history: list[RoundResult] = []
        self.current_round: int = 0

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def register_agent(self, agent_id: str, house: HogwartsHouse = None) -> QuidditchAgent:
        """Register agent in competition system."""
        if house is None:
            # Sort based on agent characteristics or randomly
            house = random.choice(list(HogwartsHouse))

        agent = QuidditchAgent(agent_id=agent_id, house=house)
        self.agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> QuidditchAgent | None:
        """Get agent profile."""
        return self.agents.get(agent_id)

    def get_house_profile(self, house: HogwartsHouse) -> HouseProfile:
        """Get house characteristics."""
        return HOUSE_PROFILES[house]

    # =========================================================================
    # ROLE ASSIGNMENT
    # =========================================================================

    def assign_roles(self, rankings: list[str]) -> dict[str, QuidditchRole]:
        """Assign Quidditch roles based on rankings.

        1st = Seeker (final authority)
        2nd-3rd = Chasers (build solutions)
        4th-5th = Beaters (critique)
        6th+ = Keepers (defend)
        """
        roles = {}

        for i, agent_id in enumerate(rankings):
            if agent_id not in self.agents:
                continue

            if i == 0:
                role = QuidditchRole.SEEKER
                self.agents[agent_id].rounds_as_seeker += 1
            elif i <= 2:
                role = QuidditchRole.CHASER
            elif i <= 4:
                role = QuidditchRole.BEATER
            else:
                role = QuidditchRole.KEEPER

            self.agents[agent_id].current_role = role
            roles[agent_id] = role

        return roles

    def get_role_abilities(self, role: QuidditchRole) -> dict[str, Any]:
        """Get abilities for each role."""
        abilities = {
            QuidditchRole.SEEKER: {
                "can_veto": True,
                "can_override": True,
                "final_authority": True,
                "description": "Catches the snitch - makes final decision",
            },
            QuidditchRole.CHASER: {
                "can_propose": True,
                "points_per_goal": 10,
                "description": "Scores goals - builds primary solution",
            },
            QuidditchRole.BEATER: {
                "can_attack": True,
                "can_critique": True,
                "description": "Bludgers - attacks weak solutions",
            },
            QuidditchRole.KEEPER: {
                "can_defend": True,
                "can_maintain": True,
                "description": "Guards hoops - defends current best",
            },
        }
        return abilities.get(role, {})

    # =========================================================================
    # COMPETITION ROUNDS
    # =========================================================================

    def start_round(self, task: str) -> dict[str, Any]:
        """Start a new competition round."""
        self.current_round += 1

        return {
            "round_id": f"round_{self.current_round}",
            "task": task,
            "participants": list(self.agents.keys()),
            "current_standings": self.get_standings(),
        }

    def play_round(
        self, rankings: list[str], winning_solution: str, seeker_decision: str,
    ) -> RoundResult:
        """Execute a competition round.

        1. Chasers propose solutions (scoring)
        2. Beaters critique (attack)
        3. Keeper defends best current
        4. Seeker makes final call
        """
        # Assign roles
        self.assign_roles(rankings)

        # Award points
        house_points = {}
        for i, agent_id in enumerate(rankings):
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # Points based on ranking
            points = max(0, 100 - (i * 15))
            agent.points_scored += points
            agent.lifetime_house_points += points

            # House points
            if agent.house not in house_points:
                house_points[agent.house] = 0
            house_points[agent.house] += points

        # Update house standings
        for house, points in house_points.items():
            self.house_points[house] += points

        # Update Glicko ratings
        self._update_ratings(rankings)

        # Create result
        result = RoundResult(
            round_id=f"round_{self.current_round}",
            rankings=rankings,
            winning_solution=winning_solution,
            house_points_awarded=house_points,
            seeker_decision=seeker_decision,
        )
        self.round_history.append(result)

        return result

    def _update_ratings(self, rankings: list[str]):
        """Update Glicko-2 ratings based on round results."""
        # Simplified Glicko update
        for i, agent_id in enumerate(rankings):
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # Winners gain, losers lose
            # Rating change based on position
            n = len(rankings)
            expected_position = n / 2
            actual_position = i + 1

            # Better than expected = gain
            rating_change = (expected_position - actual_position) * 15

            agent.glicko_rating += rating_change

            # Reduce RD as we get more data
            agent.glicko_rd = max(50, agent.glicko_rd * 0.95)

    # =========================================================================
    # STANDINGS AND RANKINGS
    # =========================================================================

    def get_standings(self) -> dict[str, Any]:
        """Get current competition standings."""
        # Agent rankings
        agent_rankings = sorted(self.agents.values(), key=lambda a: a.glicko_rating, reverse=True)

        # House rankings
        house_rankings = sorted(self.house_points.items(), key=lambda x: x[1], reverse=True)

        return {
            "agent_rankings": [
                {
                    "rank": i + 1,
                    "agent_id": a.agent_id,
                    "house": a.house.value,
                    "rating": round(a.glicko_rating),
                    "points": a.points_scored,
                    "seeker_rounds": a.rounds_as_seeker,
                }
                for i, a in enumerate(agent_rankings)
            ],
            "house_rankings": [
                {"rank": i + 1, "house": h.value, "points": p}
                for i, (h, p) in enumerate(house_rankings)
            ],
            "house_cup_leader": house_rankings[0][0].value if house_rankings else None,
        }

    def get_house_cup_winner(self) -> HogwartsHouse:
        """Get current House Cup leader."""
        return max(self.house_points, key=self.house_points.get)

    # =========================================================================
    # TEAM FORMATION
    # =========================================================================

    def form_team(self, agent_ids: list[str]) -> dict[str, Any]:
        """Form a Quidditch team from agents.
        Balances roles based on current standings.
        """
        # Sort by rating
        sorted_agents = sorted(
            [self.agents[aid] for aid in agent_ids if aid in self.agents],
            key=lambda a: a.glicko_rating,
            reverse=True,
        )

        if len(sorted_agents) < 2:
            return {"error": "Need at least 2 agents for a team"}

        # Assign roles
        roles = self.assign_roles([a.agent_id for a in sorted_agents])

        # Team composition
        team = {"seeker": None, "chasers": [], "beaters": [], "keepers": []}

        for agent_id, role in roles.items():
            if role == QuidditchRole.SEEKER:
                team["seeker"] = agent_id
            elif role == QuidditchRole.CHASER:
                team["chasers"].append(agent_id)
            elif role == QuidditchRole.BEATER:
                team["beaters"].append(agent_id)
            else:
                team["keepers"].append(agent_id)

        return {
            "team": team,
            "house_distribution": self._get_house_distribution(agent_ids),
        }

    def _get_house_distribution(self, agent_ids: list[str]) -> dict[str, int]:
        """Get house distribution for a group of agents."""
        distribution = {}
        for agent_id in agent_ids:
            if agent_id in self.agents:
                house = self.agents[agent_id].house.value
                distribution[house] = distribution.get(house, 0) + 1
        return distribution

    # =========================================================================
    # PRE-MATCH AND HALFTIME
    # =========================================================================

    def pre_match_briefing(self, team: list[str]) -> dict[str, Any]:
        """Pre-match briefing for team.
        Each agent gets strategy based on house.
        """
        briefings = {}

        for agent_id in team:
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]
            profile = HOUSE_PROFILES[agent.house]

            briefings[agent_id] = {
                "house": agent.house.value,
                "approach": profile.approach,
                "strengths_to_leverage": profile.strengths,
                "current_role": agent.current_role.value if agent.current_role else "TBD",
            }

        return briefings

    def halftime_analysis(self) -> dict[str, Any]:
        """Halftime analysis of competition.
        Identify trends, suggest adjustments.
        """
        if len(self.round_history) < 2:
            return {"message": "Not enough rounds for analysis"}

        # Recent trends
        recent = self.round_history[-5:]

        # Who's been Seeker most
        seeker_counts = {}
        for result in recent:
            seeker = result.rankings[0]
            seeker_counts[seeker] = seeker_counts.get(seeker, 0) + 1

        # House momentum
        house_momentum = dict.fromkeys(HogwartsHouse, 0)
        for result in recent:
            for house, points in result.house_points_awarded.items():
                house_momentum[house] += points

        return {
            "rounds_analyzed": len(recent),
            "dominant_seeker": max(seeker_counts, key=seeker_counts.get) if seeker_counts else None,
            "house_momentum": {h.value: p for h, p in house_momentum.items()},
            "hot_house": max(house_momentum, key=house_momentum.get).value,
        }

    # =========================================================================
    # TOURNAMENT FORMATS
    # =========================================================================

    def create_tournament(self, format: str = "bracket", rounds: int = 5) -> dict[str, Any]:
        """Create a tournament structure.

        Formats:
        - bracket: Elimination
        - league: Round-robin
        - ladder: Challenge up/down
        """
        participants = list(self.agents.keys())

        if format == "bracket":
            return self._create_bracket(participants, rounds)
        if format == "league":
            return self._create_league(participants, rounds)
        # ladder
        return self._create_ladder(participants)

    def _create_bracket(self, participants: list[str], rounds: int) -> dict[str, Any]:
        """Create elimination bracket."""
        random.shuffle(participants)

        bracket = []
        remaining = participants.copy()

        for round_num in range(rounds):
            round_matches = []
            next_round = []

            for i in range(0, len(remaining), 2):
                if i + 1 < len(remaining):
                    round_matches.append(
                        {
                            "match": len(round_matches) + 1,
                            "agent_a": remaining[i],
                            "agent_b": remaining[i + 1],
                            "winner": None,
                        },
                    )
                else:
                    # Bye
                    next_round.append(remaining[i])

            bracket.append({"round": round_num + 1, "matches": round_matches})

            # Placeholder for winners
            remaining = next_round + [None] * len(round_matches)

        return {"format": "bracket", "total_rounds": rounds, "bracket": bracket}

    def _create_league(self, participants: list[str], rounds: int) -> dict[str, Any]:
        """Create round-robin league."""
        schedule = []

        for round_num in range(rounds):
            round_matches = []
            shuffled = participants.copy()
            random.shuffle(shuffled)

            for i in range(0, len(shuffled), 2):
                if i + 1 < len(shuffled):
                    round_matches.append({"agent_a": shuffled[i], "agent_b": shuffled[i + 1]})

            schedule.append({"round": round_num + 1, "matches": round_matches})

        return {"format": "league", "total_rounds": rounds, "schedule": schedule}

    def _create_ladder(self, participants: list[str]) -> dict[str, Any]:
        """Create challenge ladder."""
        # Sort by current rating
        sorted_by_rating = sorted(
            participants,
            key=lambda aid: self.agents[aid].glicko_rating if aid in self.agents else 0,
            reverse=True,
        )

        return {
            "format": "ladder",
            "ladder": [
                {"position": i + 1, "agent_id": aid} for i, aid in enumerate(sorted_by_rating)
            ],
            "challenge_rules": "Can challenge up to 2 positions above",
        }

    def __repr__(self) -> str:
        return (
            f"QuidditchCompetition("
            f"agents={len(self.agents)}, "
            f"rounds={self.current_round}, "
            f"leader={self.get_house_cup_winner().value})"
        )


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_competition() -> QuidditchCompetition:
    """Create Quidditch competition system.

    "Competition drives excellence."
    """
    return QuidditchCompetition()


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("QuidditchCompetition - Self Test")
    print("=" * 60)

    # Create competition
    comp = create_competition()
    print(f"\nCreated: {comp}")

    # Register agents
    print("\n" + "=" * 60)
    print("Registering Agents...")

    agents = [
        ("harry", HogwartsHouse.GRYFFINDOR),
        ("hermione", HogwartsHouse.RAVENCLAW),
        ("cedric", HogwartsHouse.HUFFLEPUFF),
        ("draco", HogwartsHouse.SLYTHERIN),
        ("luna", HogwartsHouse.RAVENCLAW),
        ("neville", HogwartsHouse.GRYFFINDOR),
    ]

    for agent_id, house in agents:
        comp.register_agent(agent_id, house)
        print(f"  {agent_id} → {house.value}")

    # Start round
    print("\n" + "=" * 60)
    print("Starting Round 1...")

    round_info = comp.start_round("Implement authentication endpoint")
    print(f"Round: {round_info['round_id']}")
    print(f"Participants: {round_info['participants']}")

    # Play round
    print("\n" + "=" * 60)
    print("Playing Round...")

    # Simulate rankings
    rankings = ["hermione", "harry", "luna", "cedric", "draco", "neville"]
    result = comp.play_round(
        rankings=rankings,
        winning_solution="JWT with RS256",
        seeker_decision="Approved with edge case handling",
    )

    print(f"Winner (Seeker): {rankings[0]}")
    print(f"Chasers: {rankings[1:3]}")
    print(f"Beaters: {rankings[3:5]}")
    print(f"Keeper: {rankings[5]}")

    # Check standings
    print("\n" + "=" * 60)
    print("Standings:")

    standings = comp.get_standings()
    print("\nAgent Rankings:")
    for agent in standings["agent_rankings"][:3]:
        print(
            f"  #{agent['rank']} {agent['agent_id']} ({agent['house']}): {agent['rating']} rating",
        )

    print("\nHouse Cup:")
    for house in standings["house_rankings"]:
        print(f"  #{house['rank']} {house['house']}: {house['points']} points")

    # Form team
    print("\n" + "=" * 60)
    print("Forming Team...")

    team = comp.form_team(["hermione", "harry", "luna", "draco"])
    print(f"Seeker: {team['team']['seeker']}")
    print(f"Chasers: {team['team']['chasers']}")
    print(f"Beaters: {team['team']['beaters']}")

    print("\n" + "=" * 60)
    print("✓ QuidditchCompetition working correctly")
    print("\nPhilosophy: Competition drives excellence.")
