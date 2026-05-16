# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Compliance-First SDR Agent
Job: Generate B2B leads without GDPR/CAN-SPAM violations.

Workflow:
1. User query: "Find 100 German fintech CTOs"
2. JR Engine validates budget/purpose
3. Agent scrapes LinkedIn/Apollo/Clearbit
4. Judge #6 filters personal emails, flags EU contacts
5. Output: N approved + M blocked + audit PDF

Pricing: $0.10/approved lead
Timeline: 7-day MVP
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..core.agent_pattern import AgentResult, AgentTask, PnklnAgent
from ..core.jr_engine import Reason


class LeadStatus(Enum):
  """Status of a lead."""

  APPROVED = "approved"
  BLOCKED = "blocked"
  NEEDS_REVIEW = "needs_review"


@dataclass
class Lead:
  """Represents a B2B lead."""

  name: str
  email: str
  company: str
  title: str
  location: str
  source: str
  linkedin_url: str | None = None
  phone: str | None = None
  status: LeadStatus = LeadStatus.NEEDS_REVIEW
  block_reason: str | None = None


@dataclass
class LeadGenerationResult:
  """Result of lead generation."""

  approved_leads: list[Lead]
  blocked_leads: list[Lead]
  needs_review_leads: list[Lead]
  total_cost_usd: float
  audit_report: dict[str, Any]


