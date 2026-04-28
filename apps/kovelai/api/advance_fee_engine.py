# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Advance Fee Engine — State-by-State Rules.

Jurisdiction-aware trust account and advance fee routing logic.
Determines whether a client's advance payment goes to trust or
operating account based on the applicable state bar rules.

Sources:
  - ABA Formal Opinion 505 (advance flat fees → trust by default)
  - California Rule 1.15 (operating exception with disclosure)
  - State-specific bar guidance

Firestore Collection: advance_fee_rules (read-only reference data)

@see ADVANCE_FEE_ENGINE.md — Product specification
@see BUSINESS_PLAN_V2_2.md — Business model impact
"""

from __future__ import annotations

import enum


from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# Fee Routing
# ═══════════════════════════════════════════════════════════


class FeeDestination(enum.StrEnum):
    """Where the advance fee should be deposited."""

    TRUST = "trust"
    OPERATING = "operating"
    TRUST_WITH_EXCEPTION = "trust_with_exception"


class DisclosureRequirement(enum.StrEnum):
    """Required client disclosures for advance fees."""

    NONE = "none"
    WRITTEN_NOTICE = "written_notice"
    SIGNED_AGREEMENT = "signed_agreement"
    TRUST_ACCOUNT_NOTICE = "trust_account_notice"


# ═══════════════════════════════════════════════════════════
# State Rule Model
# ═══════════════════════════════════════════════════════════


class StateAdvanceFeeRule(BaseModel):
    """Rules for a single state's advance fee handling."""

    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    state_name: str = Field(..., description="Full state name")
    default_destination: FeeDestination = Field(
        default=FeeDestination.TRUST,
        description="Default deposit destination for advance fees",
    )
    allows_operating_deposit: bool = Field(
        default=False,
        description="Whether the state allows deposit to operating account",
    )
    operating_conditions: str | None = Field(
        None,
        description="Conditions under which operating deposit is allowed",
    )
    disclosure_required: DisclosureRequirement = Field(
        default=DisclosureRequirement.TRUST_ACCOUNT_NOTICE,
        description="Disclosure requirements for advance fees",
    )
    refund_required: bool = Field(
        default=True,
        description="Whether unearned portions must be refunded",
    )
    governing_rule: str = Field(
        ...,
        description="The state bar rule governing advance fees",
    )
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# State Rules Database (Initial Entries)
# ═══════════════════════════════════════════════════════════


