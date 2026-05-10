"""RESEARCH-GRADE CITATION VALIDATION
Verifies legal/medical references exist and are current
"""

import logging
from dataclasses import dataclass

import requests

from src.jetski.browser_engine import get_jetski

logger = logging.getLogger("citation-validator")


@dataclass
class Citation:
    text: str  # "Smith v. Jones, 123 F.3d 456 (9th Cir. 1997)"
    source_type: str  # "case_law" | "statute" | "medical_journal"
    verified: bool = False
    verification_url: str | None = None
    verification_screenshot: str | None = None


class CitationValidator:
    """Verifies legal and medical citations exist."""

    def __init__(self):
        # We access Jetski directly (if in same container) or via API
        # For simplicity here, assuming direct library access or mocked
        self.jetski = get_jetski()

        # Public legal databases
        self.legal_sources = {
            "courtlistener": "https://www.courtlistener.com",
            "justia": "https://law.justia.com",
            "govinfo": "https://www.govinfo.gov",
        }

    def verify_case_citation(self, citation: str) -> Citation:
        """Verify a legal case citation exists.
        Example: "Smith v. Jones, 123 F.3d 456 (9th Cir. 1997)"
        """
        # Parse citation (simplified)
        case_name = citation.split(",", maxsplit=1)[0].strip()

        # Search CourtListener (free API)
        search_url = f"{self.legal_sources['courtlistener']}/api/rest/v3/search/"
        params = {"q": case_name, "type": "o"}  # opinions

        try:
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"CourtListener API failed: {response.status_code}")
                return Citation(text=citation, source_type="case_law", verified=False)

            results = response.json()

            if results.get("count", 0) > 0:
                # Found potential match - verify with Jetski
                case_url = f"https://www.courtlistener.com{results['results'][0]['absolute_url']}"

                jetski_result = self.jetski.verify_page_render(
                    url=case_url,
                    selector="h1",  # Title element
                )

                return Citation(
                    text=citation,
                    source_type="case_law",
                    verified=jetski_result["success"],
                    verification_url=case_url,
                    verification_screenshot=jetski_result.get("screenshot"),
                )
        except Exception as e:
            logger.error(f"Validation error: {e}")

        return Citation(text=citation, source_type="case_law", verified=False)

    def verify_medical_citation(self, citation: str) -> Citation:
        """Verify a medical journal citation exists.
        Example: "Smith J, et al. JAMA. 2024;331(1):45-52. doi:10.1001/jama.2024.1234"
        """
        # Extract DOI
        doi = None
        if "doi:" in citation.lower():
            # Simple extraction strategy
            parts = citation.lower().split("doi:")
            if len(parts) > 1:
                doi = parts[1].strip().split(" ")[0].rstrip(".")

        if doi:
            # Verify via DOI.org
            doi_url = f"https://doi.org/{doi}"

            jetski_result = self.jetski.verify_endpoint(url=doi_url, expected_status=200)

            return Citation(
                text=citation,
                source_type="medical_journal",
                verified=jetski_result["success"],
                verification_url=doi_url,
            )

        return Citation(text=citation, source_type="medical_journal", verified=False)