class ComplianceSDRAgent(PnklnAgent):
  """
  Compliance-First SDR Agent for B2B lead generation.

  Features:
  - GDPR/CAN-SPAM enforcement
  - Personal email filtering
  - EU contact flagging
  - Audit trail generation
  - Per-lead pricing ($0.10/approved)
  """

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.price_per_approved_lead = 0.10

    # EU country codes for GDPR compliance
    self.eu_countries = {
      "DE",
      "FR",
      "IT",
      "ES",
      "NL",
      "BE",
      "AT",
      "PL",
      "RO",
      "CZ",
      "PT",
      "HU",
      "SE",
      "GR",
      "BG",
      "DK",
      "FI",
      "SK",
      "IE",
      "HR",
      "LT",
      "SI",
      "LV",
      "EE",
      "CY",
      "LU",
      "MT",
    }

    # Personal email domains (GDPR risk)
    self.personal_email_domains = {
      "gmail.com",
      "yahoo.com",
      "hotmail.com",
      "outlook.com",
      "aol.com",
      "icloud.com",
      "mail.com",
      "protonmail.com",
      "gmx.com",
      "yandex.com",
      "zoho.com",
    }

    # Corporate email patterns (lower GDPR risk)
    self.corporate_patterns = [
      r".*@(?!(" + "|".join(self.personal_email_domains) + r"))[\w\-]+\.[a-z]{2,}$"
    ]

  def generate_leads(
    self,
    query: str,
    target_count: int,
    customer_id: str,
    context: dict[str, Any] | None = None,
  ) -> AgentResult:
    """
    Generate leads with compliance enforcement.

    Args:
        query: Search query (e.g., "German fintech CTOs")
        target_count: Number of leads to generate
        customer_id: Customer ID for attribution
        context: Additional context (budget, consent status, etc.)

    Returns:
        AgentResult with LeadGenerationResult
    """
    context = context or {}
    cost_estimate = target_count * self.price_per_approved_lead

    task = AgentTask(
      intent=f"Generate {target_count} leads: {query}",
      customer_id=customer_id,
      context={
        **context,
        "query": query,
        "target_count": target_count,
        "is_lead_generation": True,
      },
      cost_estimate_usd=cost_estimate,
      business_value=f"B2B lead generation for customer {customer_id}",
      expected_outcome=f"{target_count} GDPR/CAN-SPAM compliant leads",
    )

    return self.execute(task)

  def _build_reasons(self, task: AgentTask) -> list[Reason]:
    """Build reasons specific to lead generation."""
    target_count = task.context.get("target_count", 100)
    query = task.context.get("query", "")

    # Check if query mentions EU countries
    eu_mentioned = any(country in query.upper() for country in self.eu_countries)

    risk_probability = 0.3 if eu_mentioned else 0.1
    risk_severity = 0.5 if eu_mentioned else 0.2

    return [
      Reason(
        justification=f"B2B lead generation query: {query}",
        risk_probability=risk_probability,
        risk_severity=risk_severity,
        mitigation_strategy="Judge #6 GDPR/CAN-SPAM enforcement + personal email filtering",
      ),
      Reason(
        justification=f"Estimated cost: ${task.cost_estimate_usd:.2f} for {target_count} leads",
        risk_probability=0.1,
        risk_severity=0.1,
        mitigation_strategy="Per-lead pricing ensures cost control",
      ),
    ]

  def _execute_task(
    self, task: AgentTask, constraints: dict[str, Any]
  ) -> LeadGenerationResult:
    """
    Execute lead generation with compliance filtering.

    NOTE: This is a mock implementation. In production, this would:
    1. Query LinkedIn Sales Navigator, Apollo.io, Clearbit, etc.
    2. Parse and normalize results
    3. Apply GDPR/CAN-SPAM filters
    4. Return compliant leads
    """
    query = task.context.get("query", "")
    target_count = task.context.get("target_count", 100)

    # Mock lead generation (replace with actual API calls)
    raw_leads = self._mock_lead_scraping(query, target_count)

    # Filter leads for compliance
    approved_leads = []
    blocked_leads = []
    needs_review_leads = []

    for lead in raw_leads:
      # Check if lead is from EU
      is_eu = self._is_eu_lead(lead)

      # Check if email is personal
      is_personal_email = self._is_personal_email(lead.email)

      # Apply compliance rules
      if is_eu and is_personal_email:
        # GDPR risk: EU + personal email
        lead.status = LeadStatus.BLOCKED
        lead.block_reason = "EU personal email (GDPR risk) - requires explicit consent"
        blocked_leads.append(lead)
      elif is_personal_email and not task.context.get("allow_personal_emails", False):
        # Personal email without consent
        lead.status = LeadStatus.BLOCKED
        lead.block_reason = "Personal email domain - prefer corporate email"
        blocked_leads.append(lead)
      elif is_eu and not task.context.get("gdpr_consent", False):
        # EU without GDPR consent - needs review
        lead.status = LeadStatus.NEEDS_REVIEW
        lead.block_reason = "EU contact - verify GDPR consent before outreach"
        needs_review_leads.append(lead)
      else:
        # Approved
        lead.status = LeadStatus.APPROVED
        approved_leads.append(lead)

    # Calculate actual cost
    actual_cost = len(approved_leads) * self.price_per_approved_lead

    # Build audit report
    audit_report = {
      "query": query,
      "target_count": target_count,
      "approved_count": len(approved_leads),
      "blocked_count": len(blocked_leads),
      "needs_review_count": len(needs_review_leads),
      "total_cost_usd": actual_cost,
      "price_per_lead": self.price_per_approved_lead,
      "compliance_filters_applied": [
        "EU personal email filtering",
        "GDPR consent validation",
        "Personal vs corporate email classification",
      ],
    }

    return LeadGenerationResult(
      approved_leads=approved_leads,
      blocked_leads=blocked_leads,
      needs_review_leads=needs_review_leads,
      total_cost_usd=actual_cost,
      audit_report=audit_report,
    )

  def _mock_lead_scraping(self, query: str, count: int) -> list[Lead]:
    """
    Mock lead scraping (replace with actual API integration).

    In production, this would integrate with:
    - LinkedIn Sales Navigator
    - Apollo.io
    - Clearbit
    - ZoomInfo
    - Hunter.io
    """
    # Parse query for location/industry hints
    is_german = "german" in query.lower() or "germany" in query.lower()
    is_fintech = "fintech" in query.lower()

    mock_leads = []

    for i in range(min(count, 100)):  # Cap at 100 for demo
      # Generate mock lead data
      if is_german:
        location = "Berlin, Germany"
        country_code = "DE"
      else:
        location = "San Francisco, CA"
        country_code = "US"

      # Mix of personal and corporate emails
      if i % 3 == 0:
        email = f"person{i}@gmail.com"
      else:
        company_domain = f"company{i}.com" if not is_fintech else f"fintech{i}.de"
        email = f"cto{i}@{company_domain}"

      lead = Lead(
        name=f"Person {i}",
        email=email,
        company=f"Company {i}" if not is_fintech else f"Fintech {i}",
        title="CTO" if "cto" in query.lower() else "VP Engineering",
        location=location,
        source="mock_scraper",
        linkedin_url=f"https://linkedin.com/in/person{i}",
      )

      # Store country code in lead for EU detection
      lead.__dict__["country_code"] = country_code

      mock_leads.append(lead)

    return mock_leads

  def _is_eu_lead(self, lead: Lead) -> bool:
    """Check if lead is from EU country."""
    # Check country code if available
    country_code = lead.__dict__.get("country_code", "")
    if country_code in self.eu_countries:
      return True

    # Check location string
    location_upper = lead.location.upper()
    for country in self.eu_countries:
      if country in location_upper:
        return True

    # Check email domain for country TLD
    domain = lead.email.split("@")[-1] if "@" in lead.email else ""
    eu_tlds = [".de", ".fr", ".it", ".es", ".nl", ".be", ".at", ".pl"]
    if any(domain.endswith(tld) for tld in eu_tlds):
      return True

    return False

  def _is_personal_email(self, email: str) -> bool:
    """Check if email is personal (not corporate)."""
    if not email or "@" not in email:
      return True

    domain = email.split("@")[-1].lower()
    return domain in self.personal_email_domains

  def _verify_with_judge_six(
    self, result: LeadGenerationResult, context: dict[str, Any]
  ):
    """Override to verify lead generation result."""
    # Build verification data
    verification_data = {
      "approved_count": len(result.approved_leads),
      "blocked_count": len(result.blocked_leads),
      "total_cost_usd": result.total_cost_usd,
      "leads": [
        {
          "email": lead.email,
          "location": lead.location,
          "status": lead.status.value,
        }
        for lead in result.approved_leads[:10]  # Sample first 10
      ],
    }

    # Add EU customer flags to context for GDPR checks
    verification_context = {
      **context,
      "involves_pii": True,  # Leads always contain PII
      "eu_customer": any(self._is_eu_lead(lead) for lead in result.approved_leads),
      "is_marketing_email": False,  # B2B lead gen, not direct email marketing
    }

    return super()._verify_with_judge_six(verification_data, verification_context)


# Example usage
def example_usage():
  """Example of using Compliance SDR Agent."""
  from ..core.jr_engine import JREngine
  from ..core.judge_six_lite import JudgeSixLite

  # Initialize agent
  jr_engine = JREngine(
    config={
      "max_budget_per_action": 100.0,
      "require_human_approval_above": 1000.0,
    }
  )

  judge_six = JudgeSixLite(
    config={
      "sla_p99_ms": 90,
    }
  )

  agent = ComplianceSDRAgent(jr_engine=jr_engine, judge_six=judge_six)

  # Generate leads
  result = agent.generate_leads(
    query="German fintech CTOs",
    target_count=100,
    customer_id="customer_123",
    context={
      "gdpr_consent": False,  # No GDPR consent yet
      "allow_personal_emails": False,  # Block personal emails
    },
  )

  if result.status.name == "COMPLETED":
    # Export audit report
    agent.export_audit_report(format="json")

  elif result.status.name == "ESCALATED":
    pass

  elif result.status.name == "ROLLED_BACK":
    pass


if __name__ == "__main__":
  example_usage()