STATE_RULES: dict[str, StateAdvanceFeeRule] = {
    "CA": StateAdvanceFeeRule(
        state="CA",
        state_name="California",
        default_destination=FeeDestination.TRUST_WITH_EXCEPTION,
        allows_operating_deposit=True,
        operating_conditions="Attorney provides required written disclosures per Rule 1.15",
        disclosure_required=DisclosureRequirement.SIGNED_AGREEMENT,
        refund_required=True,
        governing_rule="California Rule of Professional Conduct 1.15",
        notes="California uniquely allows flat fees to operating account with proper disclosure",
    ),
    "NY": StateAdvanceFeeRule(
        state="NY",
        state_name="New York",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="NY Rules of Professional Conduct Rule 1.15(b)",
        notes="Advance fees must go to trust. Draw down as earned.",
    ),
    "TX": StateAdvanceFeeRule(
        state="TX",
        state_name="Texas",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.TRUST_ACCOUNT_NOTICE,
        refund_required=True,
        governing_rule="Texas Disciplinary Rules of Professional Conduct Rule 1.14",
    ),
    "FL": StateAdvanceFeeRule(
        state="FL",
        state_name="Florida",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="Florida Bar Rule 5-1.1",
        notes="Flat fees are advances that must go to trust until earned.",
    ),
    "IL": StateAdvanceFeeRule(
        state="IL",
        state_name="Illinois",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="Illinois Rule of Professional Conduct 1.15",
    ),
    "PA": StateAdvanceFeeRule(
        state="PA",
        state_name="Pennsylvania",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.TRUST_ACCOUNT_NOTICE,
        refund_required=True,
        governing_rule="Pennsylvania Rule of Professional Conduct 1.15",
    ),
    "OH": StateAdvanceFeeRule(
        state="OH",
        state_name="Ohio",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="Ohio Rule of Professional Conduct 1.15",
    ),
    "GA": StateAdvanceFeeRule(
        state="GA",
        state_name="Georgia",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="Georgia Rule of Professional Conduct 1.15",
    ),
    "WA": StateAdvanceFeeRule(
        state="WA",
        state_name="Washington",
        default_destination=FeeDestination.TRUST,
        allows_operating_deposit=False,
        disclosure_required=DisclosureRequirement.WRITTEN_NOTICE,
        refund_required=True,
        governing_rule="Washington RPC 1.15A",
    ),
    "CO": StateAdvanceFeeRule(
        state="CO",
        state_name="Colorado",
        default_destination=FeeDestination.TRUST_WITH_EXCEPTION,
        allows_operating_deposit=True,
        operating_conditions="Fixed fee with written notice that it is 'earned on receipt'",
        disclosure_required=DisclosureRequirement.SIGNED_AGREEMENT,
        refund_required=True,
        governing_rule="Colorado Rule of Professional Conduct 1.15D",
        notes="Colorado follows a modified ABA approach allowing earned-on-receipt with disclosure",
    ),
    # ─── Remaining states (ABA Model Rules baseline) ──────────
    "AL": StateAdvanceFeeRule(
        state="AL",
        state_name="Alabama",
        governing_rule="Alabama RPC 1.15",
    ),
    "AK": StateAdvanceFeeRule(
        state="AK",
        state_name="Alaska",
        governing_rule="Alaska RPC 1.15",
    ),
    "AZ": StateAdvanceFeeRule(
        state="AZ",
        state_name="Arizona",
        default_destination=FeeDestination.TRUST_WITH_EXCEPTION,
        allows_operating_deposit=True,
        operating_conditions="Flat fee with written disclosure may be deposited to operating",
        disclosure_required=DisclosureRequirement.SIGNED_AGREEMENT,
        governing_rule="Arizona ER 1.15",
        notes="Arizona allows earned-on-receipt flat fees with proper written agreement",
    ),
    "AR": StateAdvanceFeeRule(
        state="AR",
        state_name="Arkansas",
        governing_rule="Arkansas RPC 1.15",
    ),
    "CT": StateAdvanceFeeRule(
        state="CT",
        state_name="Connecticut",
        governing_rule="Connecticut RPC 1.15",
    ),
    "DE": StateAdvanceFeeRule(
        state="DE",
        state_name="Delaware",
        governing_rule="Delaware RPC 1.15",
    ),
    "DC": StateAdvanceFeeRule(
        state="DC",
        state_name="District of Columbia",
        governing_rule="DC Rule of Professional Conduct 1.15",
    ),
    "HI": StateAdvanceFeeRule(
        state="HI",
        state_name="Hawaii",
        governing_rule="Hawaii RPC 1.15",
    ),
    "ID": StateAdvanceFeeRule(
        state="ID",
        state_name="Idaho",
        governing_rule="Idaho RPC 1.15",
    ),
    "IN": StateAdvanceFeeRule(
        state="IN",
        state_name="Indiana",
        governing_rule="Indiana RPC 1.15",
    ),
    "IA": StateAdvanceFeeRule(
        state="IA",
        state_name="Iowa",
        governing_rule="Iowa RPC 32:1.15",
    ),
    "KS": StateAdvanceFeeRule(
        state="KS",
        state_name="Kansas",
        default_destination=FeeDestination.TRUST_WITH_EXCEPTION,
        allows_operating_deposit=True,
        operating_conditions="Flat fee deemed earned on receipt with written agreement",
        disclosure_required=DisclosureRequirement.SIGNED_AGREEMENT,
        governing_rule="Kansas RPC 1.15",
        notes="Kansas adopted earned-on-receipt rule for flat fees",
    ),
    "KY": StateAdvanceFeeRule(
        state="KY",
        state_name="Kentucky",
        governing_rule="Kentucky SCR 3.130(1.15)",
    ),
    "LA": StateAdvanceFeeRule(
        state="LA",
        state_name="Louisiana",
        governing_rule="Louisiana RPC 1.15",
    ),
    "ME": StateAdvanceFeeRule(
        state="ME",
        state_name="Maine",
        governing_rule="Maine RPC 1.15",
    ),
    "MD": StateAdvanceFeeRule(
        state="MD",
        state_name="Maryland",
        governing_rule="Maryland Attorneys' Rules of Professional Conduct 19-301.15",
    ),
    "MA": StateAdvanceFeeRule(
        state="MA",
        state_name="Massachusetts",
        governing_rule="Massachusetts RPC 1.15",
        notes="Massachusetts requires all advance fees to be deposited in IOLTA trust",
    ),
    "MI": StateAdvanceFeeRule(
        state="MI",
        state_name="Michigan",
        governing_rule="Michigan RPC 1.15",
    ),
    "MN": StateAdvanceFeeRule(
        state="MN",
        state_name="Minnesota",
        governing_rule="Minnesota RPC 1.15",
    ),
    "MS": StateAdvanceFeeRule(
        state="MS",
        state_name="Mississippi",
        governing_rule="Mississippi RPC 1.15",
    ),
    "MO": StateAdvanceFeeRule(
        state="MO",
        state_name="Missouri",
        governing_rule="Missouri RPC 4-1.15",
    ),
    "MT": StateAdvanceFeeRule(
        state="MT",
        state_name="Montana",
        governing_rule="Montana RPC 1.15",
    ),
    "NE": StateAdvanceFeeRule(
        state="NE",
        state_name="Nebraska",
        governing_rule="Nebraska CT R Prof Cond 1.15",
    ),
    "NV": StateAdvanceFeeRule(
        state="NV",
        state_name="Nevada",
        governing_rule="Nevada RPC 1.15",
    ),
    "NH": StateAdvanceFeeRule(
        state="NH",
        state_name="New Hampshire",
        governing_rule="New Hampshire RPC 1.15",
    ),
    "NJ": StateAdvanceFeeRule(
        state="NJ",
        state_name="New Jersey",
        governing_rule="New Jersey RPC 1.15",
        notes="NJ requires detailed trust account recordkeeping (R. 1:21-6)",
    ),
    "NM": StateAdvanceFeeRule(
        state="NM",
        state_name="New Mexico",
        governing_rule="New Mexico RPC 16-115",
    ),
    "NC": StateAdvanceFeeRule(
        state="NC",
        state_name="North Carolina",
        governing_rule="North Carolina RPC 1.15",
        notes="NC requires quarterly trust account reconciliation",
    ),
    "ND": StateAdvanceFeeRule(
        state="ND",
        state_name="North Dakota",
        governing_rule="North Dakota RPC 1.15",
    ),
    "OK": StateAdvanceFeeRule(
        state="OK",
        state_name="Oklahoma",
        governing_rule="Oklahoma RPC 1.15",
    ),
    "OR": StateAdvanceFeeRule(
        state="OR",
        state_name="Oregon",
        governing_rule="Oregon RPC 1.15",
        notes="Oregon allows earned-on-receipt for flat fees with proper disclosure",
        default_destination=FeeDestination.TRUST_WITH_EXCEPTION,
        allows_operating_deposit=True,
        operating_conditions="Flat fee with written agreement specifying earned on receipt",
        disclosure_required=DisclosureRequirement.SIGNED_AGREEMENT,
    ),
    "RI": StateAdvanceFeeRule(
        state="RI",
        state_name="Rhode Island",
        governing_rule="Rhode Island RPC 1.15",
    ),
    "SC": StateAdvanceFeeRule(
        state="SC",
        state_name="South Carolina",
        governing_rule="South Carolina RPC 1.15",
    ),
    "SD": StateAdvanceFeeRule(
        state="SD",
        state_name="South Dakota",
        governing_rule="South Dakota RPC 1.15",
    ),
    "TN": StateAdvanceFeeRule(
        state="TN",
        state_name="Tennessee",
        governing_rule="Tennessee RPC 1.15",
    ),
    "UT": StateAdvanceFeeRule(
        state="UT",
        state_name="Utah",
        governing_rule="Utah RPC 1.15",
    ),
    "VT": StateAdvanceFeeRule(
        state="VT",
        state_name="Vermont",
        governing_rule="Vermont RPC 1.15",
    ),
    "VA": StateAdvanceFeeRule(
        state="VA",
        state_name="Virginia",
        governing_rule="Virginia RPC 1.15",
        notes="Virginia LEO opinions require trust deposit for all advance fees",
    ),
    "WV": StateAdvanceFeeRule(
        state="WV",
        state_name="West Virginia",
        governing_rule="West Virginia RPC 1.15",
    ),
    "WI": StateAdvanceFeeRule(
        state="WI",
        state_name="Wisconsin",
        governing_rule="Wisconsin SCR 20:1.15",
    ),
    "WY": StateAdvanceFeeRule(
        state="WY",
        state_name="Wyoming",
        governing_rule="Wyoming RPC 1.15",
    ),
}


