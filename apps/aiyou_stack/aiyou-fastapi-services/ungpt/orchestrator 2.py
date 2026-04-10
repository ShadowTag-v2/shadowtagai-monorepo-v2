"""
UnGPT v2.0 Orchestrator
Static vs Dynamic Architecture

Layers:
- L0: SuperGrok.1 (Intake & SPT.1) - Static
- L1: Claude.1 (Frame & SPT.2) - Dynamic
- L2: Gemini <-> GPT Loop - Generation
- L3: SuperGrok.2 (Static Validation) - Static
- L4: Claude.2 (Execution & Publish) - Dynamic
- L5: SuperGrok.3 (Repackage) - Static
- L6: Claude.3 (PR Check) - Dynamic (Optional)
- L7: SuperGrok.4 (Voice) - Static
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import yaml
from rich.console import Console

from .agents import (
    claude_execute,
    claude_frame,
    claude_pr_check,
    gemini_refine,
    gpt5_refine,
    supergrok_intake,
    supergrok_repackage,
    supergrok_validate,
    supergrok_voice,
)
from .utils import crm_analytics, retry_logic

console = Console()


@dataclass
class PipelineResult:
    """Result of a complete pipeline run"""

    success: bool
    query_id: str
    crm_score: float = 0.0
    final_answer: str = ""
    voice_script: str = ""
    github_url: str = ""
    relooped: bool = False
    total_cost: float = 0.0
    total_cycles: int = 0
    abort_reason: str = ""
    error: str = ""
    costs_breakdown: dict[str, float] = field(default_factory=dict)


class UnGPTOrchestrator:
    """
    Main orchestrator for UnGPT v2.0 pipeline.

    Static vs Dynamic separation:
    - Static (SuperGrok): Text validation, intent checking, no code execution
    - Dynamic (Claude): Code execution, sandbox, publishing
    """

    def __init__(self, config_path: str = "ungpt/config.yaml"):
        self.config = self._load_config(config_path)
        self.api_keys = self._load_api_keys()
        self.costs: dict[str, float] = {}
        self.query_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time: datetime | None = None

        # Initialize analytics DB
        self.analytics_db = self.config["analytics"]["db_path"]
        crm_analytics.init_db(self.analytics_db)

    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML"""
        with open(path) as f:
            return yaml.safe_load(f)

    def _load_api_keys(self) -> dict:
        """Load API keys from environment"""
        return {
            "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        }

    def _track_cost(self, layer: str, cost: float):
        """Track cost for a layer"""
        self.costs[layer] = cost
        total = sum(self.costs.values())
        if total > self.config["pipeline"]["cost_alert_threshold"]:
            console.print(f"[yellow]Cost Alert: ${total:.4f}[/yellow]")

    async def run(self, voice_input: str) -> PipelineResult:
        """
        Execute the complete 7-layer pipeline.

        Args:
            voice_input: Raw voice input or text query

        Returns:
            PipelineResult with all outputs
        """
        self.start_time = datetime.now()
        console.print(f"\n[cyan]Query ID:[/cyan] {self.query_id}")

        # Initialize tracking variables for scope safety
        enhanced_tools: list[str] = []
        total_cycles = 0
        relooped = False

        try:
            # === L0: SuperGrok Intake (STATIC) ===
            console.print("[yellow]L0: SuperGrok Intake[/yellow]")
            l0 = await retry_logic.with_retry(
                supergrok_intake.process_voice,
                voice_input,
                self.config["models"]["l0_grok"],
                self.api_keys["XAI_API_KEY"],
            )
            self._track_cost("L0_SuperGrok", l0["cost"])
            normalized_query = l0["normalized"]
            spt1 = l0["spt1"]  # Baseline expectations
            console.print("  Query normalized. SPT.1 defined.\n")

            # === L1: Claude Frame (DYNAMIC) ===
            console.print("[yellow]L1: Claude Frame & Scope[/yellow]")
            l1 = await retry_logic.with_retry(
                claude_frame.frame_query,
                normalized_query,
                spt1,
                self.config["models"]["l1_claude"],
                self.api_keys["ANTHROPIC_API_KEY"],
            )
            self._track_cost("L1_Claude_Frame", l1["cost"])
            framework = l1["framework"]
            spt2 = l1["spt2"]  # Structural requirements
            console.print("  Framework ready. SPT.2 defined.\n")

            # === L2: Gemini <-> GPT Infinite Loop ===
            console.print("[yellow]L2: Collaborative Loop (Gemini <-> GPT)[/yellow]")
            l2_result = await self._run_collaborative_loop(
                framed_content=framework, tools=None, feedback=None
            )
            total_cycles += l2_result["cycles"]
            converged_draft = l2_result["final_draft"]
            console.print(f"  Converged in {l2_result['cycles']} cycles.\n")

            # === L3: SuperGrok Static Validation (STATIC) ===
            console.print("[yellow]L3: SuperGrok Static Validation[/yellow]")
            l3 = await retry_logic.with_retry(
                supergrok_validate.validate_draft,
                converged_draft,
                spt1,  # Check against baseline expectations
                self.config["models"]["l3_grok"],
                self.api_keys["XAI_API_KEY"],
            )
            self._track_cost("L3_SuperGrok_Validate", l3["cost"])

            # Extract execution flags
            l3["validation_report"]
            flagged_draft = l3["flagged_draft"]  # Contains [REQ_EXECUTION] tags
            execution_flags = l3["execution_flags"]
            console.print(f"  Validation complete. {len(execution_flags)} code blocks flagged.\n")

            # === L4: Claude Execution & Publish (DYNAMIC) ===
            console.print("[yellow]L4: Claude Execution & Publish[/yellow]")
            l4 = await retry_logic.with_retry(
                claude_execute.execute_and_publish,
                flagged_draft,
                spt2,  # Check against structural requirements
                execution_flags,
                self.config["models"]["l4_claude"],
                self.api_keys["ANTHROPIC_API_KEY"],
                self.config["github"],
                self.api_keys["GITHUB_TOKEN"],
                self.query_id,
            )
            self._track_cost("L4_Claude_Execute", l4["cost"])

            crm_score = l4["crm_score"]
            final_answer = l4["final_answer"]
            github_url = l4["github_url"]
            console.print(f"  CRM Score: [bold]{crm_score}/10[/bold]")
            console.print(f"  GitHub: {github_url}\n")

            # === CRM Decision Gate ===
            if crm_score <= self.config["pipeline"]["crm_abort_threshold"]:
                console.print("[bold red]CRM Score <= 3: ABORTING[/bold red]")
                return self._finalize(
                    success=False,
                    crm_score=crm_score,
                    abort_reason=l4.get("crm_reasoning", "Score too low"),
                )

            elif (
                self.config["pipeline"]["crm_reloop_min"]
                <= crm_score
                <= self.config["pipeline"]["crm_reloop_max"]
            ):
                console.print(f"[yellow]CRM Score {crm_score}: Triggering L2b Re-loop[/yellow]")
                relooped = True

                # Determine tools for re-loop
                is_internal = any(
                    kw.lower() in normalized_query.lower()
                    for kw in self.config["tools"]["internal_keywords"]
                )
                enhanced_tools = list(self.config["tools"]["l2b_default"])
                if is_internal:
                    enhanced_tools.append("vertex_ai_search")

                console.print(f"    Tools: {', '.join(enhanced_tools)}")

                l2b_result = await self._run_collaborative_loop(
                    framed_content=converged_draft,
                    tools=enhanced_tools,
                    feedback=l4.get("crm_reasoning", ""),
                )
                total_cycles += l2b_result["cycles"]
                console.print(f"  Re-loop converged in {l2b_result['cycles']} cycles.\n")

                # Re-validate and re-execute
                l3b = await supergrok_validate.validate_draft(
                    l2b_result["final_draft"],
                    spt1,
                    self.config["models"]["l3_grok"],
                    self.api_keys["XAI_API_KEY"],
                )

                l4b = await claude_execute.execute_and_publish(
                    l3b["flagged_draft"],
                    spt2,
                    l3b["execution_flags"],
                    self.config["models"]["l4_claude"],
                    self.api_keys["ANTHROPIC_API_KEY"],
                    self.config["github"],
                    self.api_keys["GITHUB_TOKEN"],
                    self.query_id,
                )

                original_score = crm_score
                crm_score = l4b["crm_score"]
                final_answer = l4b["final_answer"]
                github_url = l4b["github_url"]

                console.print(f"  New CRM Score: [bold]{crm_score}/10[/bold]\n")

                crm_analytics.log_reloop(
                    db_path=self.analytics_db,
                    query_id=self.query_id,
                    before_score=original_score,
                    after_score=crm_score,
                    tools_used=",".join(enhanced_tools),
                )

            # === L5: SuperGrok Repackage (STATIC) ===
            console.print("[yellow]L5: SuperGrok Repackage[/yellow]")
            l5 = await retry_logic.with_retry(
                supergrok_repackage.create_briefing,
                github_url,
                final_answer,
                crm_score,
                self.config["models"]["l5_grok"],
                self.api_keys["XAI_API_KEY"],
            )
            self._track_cost("L5_SuperGrok_Repackage", l5["cost"])
            executive_briefing = l5["briefing"]
            console.print("  Executive briefing ready.\n")

            # === L6: Claude PR Check (DYNAMIC, Optional) ===
            run_l6 = self.config["pipeline"].get("always_pr_check", False)
            if not run_l6 and 4 <= crm_score <= 6:
                run_l6 = True

            if run_l6:
                console.print("[yellow]L6: Claude PR Check (Optional)[/yellow]")
                try:
                    l6 = await retry_logic.with_retry(
                        claude_pr_check.review_pr,
                        github_url,
                        self.config["github"]["repo_name"],
                        self.config["models"]["l6_claude"],
                        self.api_keys["ANTHROPIC_API_KEY"],
                        self.api_keys["GITHUB_TOKEN"],
                    )
                    self._track_cost("L6_Claude_PR", l6["cost"])
                    console.print(f"  PR Check: {l6['verdict'][:50]}...\n")
                except Exception as e:
                    console.print(f"[dim]  PR Check skipped: {e}[/dim]")

            # === L7: SuperGrok Voice (STATIC) ===
            console.print("[yellow]L7: SuperGrok Voice[/yellow]")
            l7 = await retry_logic.with_retry(
                supergrok_voice.generate_voice,
                executive_briefing,
                self.config["models"]["l7_grok"],
                self.api_keys["XAI_API_KEY"],
            )
            self._track_cost("L7_SuperGrok_Voice", l7["cost"])
            voice_script = l7["script"]
            console.print("  Voice briefing ready.\n")

            return self._finalize(
                success=True,
                crm_score=crm_score,
                final_answer=final_answer,
                voice_script=voice_script,
                github_url=github_url,
                relooped=relooped,
                total_cycles=total_cycles,
            )

        except Exception as e:
            console.print(f"\n[bold red]Pipeline Failed: {e}[/bold red]\n")
            import traceback

            traceback.print_exc()
            return self._finalize(success=False, error=str(e))

    async def _run_collaborative_loop(
        self, framed_content: str, tools: list[str] | None = None, feedback: str | None = None
    ) -> dict[str, Any]:
        """
        L2: Gemini <-> GPT collaborative loop until convergence.

        Returns:
            {
                'final_draft': str,
                'cycles': int,
                'converged': bool
            }
        """
        current_draft = framed_content
        cycles = 0
        max_cycles = self.config["pipeline"]["HARD_CAP_CYCLES"]
        convergence_signal = self.config["pipeline"]["convergence_signal"]

        while cycles < max_cycles:
            cycles += 1

            # Gemini refines
            gemini_result = await gemini_refine.refine(
                current_draft,
                tools=tools,
                feedback=feedback if cycles == 1 else None,
                model=self.config["models"]["l2_gemini"],
                api_key=self.api_keys["GOOGLE_API_KEY"],
            )
            self._track_cost(f"L2_Gemini_C{cycles}", gemini_result["cost"])

            # GPT refines Gemini's output
            gpt_result = await gpt5_refine.refine(
                gemini_result["draft"],
                previous_draft=current_draft,
                model=self.config["models"]["l2_gpt"],
                api_key=self.api_keys["OPENAI_API_KEY"],
            )
            self._track_cost(f"L2_GPT_C{cycles}", gpt_result["cost"])

            # Check convergence
            if gpt_result.get("convergence_signal") == convergence_signal:
                return {"final_draft": gpt_result["draft"], "cycles": cycles, "converged": True}

            current_draft = gpt_result["draft"]

        # Hit max cycles
        return {"final_draft": current_draft, "cycles": cycles, "converged": False}

    def _finalize(self, **kwargs) -> PipelineResult:
        """Create final result and save to analytics"""
        result = PipelineResult(
            query_id=self.query_id,
            total_cost=sum(self.costs.values()),
            costs_breakdown=self.costs.copy(),
            **kwargs,
        )

        # Log to analytics
        crm_analytics.log_run(
            db_path=self.analytics_db,
            query_id=self.query_id,
            success=result.success,
            crm_score=result.crm_score,
            total_cost=result.total_cost,
            cycles=result.total_cycles,
            relooped=result.relooped,
        )

        # Print summary
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        console.print(f"\n{'=' * 50}")
        console.print(f"[cyan]Query ID:[/cyan] {self.query_id}")
        console.print(f"[cyan]Success:[/cyan] {result.success}")
        console.print(f"[cyan]CRM Score:[/cyan] {result.crm_score}/10")
        console.print(f"[cyan]Total Cost:[/cyan] ${result.total_cost:.4f}")
        console.print(f"[cyan]Elapsed:[/cyan] {elapsed:.1f}s")
        console.print(f"{'=' * 50}\n")

        return result
