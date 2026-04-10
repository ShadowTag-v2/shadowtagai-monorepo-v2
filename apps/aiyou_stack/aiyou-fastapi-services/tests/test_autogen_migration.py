"""
Tests for AutoGen to n-autoresearch/Kosmos/BioAgents Migration Script.

Covers:
- Agent-to-tier mapping
- Risk detection
- Brakes penalty system
- Swarm voting decisions
- Weekly-audit end-to-end scenario
"""

import pytest

from agents.autogen_migration import (
    AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator,
    Decision,
    n-autoresearch/Kosmos/BioAgentsClient,
    RiskLevel,
    migrate_autogen_config,
)


class Testn-autoresearch/Kosmos/BioAgentsClient:
    """Tests for the mock n-autoresearch/Kosmos/BioAgents voting client."""

    @pytest.fixture
    def client(self):
        return n-autoresearch/Kosmos/BioAgentsClient()

    def test_simple_hash_deterministic(self, client):
        """Hash should be deterministic for same input."""
        hash1 = client.simple_hash("test input")
        hash2 = client.simple_hash("test input")
        assert hash1 == hash2

    def test_simple_hash_different_for_different_input(self, client):
        """Different inputs should produce different hashes."""
        hash1 = client.simple_hash("input a")
        hash2 = client.simple_hash("input b")
        assert hash1 != hash2

    # Risk Detection Tests
    def test_detect_risk_low_for_test_env(self, client):
        """Test/staging environments should be low risk."""
        assert client.detect_risk("Deploy to test environment") == RiskLevel.LOW.value
        assert client.detect_risk("Run in staging") == RiskLevel.LOW.value
        assert client.detect_risk("Local development") == RiskLevel.LOW.value

    def test_detect_risk_medium_default(self, client):
        """Normal tasks should default to medium risk."""
        assert client.detect_risk("Deploy weekly audit job") == RiskLevel.MEDIUM.value
        assert client.detect_risk("Create new endpoint") == RiskLevel.MEDIUM.value

    def test_detect_risk_high_for_sensitive_ops(self, client):
        """Sensitive operations should be high risk."""
        assert client.detect_risk("Delete old records") == RiskLevel.HIGH.value
        assert client.detect_risk("Deploy to prod") == RiskLevel.HIGH.value
        assert client.detect_risk("Update secret values") == RiskLevel.HIGH.value

    def test_detect_risk_extreme_for_destructive_ops(self, client):
        """Destructive operations should be extreme high risk."""
        assert client.detect_risk("rm -rf /data") == RiskLevel.EXTREME_HIGH.value
        assert client.detect_risk("DROP DATABASE users") == RiskLevel.EXTREME_HIGH.value

    # Brakes Detection Tests
    def test_detect_brakes_zero_for_clean_input(self, client):
        """Clean inputs should have zero brakes."""
        assert client.detect_brakes("Deploy standard update") == 0

    def test_detect_brakes_counts_keywords(self, client):
        """Should count brake keywords."""
        assert client.detect_brakes("untested code") == 1
        assert client.detect_brakes("untested prod deployment") == 2
        assert client.detect_brakes("untested prod delete with force") == 4

    def test_detect_brakes_capped_at_five(self, client):
        """Brakes count should cap at 5."""
        text = "untested prod delete secret force override extra"
        assert client.detect_brakes(text) == 5

    # Swarm Vote Tests
    def test_swarm_vote_approve_low_risk(self, client):
        """Low risk tasks should be approved."""
        result = client.swarm_vote("Run tests in staging environment")
        assert result.decision == Decision.APPROVE.value
        assert result.risk == RiskLevel.LOW.value
        assert result.confidence > 60

    def test_swarm_vote_approve_medium_risk_clean(self, client):
        """Medium risk clean tasks should be approved."""
        result = client.swarm_vote("Deploy weekly audit scheduler")
        assert result.decision == Decision.APPROVE.value
        assert result.risk == RiskLevel.MEDIUM.value

    def test_swarm_vote_reject_extreme_risk(self, client):
        """Extreme risk should be fast-rejected."""
        result = client.swarm_vote("Execute rm -rf on database")
        assert result.decision == Decision.REJECT.value
        assert result.risk == RiskLevel.EXTREME_HIGH.value
        assert result.confidence == 95

    def test_swarm_vote_reject_excessive_brakes(self, client):
        """Excessive brakes should trigger fast-reject."""
        result = client.swarm_vote("Force override untested prod delete secret")
        assert result.decision == Decision.REJECT.value
        assert result.brakes >= 4

    def test_swarm_vote_includes_tier_votes(self, client):
        """Approved votes should include tier breakdown."""
        result = client.swarm_vote("Standard deployment task")
        assert result.tier_votes is not None
        assert len(result.tier_votes) == 3  # Strategy, Execution, Worker

        tier_labels = {v["tier"] for v in result.tier_votes}
        assert tier_labels == {"Strategy", "Execution", "Worker"}

    def test_swarm_vote_score_range(self, client):
        """Score should be between 0 and 1."""
        result = client.swarm_vote("Any task here")
        assert 0 <= result.score <= 1


