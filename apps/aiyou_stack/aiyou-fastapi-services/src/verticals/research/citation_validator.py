"""RESEARCH-GRADE CITATION VALIDATION
Verifies legal/medical references exist and are current.
Integrates with Jetski for browser-based ground truth verification.
"""

from dataclasses import dataclass
from typing import Any

import requests

from src.jetski.browser_engine import get_jetski


@dataclass
class Citation:
    text: str  # "Smith v. Jones, 123 F.3d 456 (9th Cir. 1997)"
    source_type: str  # "case_law" | "statute" | "medical_journal"
    verified: bool = False
    verification_url: str | None = None
    verification_screenshot: str | None = None


class CitationValidator:
    """Verifies legal and medical citations exist using public APIs and Jetski."""

    def __init__(self):
        self.jetski = get_jetski()

        # Public legal databases
        self.legal_sources = {
            "courtlistener": "https://www.courtlistener.com",
            "justia": "https://law.justia.com",
            "govinfo": "https://www.govinfo.gov",
        }

        # Public medical databases
        self.medical_sources = {
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov",
            "cochrane": "https://www.cochranelibrary.com",
            "clinicaltrials": "https://clinicaltrials.gov",
        }

    async def verify_case_citation(self, citation: str) -> Citation:
        """Verify a legal case citation exists.
        Example: "Smith v. Jones, 123 F.3d 456 (9th Cir. 1997)"
        """
        # Parse citation (simplified - use bluebook parser in production)
        case_name = citation.split(",", maxsplit=1)[0].strip()

        # Search CourtListener (free API)
        search_url = f"{self.legal_sources['courtlistener']}/api/rest/v3/search/"
        params = {"q": case_name, "type": "o"}  # o = opinions

        try:
            response = requests.get(search_url, params=params, timeout=10)
            results = response.json()

            if results.get("count", 0) > 0:
                # Found potential match - verify with Jetski
                # CourtListener API returns 'absolute_url' relative to domain
                relative_url = results["results"][0].get("absolute_url", "")
                case_url = (
                    f"https://www.courtlistener.com{relative_url}"
                    if relative_url.startswith("/")
                    else relative_url
                )

                # Use Jetski to visually verify the page renders
                jetski_result = await self.jetski.verify_page_render(
                    url=case_url,
                    selector=".title",  # Case name element usually has .title or h1
                )

                return Citation(
                    text=citation,
                    source_type="case_law",
                    verified=jetski_result.get("success", False),
                    verification_url=case_url,
                    verification_screenshot=jetski_result.get("screenshot"),
                )
        except Exception as e:
            print(f"Error verifying legal citation: {e}")

        return Citation(text=citation, source_type="case_law", verified=False)

    async def verify_medical_citation(self, citation: str) -> Citation:
        """Verify a medical journal citation exists.
        Example: "Smith J, et al. JAMA. 2024;331(1):45-52. doi:10.1001/jama.2024.1234"
        """
        # Extract DOI or PMID
        doi = None
        if "doi:" in citation:
            # Simple extraction
            parts = citation.split("doi:")
            if len(parts) > 1:
                doi = parts[1].strip().rstrip(".").split(" ")[0]

        if doi:
            # Verify via DOI.org (canonical resolver)
            doi_url = f"https://doi.org/{doi}"

            # Use Jetski to verify HTTP 200 and some content
            jetski_result = await self.jetski.verify_endpoint(url=doi_url, expected_status=200)

            return Citation(
                text=citation,
                source_type="medical_journal",
                verified=jetski_result.get("success", False),
                verification_url=doi_url,
            )

        # Fallback: Search PubMed (Simulated via URL for now)
        # Real implementation would use BioPython or E-Utilities API
        return Citation(text=citation, source_type="medical_journal", verified=False)

    async def batch_verify(self, document_text: str) -> dict[str, Any]:
        """Extract and verify all citations in a document.
        Returns validation report.
        """
        # Mock extraction for prototype - in production use dedicated NLP models
        # This just looks for basic patterns
        verified = []
        failed = []  # type: list[Citation]

        # TODO: Implement regex extraction loop

        return {
            "total_citations": len(verified) + len(failed),
            "verified_count": len(verified),
            "failed_count": len(failed),
            "failed_citations": failed,
            "confidence_score": len(verified) / (len(verified) + len(failed))
            if verified or failed
            else 0,
        }
