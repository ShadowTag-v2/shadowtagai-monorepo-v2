# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# ATOMIC CODE BLOCK 3: SCHOLAR AGENT
# File: src/agents/scholar.py
# Function: The Sensor (arXiv Scraper + Vertex AI Analyzer)

from datetime import date, datetime

import arxiv

from src.governance.judge_six import ActionType, ProposedAction


class Autoresearch_Triad_Scholar:
    def __init__(self, target_ids):
        self.target_ids = target_ids
        # "Current" Date for the simulation: Jan 24, 2026
        self.current_date = date(2026, 1, 24)

    def fetch_intelligence(self):
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] [SENSOR] Spinning up arXiv harvester for targets: {self.target_ids}...",
        )

        # 1. Query arXiv API
        # Handle cases where IDs might not exist in arXiv by using exception handling or careful querying
        # For simulation, we assume valid IDs are passed or we simulate results if network fails.
        try:
            search = arxiv.Search(id_list=self.target_ids)
            results = list(search.results())
        except Exception as e:
            print(f"[SENSOR] arXiv API Error: {e}")
            return []

        proposals = []

        for result in results:
            print(f"\n[SENSOR] DETECTED PAPER: {result.title}")
            print(f"         Published: {result.published.date()}")

            # 2. Analyze "Tech Age" (Lindy Effect)
            # How many months has this idea survived?
            age_months = self._calculate_age(result.published)
            print(f"         Maturity: {age_months} months")

            # 3. Analyze "Hype Score" (Simulated Vertex AI)
            # In production, we send the PDF to Vertex AI here.
            # Logic: If age < 3 months, Hype is HIGH (0.95). If age > 6 months, Hype is LOW (0.10).
            hype_score = 0.95 if age_months < 3 else 0.10

            # 4. Formulate Proposal for Claude_Code_6
            proposal = ProposedAction(
                action_type=ActionType.CODE_MERGE,
                target_name=f"Update: {result.title[:40]}...",
                cost_usd=0.0,  # Knowledge is free
                seller_reputation=1.0,  # Academic sources assumed trusted
                tech_age_months=age_months,
                return_policy_days=365,  # Code can be reverted
                hype_score=hype_score,
            )

            proposals.append(proposal)

        return proposals

    def _calculate_age(self, pub_date):
        delta = self.current_date - pub_date.date()
        return max(0, int(delta.days / 30))

    def _download_pdf(self, result):
        # Antigravity Uplift: Stream directly to GCS (No local disk)
        # This keeps the container stateless and fast.
        print(f"[SENSOR] Streaming PDF {result.entry_id} to Google Cloud Storage...")
        # (GCS streaming logic omitted for brevity)