class TestAutoGenTon-autoresearch/Kosmos/BioAgentsMigrator:
    """Tests for the AutoGen migration adapter."""

    @pytest.fixture
    def migrator(self):
        return AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

    # Agent Mapping Tests
    def test_map_planner_to_strategy(self, migrator):
        """Planner roles should map to strategy tier."""
        agents = [{"name": "task_planner", "role": "planner"}]
        mapping = migrator.map_agents_to_tiers(agents)
        assert mapping["task_planner"] == "strategy"

    def test_map_coder_to_execution(self, migrator):
        """Coder/developer roles should map to execution tier."""
        agents = [
            {"name": "python_dev", "role": "coder"},
            {"name": "backend_eng", "role": "developer"},
        ]
        mapping = migrator.map_agents_to_tiers(agents)
        assert mapping["python_dev"] == "execution"
        assert mapping["backend_eng"] == "execution"

    def test_map_verifier_to_worker(self, migrator):
        """Verifier/tester roles should map to worker tier."""
        agents = [
            {"name": "qa_agent", "role": "verifier"},
            {"name": "test_runner", "role": "tester"},
        ]
        mapping = migrator.map_agents_to_tiers(agents)
        assert mapping["qa_agent"] == "worker"
        assert mapping["test_runner"] == "worker"

    def test_map_unknown_role_defaults_to_worker(self, migrator):
        """Unknown roles should default to worker tier."""
        agents = [{"name": "mystery_agent", "role": "custom_role"}]
        mapping = migrator.map_agents_to_tiers(agents)
        assert mapping["mystery_agent"] == "worker"

    # Handoff Translation Tests
    def test_translate_handoff_includes_tier(self, migrator):
        """Handoff translation should include target tier."""
        agents = [{"name": "executor", "role": "coder"}]
        migrator.map_agents_to_tiers(agents)

        intent = migrator.translate_handoff("Deploy job", "executor")
        assert "execution tier" in intent
        assert "Deploy job" in intent

    def test_translate_handoff_unknown_agent(self, migrator):
        """Unknown agent should default to execution tier."""
        intent = migrator.translate_handoff("Some task", "unknown_agent")
        assert "execution tier" in intent

    # Full Migration Tests
    def test_migrate_task_returns_complete_result(self, migrator):
        """Migration should return complete result structure."""
        result = migrator.migrate_task(
            autogen_task="Simple task", autogen_agents=[{"name": "agent1", "role": "coder"}]
        )

        assert "original_autogen" in result
        assert "migrated_fm" in result
        assert "migration_notes" in result

        assert result["original_autogen"]["task"] == "Simple task"
        assert result["migrated_fm"]["decision"] in ["APPROVE", "REJECT", "ESCALATE"]

    def test_migrate_task_with_handoff(self, migrator):
        """Migration with handoff should translate to intent."""
        result = migrator.migrate_task(
            autogen_task="Deploy service",
            autogen_agents=[
                {"name": "planner", "role": "planner"},
                {"name": "deployer", "role": "coder"},
            ],
            handoff="deployer",
        )

        assert result["original_autogen"]["handoff"] == "deployer"
        assert "decision" in result["migrated_fm"]

    def test_migrate_task_notes_agent_count(self, migrator):
        """Migration notes should mention agent replacement."""
        result = migrator.migrate_task(
            autogen_task="Task", autogen_agents=[{"name": "a1", "role": "coder"}] * 5
        )

        assert "5-agent chat" in result["migration_notes"]
        assert "200 weighted vote" in result["migration_notes"]


