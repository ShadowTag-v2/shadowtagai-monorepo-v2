"""FM 3-0 Multi-Domain Operations — Temporal.io Durable Execution.

The complete Theater Campaign workflow: the Commander's Operations
Process executed as a durable, crash-proof state machine.

Flow:
    1. J-5 drafts OPORD & prepares backbrief
    2. Commander authorization (Mobile PWA signal)
    3. IMMORTAL LOOP:
       a. J-2 Shaping Operations (recon)
       b. J-3 Decisive Operations (AI generation)
       c. ROC Drill (gVisor sandbox verification)
       d. J-1 ShadowTag DCT (watermarking)
       e. J-6 Sustaining Operations (audit)
       f. J-39 Splinter (information operations)
    4. Return certified BoundedAlert

Backbrief Pattern:
    The workflow HALTS after OPORD generation and waits for the
    Commander's cryptographic authorization via the Mobile PWA.
    This is the human-in-the-loop gate for HIGH risk operations.
"""

from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from src.activities import (
        j1_shadowtag_dct_embed,
        j2_shaping_ops_recon,
        j39_splinter_information_ops,
        j3_decisive_ops_strike,
        j5_draft_opord_and_backbrief,
        j6_sustaining_ops_audit,
        notify_commander_pwa,
    )
    from src.activities.j3_roc_drill import j3_roc_drill_sandbox


# Maximum retry attempts before escalating to Commander
_MAX_STRIKE_RETRIES = 3


@workflow.defn(name="MultiDomainTheaterCampaign")
class MultiDomainTheaterCampaign:
    """The Commander's Continuous Cycle: Plan → Prepare → Execute → Assess.

    Implements FM 3-0 Multi-Domain Operations as a Temporal workflow.
    The workflow is durable — if the process crashes, Temporal resumes
    from the exact activity where it left off.
    """

    def __init__(self) -> None:
        self.backbrief_authorized: bool | None = None

    @workflow.run
    async def execute_campaign(self, mission: dict) -> dict:
        """Execute the full theater campaign.

        Args:
            mission: Serialized CallOfQuestion dict.

        Returns:
            Final certified receipt with BoundedAlert.
        """
        workflow.logger.info("🎖️ FM 3-0 MDO Campaign initiated: %s", mission.get("case_id"))

        # ── Phase 1: PLAN (J-5 MDMP → OPORD) ──────────────────
        opord = await workflow.execute_activity(
            j5_draft_opord_and_backbrief,
            mission,
            start_to_close_timeout=timedelta(minutes=2),
        )

        # ── THE BACKBRIEF: Commander authorization gate ────────
        await workflow.execute_activity(
            notify_commander_pwa,
            {"type": "BACKBRIEF", "data": opord},
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Wait for the Commander's signal from the Mobile PWA
        await workflow.wait_condition(lambda: self.backbrief_authorized is not None)

        if not self.backbrief_authorized:
            workflow.logger.warning("❌ Commander REJECTED backbrief. Wiping context.")
            raise ApplicationError(
                "COMMANDER_REJECTED_BACKBRIEF",
                non_retryable=True,
            )

        workflow.logger.info("✅ Backbrief AUTHORIZED. Commencing operations.")

        # ── Phase 2-4: IMMORTAL LOOP ───────────────────────────
        for attempt in range(1, _MAX_STRIKE_RETRIES + 1):
            workflow.logger.info("🔄 Strike attempt %d/%d", attempt, _MAX_STRIKE_RETRIES)

            # SHAPING OPERATIONS (J-2 Intel / Deep Research)
            intel = await workflow.execute_activity(
                j2_shaping_ops_recon,
                opord,
                start_to_close_timeout=timedelta(minutes=5),
            )

            # DECISIVE OPERATIONS (J-3 Builder/Tester under UCMJ SLAs)
            assault_artifact = await workflow.execute_activity(
                j3_decisive_ops_strike,
                {"intel": intel, "opord": opord},
                start_to_close_timeout=timedelta(seconds=40),
            )

            # ROC DRILL (gVisor Sand Table — zero fratricide gate)
            roc_report = await workflow.execute_activity(
                j3_roc_drill_sandbox,
                assault_artifact,
                start_to_close_timeout=timedelta(minutes=5),
            )

            if not roc_report.get("passed", False):
                workflow.logger.warning("❌ ROC Drill FAILED (attempt %d). Kickback to J-3.", attempt)
                continue  # Temporal retries from shaping ops

            # SUSTAINING OPS — ShadowTag DCT Watermarking
            watermarked = await workflow.execute_activity(
                j1_shadowtag_dct_embed,
                assault_artifact,
                start_to_close_timeout=timedelta(minutes=1),
            )

            # SUSTAINING OPS — J-6 Audit & Certification
            receipt = await workflow.execute_activity(
                j6_sustaining_ops_audit,
                watermarked,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # INFORMATION OPS — J-39 Splinter Engine
            await workflow.execute_activity(
                j39_splinter_information_ops,
                receipt,
                start_to_close_timeout=timedelta(minutes=2),
            )

            workflow.logger.info("🏁 Campaign COMPLETE. Mission certified.")
            return receipt

        # All retries exhausted
        raise ApplicationError(
            f"CAMPAIGN_FAILED: {_MAX_STRIKE_RETRIES} strike attempts exhausted.",
            non_retryable=True,
        )

    @workflow.signal
    def authorize_backbrief(self, authorized: bool) -> None:
        """Signal handler for Commander backbrief authorization.

        Called from the Mobile PWA when the Commander approves or
        rejects the OPORD backbrief.

        Args:
            authorized: True to proceed, False to abort.
        """
        workflow.logger.info("📱 Backbrief signal received: authorized=%s", authorized)
        self.backbrief_authorized = authorized
