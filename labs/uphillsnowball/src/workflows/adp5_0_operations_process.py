# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ADP 5-0 Operations Process — Plan, Prepare, Execute, Assess.

A simpler, IPB-first workflow variant that follows ADP 5-0 strictly.
Used for routine operations that don't require the full FM 3-0
Multi-Domain Theater Campaign.

Flow:
    1. J-2 IPB (Intelligence Preparation of the Battlefield)
    2. PLAN: J-5 Architect executes MDMP
    3. PREPARE: ROC Drill / Sand Table
    4. EXECUTE: J-3 N-Autoresearch Triad (with J-6 ZTA checks)
    5. ASSESS: J-9 Splinter Engine
"""

from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from src.activities import (
        j3_n_autoresearch_execute,
        j3_roc_drill_prepare,
        j4_logistics_repair,
        j5_mdmp_plan,
        j9_assess_and_syndicate,
    )
    from src.governance.j6_csrmc_cato import Cor_Claude_Code_6_CSRMC_cATO
    from src.intelligence.ipb_engine import ATP_2_01_3_IPB

# Maximum execution retries before escalation
_MAX_EXECUTE_RETRIES = 5


@workflow.defn(name="ADP5_0_OperationsProcess")
class ADP5_0_OperationsProcess:
    """The Operations Process: Plan, Prepare, Execute, Assess.

    Structured exactly per ADP 5-0. The Architect (J-5) executes MDMP.
    The ROC Drill is the Prepare phase. The N-Autoresearch Triad
    is the Execute phase. J-9 Splinter is the Assess phase.
    """

    @workflow.run
    async def run_campaign(self, call_of_question: dict) -> dict:
        """Execute the ADP 5-0 cycle.

        Args:
            call_of_question: Serialized CallOfQuestion dict.

        Returns:
            Final assessment dict from J-9.
        """
        workflow.logger.info("📋 ADP 5-0 Operations Process initiated.")

        # ── Step 1: J-2 IPB ────────────────────────────────────
        ipb_engine = ATP_2_01_3_IPB()
        ipb_intel = await workflow.execute_activity(
            ipb_engine.execute_ipb,
            call_of_question,
            start_to_close_timeout=timedelta(minutes=2),
        )
        workflow.logger.info("✅ IPB complete. MDCOA: %s", ipb_intel.get("mdcoa", ""))

        # ── Step 2: PLAN (J-5 MDMP) ───────────────────────────
        opord = await workflow.execute_activity(
            j5_mdmp_plan,
            {"coq": call_of_question, "intel": ipb_intel},
            start_to_close_timeout=timedelta(minutes=3),
        )

        # ── Step 3: PREPARE (ROC Drill) ───────────────────────
        roc_result = await workflow.execute_activity(
            j3_roc_drill_prepare,
            opord,
            start_to_close_timeout=timedelta(minutes=5),
        )

        if not roc_result.get("passed", False):
            raise ApplicationError(
                "ROC DRILL FAILED. Fratricide detected. Re-planning required.",
                non_retryable=True,
            )

        workflow.logger.info("✅ ROC Drill passed. Proceeding to execution.")

        # ── Step 4: EXECUTE (N-Autoresearch Triad) ─────────────
        for attempt in range(1, _MAX_EXECUTE_RETRIES + 1):
            # J-6 ZTA check before every execution attempt
            Cor_Claude_Code_6_CSRMC_cATO.enforce_zero_trust_handoff(
                "J5",
                "J3",
                {
                    "type": opord.get("type", "CODE_MODIFICATION"),
                    "risk_prob": "SELDOM",
                    "risk_sev": "MARGINAL",
                },
            )

            execution_result = await workflow.execute_activity(
                j3_n_autoresearch_execute,
                opord,
                start_to_close_timeout=timedelta(minutes=6),
            )

            if execution_result.get("success", False):
                break

            workflow.logger.warning("❌ Execution attempt %d failed. J-4 repair.", attempt)

            # J-4 Corrector: Logistics repair (git reset, context wipe)
            await workflow.execute_activity(
                j4_logistics_repair,
                execution_result,
                start_to_close_timeout=timedelta(minutes=1),
            )
        else:
            raise ApplicationError(
                f"EXECUTION FAILED after {_MAX_EXECUTE_RETRIES} attempts.",
                non_retryable=True,
            )

        # ── Step 5: ASSESS (J-9 Splinter Engine) ──────────────
        final_assessment = await workflow.execute_activity(
            j9_assess_and_syndicate,
            execution_result,
            start_to_close_timeout=timedelta(minutes=2),
        )

        workflow.logger.info("🏁 ADP 5-0 cycle COMPLETE.")
        return final_assessment