# ═══════════════════════════════════════════════════════════
# Fee Routing Engine
# ═══════════════════════════════════════════════════════════


class FeeRoutingResult(BaseModel):
    """Result of the advance fee routing decision."""

    destination: FeeDestination
    state: str
    state_name: str
    disclosure_required: DisclosureRequirement
    refund_required: bool
    governing_rule: str
    operating_conditions: str | None = None
    warning: str | None = None


def route_advance_fee(
    state_code: str,
    fee_type: str = "flat",
    has_signed_agreement: bool = False,
) -> FeeRoutingResult:
    """
    Route an advance fee to the correct account based on jurisdiction.

    Args:
        state_code: Two-letter state code (e.g., "CA", "NY")
        fee_type: Type of fee ("flat", "retainer", "advance")
        has_signed_agreement: Whether client has signed fee agreement

    Returns:
        FeeRoutingResult with routing decision and compliance info

    Raises:
        ValueError: If state code is not recognized
    """
    state_code = state_code.upper()
    rule = STATE_RULES.get(state_code)

    if rule is None:
        # Default to ABA Formal Opinion 505: trust account
        return FeeRoutingResult(
            destination=FeeDestination.TRUST,
            state=state_code,
            state_name=f"Unknown ({state_code})",
            disclosure_required=DisclosureRequirement.TRUST_ACCOUNT_NOTICE,
            refund_required=True,
            governing_rule="ABA Formal Opinion 505 (default)",
            warning=(
                f"State '{state_code}' not in rules database. "
                "Defaulting to ABA Formal Opinion 505 (trust account). "
                "Verify with local bar association."
            ),
        )

    # Determine actual routing
    destination = rule.default_destination
    warning = None

    if rule.allows_operating_deposit:
        if not has_signed_agreement:
            destination = FeeDestination.TRUST
            warning = f"{rule.state_name} allows operating deposit but requires signed agreement. Routing to trust until agreement is signed."
        else:
            destination = FeeDestination.OPERATING

    return FeeRoutingResult(
        destination=destination,
        state=rule.state,
        state_name=rule.state_name,
        disclosure_required=rule.disclosure_required,
        refund_required=rule.refund_required,
        governing_rule=rule.governing_rule,
        operating_conditions=rule.operating_conditions,
        warning=warning,
    )


def get_all_state_rules() -> list[StateAdvanceFeeRule]:
    """Return all configured state rules."""
    return list(STATE_RULES.values())


def get_state_rule(state_code: str) -> StateAdvanceFeeRule | None:
    """Get the rule for a specific state."""
    return STATE_RULES.get(state_code.upper())
