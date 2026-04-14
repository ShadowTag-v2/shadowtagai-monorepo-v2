"""PanelGPT: Expert Panel Discussion

Simulates a panel of domain experts discussing a topic.
With moderator to guide and synthesize.

Philosophy: Diverse expertise > single generalist.
"""

from pydantic import BaseModel, Field


class PanelMember(BaseModel):
    """Expert panel member."""

    name: str
    expertise: str
    perspective: str = Field(description="Their typical viewpoint/approach")


class PanelRound(BaseModel):
    """Single round of panel discussion."""

    round_number: int
    topic: str
    member_contributions: dict[str, str] = Field(description="name -> contribution")
    moderator_summary: str | None = None


class PanelGPTResult(BaseModel):
    """Result of panel discussion."""

    rounds: list[PanelRound]
    synthesis: str = Field(description="Moderator's final synthesis")
    key_insights: list[str]
    areas_of_agreement: list[str]
    areas_of_disagreement: list[str]
    metadata: dict = Field(default_factory=dict)


class PanelGPT:
    """PanelGPT expert panel engine.

    Usage:
        >>> panel = PanelGPT(
        ...     members=[
        ...         PanelMember(
        ...             name="Dr. Smith",
        ...             expertise="ML infrastructure",
        ...             perspective="Performance & scalability"
        ...         ),
        ...         PanelMember(
        ...             name="Jane Doe",
        ...             expertise="Product strategy",
        ...             perspective="User value & monetization"
        ...         )
        ...     ]
        ... )
        >>> result = panel.discuss("Should we build in-house or buy a solution?")

    Why it works:
        - Each expert brings different lens
        - Moderator synthesizes diverse views
        - Reduces blind spots from single perspective
        - Great for:
          * Strategic decisions
          * Cross-functional problems
          * When expertise spans multiple domains
    """

    def __init__(
        self,
        members: list[PanelMember],
        rounds: int = 3,
        moderator_role: str = "synthesize and guide",
    ) -> None:
        """Initialize expert panel.

        Args:
            members: List of panel members with expertise
            rounds: Number of discussion rounds
            moderator_role: What the moderator should do

        """
        self.members = members
        self.rounds = rounds
        self.moderator_role = moderator_role

    def format_member_prompt(
        self,
        member: PanelMember,
        topic: str,
        round_num: int,
        previous_round: PanelRound | None = None,
    ) -> str:
        """Generate prompt for a panel member."""
        prompt = f"""You are {member.name}, a {member.expertise} expert on this panel.

Your perspective: {member.perspective}

Panel discussion topic:
{topic}

Round {round_num}/{self.rounds}"""

        if previous_round:
            prompt += "\n\nPrevious round contributions:\n"
            for name, contribution in previous_round.member_contributions.items():
                if name != member.name:
                    prompt += f"\n{name}: {contribution}\n"

            if previous_round.moderator_summary:
                prompt += f"\nModerator summary: {previous_round.moderator_summary}\n"

            prompt += "\n\nBuild on the discussion. What do you add or challenge?"

        else:
            prompt += "\n\nProvide your initial perspective as an expert."

        return prompt.strip()

    def format_moderator_prompt(self, round_data: PanelRound) -> str:
        """Generate moderator synthesis prompt."""
        contributions = "\n\n".join(
            f"{name}:\n{text}" for name, text in round_data.member_contributions.items()
        )

        prompt = f"""You are the panel moderator. Your role: {self.moderator_role}

Topic: {round_data.topic}

Panel contributions this round:
{contributions}

Synthesize:
- Key points of agreement
- Key points of debate/disagreement
- What questions remain
- Where to focus next round (if applicable)"""

        return prompt.strip()

    def discuss(
        self,
        topic: str,
        model: any | None = None,
        temperature: float = 0.6,
    ) -> PanelGPTResult:
        """Run panel discussion.

        Args:
            topic: What to discuss
            model: Optional model instance
            temperature: Sampling temperature

        Returns:
            PanelGPTResult with rounds and synthesis

        """
        # Placeholder implementation
        # In production:
        # 1. For each round:
        #    a. Each member contributes (based on their expertise)
        #    b. Moderator synthesizes
        # 2. Final moderator synthesis across all rounds
        # 3. Extract key insights, agreements, disagreements

        result = PanelGPTResult(
            rounds=[
                PanelRound(
                    round_number=1,
                    topic=topic,
                    member_contributions={
                        m.name: f"Contribution placeholder from {m.name}" for m in self.members
                    },
                    moderator_summary="Round 1 summary placeholder",
                ),
            ],
            synthesis="Final synthesis placeholder",
            key_insights=[],
            areas_of_agreement=[],
            areas_of_disagreement=[],
            metadata={
                "technique": "PanelGPT",
                "num_members": len(self.members),
                "rounds": self.rounds,
            },
        )

        return result

    def __repr__(self) -> str:
        member_names = [m.name for m in self.members]
        return f"PanelGPT(members={member_names}, rounds={self.rounds})"