class TestWeeklyAuditMigration:
    """End-to-end test for the weekly-audit deployment scenario."""

    def test_weekly_audit_full_migration(self):
        """
        Test the complete weekly-audit migration scenario.

        Simulates AutoGen Swarm with 3 agents:
        - audit_planner (planner) -> strategy tier
        - deploy_executor (coder) -> execution tier
        - verification_agent (verifier) -> worker tier

        Expected: APPROVE with medium risk, zero brakes
        """
        migrator = AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

        autogen_agents = [
            {"name": "audit_planner", "role": "planner"},
            {"name": "deploy_executor", "role": "coder"},
            {"name": "verification_agent", "role": "verifier"},
        ]

        autogen_task = (
            "Plan and deploy weekly-audit Cloud Run Job with scheduler trigger every Sunday 3AM UTC"
        )

        result = migrator.migrate_task(
            autogen_task=autogen_task, autogen_agents=autogen_agents, handoff="deploy_executor"
        )

        # Verify original is preserved
        assert result["original_autogen"]["task"] == autogen_task
        assert len(result["original_autogen"]["agents"]) == 3
        assert result["original_autogen"]["handoff"] == "deploy_executor"

        # Verify FM decision
        fm_result = result["migrated_fm"]
        assert fm_result["decision"] == "APPROVE"
        assert fm_result["risk"] == "M"  # Medium risk (no prod/delete keywords)
        assert fm_result["brakes"] == 0  # No brake keywords
        assert fm_result["confidence"] >= 60  # Above approval threshold
        assert 0.60 <= fm_result["score"] <= 0.85  # Reasonable approval range

        # Verify migration notes
        assert "3-agent chat" in result["migration_notes"]
        assert "200 weighted vote" in result["migration_notes"]

    def test_weekly_audit_with_prod_keyword(self):
        """
        Weekly-audit with 'prod' keyword should be higher risk.
        """
        migrator = AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

        result = migrator.migrate_task(
            autogen_task="Deploy weekly-audit to prod Cloud Run",
            autogen_agents=[{"name": "deployer", "role": "coder"}],
        )

        # Higher risk due to 'prod' keyword
        assert result["migrated_fm"]["risk"] == "H"
        # May still approve but with lower confidence
        assert result["migrated_fm"]["decision"] in ["APPROVE", "ESCALATE", "REJECT"]

    def test_weekly_audit_execution_time(self):
        """
        Migration should complete in under 1 second.

        This validates the 350x efficiency improvement over AutoGen chat.
        """
        import time

        migrator = AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

        autogen_agents = [
            {"name": "audit_planner", "role": "planner"},
            {"name": "deploy_executor", "role": "coder"},
            {"name": "verification_agent", "role": "verifier"},
        ]

        start = time.perf_counter()

        for _ in range(100):  # Run 100 migrations
            migrator.migrate_task(
                autogen_task="Deploy weekly-audit Cloud Run Job",
                autogen_agents=autogen_agents,
                handoff="deploy_executor",
            )

        elapsed = time.perf_counter() - start

        # 100 migrations should complete in under 1 second
        assert elapsed < 1.0, f"100 migrations took {elapsed:.3f}s, expected <1s"
        # Average per migration should be under 10ms
        assert (elapsed / 100) < 0.01


class TestConvenienceFunction:
    """Tests for the migrate_autogen_config convenience function."""

    def test_migrate_autogen_config_works(self):
        """Convenience function should work without instantiating migrator."""
        result = migrate_autogen_config(
            task="Quick task", agents=[{"name": "worker", "role": "coder"}]
        )

        assert "migrated_fm" in result
        assert result["migrated_fm"]["decision"] in ["APPROVE", "REJECT", "ESCALATE"]

    def test_migrate_autogen_config_with_handoff(self):
        """Convenience function should support handoff parameter."""
        result = migrate_autogen_config(
            task="Task with handoff",
            agents=[{"name": "planner", "role": "planner"}, {"name": "executor", "role": "coder"}],
            handoff="executor",
        )

        assert result["original_autogen"]["handoff"] == "executor"


class TestGroupChatMigration:
    """Tests for AutoGen GroupChat message history migration."""

    def test_migrate_group_chat_extracts_task(self):
        """Should extract task from message history."""
        migrator = AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Deploy the weekly audit job"},
            {"role": "assistant", "content": "I will deploy the job"},
        ]

        agents = [{"name": "assistant", "role": "coder"}]

        result = migrator.migrate_group_chat(messages, agents)

        assert "Deploy the weekly audit job" in result["original_autogen"]["task"]

    def test_migrate_group_chat_uses_last_message_fallback(self):
        """Should use last message if no user/system found."""
        migrator = AutoGenTon-autoresearch/Kosmos/BioAgentsMigrator()

        messages = [{"role": "assistant", "content": "Final response with task"}]

        agents = [{"name": "assistant", "role": "coder"}]

        result = migrator.migrate_group_chat(messages, agents)

        assert result["original_autogen"]["task"] == "Final response with task"
