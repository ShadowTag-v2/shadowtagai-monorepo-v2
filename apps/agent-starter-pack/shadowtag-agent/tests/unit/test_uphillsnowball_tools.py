# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for UphillSnowball legal domain tools."""

import json

from app.agent import (
    uphillsnowball_billing_tracker,
    uphillsnowball_case_intake,
    uphillsnowball_document_analysis,
    uphillsnowball_sanctions_check,
)


class TestUphillSnowballCaseIntake:
    """Tests for the case intake tool."""

    def test_high_risk_detection(self):
        """Sanctions keyword triggers HIGH risk level."""
        result = json.loads(uphillsnowball_case_intake(
            "Client is facing sanctions from federal regulators",
        ))
        assert result["risk_level"] == "HIGH"
        assert "sanctions" in result["detected_practice_areas"]
        assert result["privilege_status"] == "PROTECTED"
        assert result["billable"] is True

    def test_medium_risk_detection(self):
        """Breach keyword triggers MEDIUM risk level."""
        result = json.loads(uphillsnowball_case_intake(
            "Contract breach dispute with vendor over deliverables",
        ))
        assert result["risk_level"] == "MEDIUM"
        assert "breach" in result["detected_practice_areas"]

    def test_low_risk_default(self):
        """General inquiry defaults to LOW risk."""
        result = json.loads(uphillsnowball_case_intake(
            "Need help with a standard contract review",
        ))
        assert result["risk_level"] == "LOW"

    def test_intake_id_format(self):
        """Intake ID follows USI-YYYYMMDDHHMMSS format."""
        result = json.loads(uphillsnowball_case_intake("General question"))
        assert result["intake_id"].startswith("USI-")
        assert len(result["intake_id"]) > 10

    def test_summary_truncation(self):
        """Client summary is truncated to 500 chars."""
        long_desc = "x" * 1000
        result = json.loads(uphillsnowball_case_intake(long_desc))
        assert len(result["client_summary"]) == 500


class TestUphillSnowballSanctionsCheck:
    """Tests for the sanctions screening tool."""

    def test_us_jurisdiction_default(self):
        """US jurisdiction is default and checks OFAC databases."""
        result = json.loads(uphillsnowball_sanctions_check("Acme Corp"))
        assert result["jurisdiction"] == "US"
        assert "OFAC-SDN" in result["databases_checked"]
        assert result["match_status"] == "NO_MATCH"

    def test_eu_jurisdiction(self):
        """EU jurisdiction checks EU-CONSOLIDATED databases."""
        result = json.loads(uphillsnowball_sanctions_check(
            "Euro Trading GmbH", jurisdiction="EU",
        ))
        assert result["jurisdiction"] == "EU"
        assert "EU-CONSOLIDATED" in result["databases_checked"]

    def test_screening_id_format(self):
        """Screening ID follows SCR-YYYYMMDDHHMMSS format."""
        result = json.loads(uphillsnowball_sanctions_check("Test Entity"))
        assert result["screening_id"].startswith("SCR-")

    def test_unknown_jurisdiction_fallback(self):
        """Unknown jurisdiction falls back to US databases."""
        result = json.loads(uphillsnowball_sanctions_check(
            "Entity", jurisdiction="ZZ",
        ))
        assert "OFAC-SDN" in result["databases_checked"]


class TestUphillSnowballDocumentAnalysis:
    """Tests for the document analysis tool."""

    def test_risk_detection(self):
        """Detects indemnification risk pattern."""
        doc = "The party shall indemnify and hold harmless the other party."
        result = json.loads(uphillsnowball_document_analysis(doc))
        assert result["findings_count"] >= 2
        assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert result["privilege_status"] == "PROTECTED"

    def test_no_findings(self):
        """Clean document yields zero findings."""
        result = json.loads(uphillsnowball_document_analysis(
            "This is a simple agreement between two parties.",
        ))
        assert result["findings_count"] == 0
        assert result["risk_score"] == 0
        assert result["risk_level"] == "LOW"

    def test_high_risk_score_cap(self):
        """Risk score caps at 100."""
        doc = (
            "indemnify hold harmless limitation of liability "
            "force majeure termination arbitration waiver "
            "non-compete non-solicitation confidentiality "
            "extra terms more clauses"
        )
        result = json.loads(uphillsnowball_document_analysis(doc))
        assert result["risk_score"] <= 100

    def test_analysis_type_passthrough(self):
        """Analysis type is correctly recorded."""
        result = json.loads(uphillsnowball_document_analysis(
            "Test document", analysis_type="compliance",
        ))
        assert result["type"] == "compliance"


class TestUphillSnowballBillingTracker:
    """Tests for the billing tracker tool."""

    def test_basic_entry(self):
        """Creates a valid billing entry."""
        result = json.loads(uphillsnowball_billing_tracker(
            matter_id="MTR-2026-001",
            activity="Research on case precedents",
            duration_minutes=30,
        ))
        assert result["matter_id"] == "MTR-2026-001"
        assert result["duration_minutes"] == 30
        assert result["currency"] == "USD"
        assert result["status"] == "PENDING_REVIEW"

    def test_rate_category_detection(self):
        """Research activity maps to category A."""
        result = json.loads(uphillsnowball_billing_tracker(
            matter_id="MTR-001",
            activity="Legal research",
            duration_minutes=60,
        ))
        assert result["rate_category"] == "A"
        assert result["ledes_code"] == "L110"

    def test_cost_calculation(self):
        """30 minutes at $149/hr = $74.50."""
        result = json.loads(uphillsnowball_billing_tracker(
            matter_id="MTR-001",
            activity="Document review",
            duration_minutes=30,
        ))
        assert result["estimated_cost"] == 74.5

    def test_entry_id_format(self):
        """Entry ID follows BIL-YYYYMMDDHHMMSS format."""
        result = json.loads(uphillsnowball_billing_tracker(
            matter_id="MTR-001",
            activity="Test activity",
        ))
        assert result["entry_id"].startswith("BIL-")
