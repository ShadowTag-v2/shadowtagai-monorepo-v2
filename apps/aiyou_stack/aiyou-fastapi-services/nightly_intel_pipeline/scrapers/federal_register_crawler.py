"""Federal Register API Crawler
Discovers and ingests regulatory intelligence from 530+ federal agencies
No authentication required - free public API
"""

import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import structlog

from ..config import STORAGE_CONFIG

logger = structlog.get_logger(__name__)


# Federal Register API Configuration
FEDERAL_REGISTER_CONFIG = {
    "base_url": "https://www.federalregister.gov/api/v1",
    "endpoints": {
        "documents": "/documents",
        "public_inspection": "/public-inspection-documents",
        "agencies": "/agencies",
    },
    # PNKLN-aligned agency slugs
    "agencies": [
        # Defense & National Security
        "defense-department",
        "army-department",
        "navy-department",
        "air-force-department",
        "defense-acquisition-regulations-system",
        "defense-logistics-agency",
        # Energy & Grid
        "energy-department",
        "federal-energy-regulatory-commission",
        "nuclear-regulatory-commission",
        # Space & Aerospace
        "national-aeronautics-and-space-administration",
        "federal-aviation-administration",
        "federal-communications-commission",  # Spectrum/satellite
        # Technology & Commerce
        "commerce-department",
        "national-institute-of-standards-and-technology",
        "patent-and-trademark-office",
        "bureau-of-industry-and-security",  # Export controls
        # Homeland Security & Cyber
        "homeland-security-department",
        "cybersecurity-and-infrastructure-security-agency",
        "transportation-security-administration",
        # Health & FDA (SaMD)
        "food-and-drug-administration",
        "health-and-human-services-department",
        # Finance & Treasury
        "treasury-department",
        "securities-and-exchange-commission",
        "commodity-futures-trading-commission",
        # Intelligence (public notices)
        "office-of-the-director-of-national-intelligence",
    ],
    # Document types to track
    "document_types": [
        "RULE",  # Final rules - immediate impact
        "PRORULE",  # Proposed rules - upcoming changes
        "NOTICE",  # General notices
        "PRESDOCU",  # Presidential documents
    ],
    # PNKLN-aligned topic keywords
    "topic_keywords": [
        # AI/ML
        "artificial intelligence",
        "machine learning",
        "autonomous systems",
        "neural network",
        "deep learning",
        "algorithm",
        # Cybersecurity
        "cybersecurity",
        "information security",
        "critical infrastructure",
        "encryption",
        "zero trust",
        "vulnerability",
        # Defense tech
        "defense procurement",
        "defense acquisition",
        "unmanned systems",
        "autonomous weapons",
        "space force",
        "hypersonic",
        # Space
        "satellite",
        "orbital",
        "launch vehicle",
        "spectrum allocation",
        "space debris",
        "remote sensing",
        # Energy
        "grid modernization",
        "energy storage",
        "renewable energy",
        "smart grid",
        "electric vehicle",
        "power systems",
        # Medical devices (SaMD)
        "software as a medical device",
        "digital health",
        "510k",
        "premarket approval",
        "clinical decision support",
        # Export controls
        "export control",
        "deemed export",
        "itar",
        "ear",
        "dual use",
        "controlled technology",
    ],
    "rate_limit": 1.0,  # 1 request per second (respectful)
    "max_results_per_page": 100,
    "max_pages": 5,  # Safety limit
}


@dataclass
class FederalDocument:
    """Represents a Federal Register document"""

    document_number: str
    title: str
    document_type: str
    agency_names: list[str]
    publication_date: datetime
    abstract: str
    html_url: str
    pdf_url: str | None = None
    significant: bool = False
    topics: list[str] = field(default_factory=list)
    docket_ids: list[str] = field(default_factory=list)
    cfr_references: list[str] = field(default_factory=list)
    effective_date: datetime | None = None
    comment_deadline: datetime | None = None
    relevance_score: float = 0.5
    pnkln_vertical: str | None = None


class FederalRegisterCrawler:
    """Federal Register API crawler for regulatory intelligence

    Features:
    - No authentication required
    - Agency-filtered search
    - Topic keyword matching
    - Document type filtering
    - PNKLN vertical classification
    """

    def __init__(self):
        self.config = FEDERAL_REGISTER_CONFIG
        self.base_url = self.config["base_url"]
        self.storage_path = Path(
            STORAGE_CONFIG.get("federal_register", {}).get(
                "path",
                str(Path(STORAGE_CONFIG["briefing_output"]["path"]).parent / "federal_register"),
            ),
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(
            "federal_register_crawler_initialized",
            storage_path=str(self.storage_path),
            agency_count=len(self.config["agencies"]),
            keyword_count=len(self.config["topic_keywords"]),
        )

    def _classify_vertical(self, doc: FederalDocument) -> str:
        """Classify document into PNKLN vertical"""
        text = f"{doc.title} {doc.abstract}".lower()
        agencies = " ".join(doc.agency_names).lower()

        # Vertical classification rules
        if any(x in agencies for x in ["defense", "army", "navy", "air force", "darpa"]):
            return "gov_defense"
        if any(x in agencies for x in ["energy", "ferc", "nuclear"]):
            return "energy"
        if any(x in agencies for x in ["nasa", "faa"]) or "satellite" in text or "orbital" in text:
            return "orbital"
        if any(x in agencies for x in ["fda", "health"]) or "medical device" in text:
            return "digital_mall"  # Healthcare SaaS
        if any(x in text for x in ["autonomous vehicle", "self-driving", "adas"]):
            return "roadmesh"
        if any(x in text for x in ["artificial intelligence", "machine learning", "neural"]):
            return "core_stack"
        if any(x in agencies for x in ["homeland", "cyber"]) or "cybersecurity" in text:
            return "gov_defense"
        return "gov_defense"  # Default for federal

    def _calculate_relevance(self, doc: FederalDocument) -> float:
        """Calculate document relevance to PNKLN business"""
        text = f"{doc.title} {doc.abstract}".lower()

        # Base score
        base_score = 0.3

        # Document type weight
        type_weights = {
            "RULE": 0.15,  # Final rules most actionable
            "PRORULE": 0.12,  # Proposed rules important for planning
            "NOTICE": 0.08,
            "PRESDOCU": 0.20,  # Presidential docs often significant
        }
        base_score += type_weights.get(doc.document_type, 0.05)

        # Significant document bonus
        if doc.significant:
            base_score += 0.15

        # Keyword match bonus
        keyword_matches = sum(1 for kw in self.config["topic_keywords"] if kw.lower() in text)
        keyword_bonus = min(keyword_matches * 0.03, 0.25)
        base_score += keyword_bonus

        # Priority agency bonus
        priority_agencies = [
            "defense-department",
            "energy-department",
            "national-aeronautics-and-space-administration",
            "cybersecurity-and-infrastructure-security-agency",
        ]
        if any(agency in " ".join(doc.agency_names).lower() for agency in priority_agencies):
            base_score += 0.1

        # Recency bonus
        days_old = (datetime.now() - doc.publication_date).days
        if days_old <= 7:
            base_score += 0.1
        elif days_old <= 30:
            base_score += 0.05

        return min(base_score, 1.0)

    async def fetch_documents(
        self,
        days_back: int = 30,
        agency_slugs: list[str] | None = None,
        document_types: list[str] | None = None,
    ) -> list[FederalDocument]:
        """Fetch documents from Federal Register API"""
        documents = []

        agencies = agency_slugs or self.config["agencies"]
        doc_types = document_types or self.config["document_types"]

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        async with httpx.AsyncClient() as client:
            for page in range(1, self.config["max_pages"] + 1):
                try:
                    # Build API request
                    params = {
                        "per_page": self.config["max_results_per_page"],
                        "page": page,
                        "conditions[publication_date][gte]": start_date.strftime("%Y-%m-%d"),
                        "conditions[publication_date][lte]": end_date.strftime("%Y-%m-%d"),
                        "conditions[type][]": doc_types,
                        "order": "newest",
                    }

                    # Add agency filter (API accepts multiple)
                    if agencies:
                        params["conditions[agencies][]"] = agencies[:10]  # API limit

                    # Rate limiting
                    await asyncio.sleep(self.config["rate_limit"])

                    response = await client.get(
                        f"{self.base_url}/documents",
                        params=params,
                        timeout=30.0,
                    )

                    if response.status_code != 200:
                        logger.warning(
                            "federal_register_api_error",
                            status=response.status_code,
                            page=page,
                        )
                        break

                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        break

                    for item in results:
                        doc = self._parse_document(item)
                        if doc:
                            doc.relevance_score = self._calculate_relevance(doc)
                            doc.pnkln_vertical = self._classify_vertical(doc)
                            documents.append(doc)

                    logger.info(
                        "federal_register_page_fetched",
                        page=page,
                        documents=len(results),
                        total=len(documents),
                    )

                    # Check if more pages exist
                    if len(results) < self.config["max_results_per_page"]:
                        break

                except Exception as e:
                    logger.error("federal_register_fetch_error", page=page, error=str(e))
                    break

        # Sort by relevance
        documents.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.info(
            "federal_register_fetch_complete",
            total_documents=len(documents),
            days_back=days_back,
        )

        return documents

    def _parse_document(self, item: dict[str, Any]) -> FederalDocument | None:
        """Parse API response into FederalDocument"""
        try:
            # Parse publication date
            pub_date_str = item.get("publication_date", "")
            pub_date = (
                datetime.strptime(pub_date_str, "%Y-%m-%d") if pub_date_str else datetime.now()
            )

            # Parse effective date if present
            effective_date = None
            if item.get("effective_on"):
                with contextlib.suppress(BaseException):
                    effective_date = datetime.strptime(item["effective_on"], "%Y-%m-%d")

            # Parse comment deadline if present
            comment_deadline = None
            if item.get("comments_close_on"):
                with contextlib.suppress(BaseException):
                    comment_deadline = datetime.strptime(item["comments_close_on"], "%Y-%m-%d")

            return FederalDocument(
                document_number=item.get("document_number", ""),
                title=item.get("title", "Untitled"),
                document_type=item.get("type", "NOTICE"),
                agency_names=[a.get("name", "") for a in item.get("agencies", [])],
                publication_date=pub_date,
                abstract=item.get("abstract", "") or item.get("title", ""),
                html_url=item.get("html_url", ""),
                pdf_url=item.get("pdf_url"),
                significant=item.get("significant", False),
                topics=item.get("topics", []),
                docket_ids=item.get("docket_ids", []),
                cfr_references=[
                    f"{ref.get('title', '')} CFR {ref.get('part', '')}"
                    for ref in item.get("cfr_references", [])
                ],
                effective_date=effective_date,
                comment_deadline=comment_deadline,
            )
        except Exception as e:
            logger.error("document_parse_error", error=str(e))
            return None

    async def search_by_keyword(self, keyword: str, days_back: int = 30) -> list[FederalDocument]:
        """Search Federal Register by keyword"""
        documents = []

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        async with httpx.AsyncClient() as client:
            try:
                await asyncio.sleep(self.config["rate_limit"])

                params = {
                    "per_page": 50,
                    "conditions[term]": keyword,
                    "conditions[publication_date][gte]": start_date.strftime("%Y-%m-%d"),
                    "conditions[publication_date][lte]": end_date.strftime("%Y-%m-%d"),
                    "order": "relevance",
                }

                response = await client.get(
                    f"{self.base_url}/documents",
                    params=params,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("results", []):
                        doc = self._parse_document(item)
                        if doc:
                            doc.relevance_score = self._calculate_relevance(doc)
                            doc.pnkln_vertical = self._classify_vertical(doc)
                            documents.append(doc)

                    logger.info("keyword_search_complete", keyword=keyword, results=len(documents))

            except Exception as e:
                logger.error("keyword_search_error", keyword=keyword, error=str(e))

        return documents

    async def get_public_inspection_documents(self) -> list[FederalDocument]:
        """Get documents on public inspection (pre-publication)"""
        documents = []

        async with httpx.AsyncClient() as client:
            try:
                await asyncio.sleep(self.config["rate_limit"])

                response = await client.get(
                    f"{self.base_url}/public-inspection-documents/current",
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("results", []):
                        doc = self._parse_document(item)
                        if doc:
                            doc.relevance_score = self._calculate_relevance(doc)
                            doc.pnkln_vertical = self._classify_vertical(doc)
                            documents.append(doc)

                    logger.info("public_inspection_fetch_complete", documents=len(documents))

            except Exception as e:
                logger.error("public_inspection_error", error=str(e))

        return documents

    def format_document_markdown(self, doc: FederalDocument) -> str:
        """Format document as markdown"""
        parts = [
            f"# {doc.title}",
            "",
            f"**Document Number:** {doc.document_number}",
            f"**Type:** {doc.document_type}",
            f"**Publication Date:** {doc.publication_date.strftime('%Y-%m-%d')}",
            f"**Agency:** {', '.join(doc.agency_names)}",
            f"**PNKLN Vertical:** {doc.pnkln_vertical}",
            f"**Relevance Score:** {doc.relevance_score:.2f}",
            f"**Significant:** {'Yes' if doc.significant else 'No'}",
            "",
            f"**HTML URL:** {doc.html_url}",
        ]

        if doc.pdf_url:
            parts.append(f"**PDF URL:** {doc.pdf_url}")

        if doc.effective_date:
            parts.append(f"**Effective Date:** {doc.effective_date.strftime('%Y-%m-%d')}")

        if doc.comment_deadline:
            parts.append(f"**Comment Deadline:** {doc.comment_deadline.strftime('%Y-%m-%d')}")

        if doc.docket_ids:
            parts.append(f"**Docket IDs:** {', '.join(doc.docket_ids)}")

        if doc.cfr_references:
            parts.append(f"**CFR References:** {', '.join(doc.cfr_references)}")

        parts.extend(
            [
                "",
                "## Abstract",
                "",
                doc.abstract,
                "",
                "---",
            ],
        )

        return "\n".join(parts)

    def save_documents(self, documents: list[FederalDocument]) -> list[str]:
        """Save documents to storage"""
        saved_files = []

        for doc in documents:
            # Create safe filename
            safe_title = "".join(
                c if c.isalnum() or c in "._- " else "_" for c in doc.title[:40]
            ).strip()
            filename = (
                f"{doc.publication_date.strftime('%Y%m%d')}_{doc.document_number}_{safe_title}.md"
            )
            filepath = self.storage_path / filename

            try:
                markdown = self.format_document_markdown(doc)
                filepath.write_text(markdown, encoding="utf-8")
                saved_files.append(str(filepath))

                logger.debug(
                    "document_saved",
                    document_number=doc.document_number,
                    file=str(filepath),
                )
            except Exception as e:
                logger.error(
                    "document_save_error",
                    document_number=doc.document_number,
                    error=str(e),
                )

        logger.info("documents_saved", count=len(saved_files))

        return saved_files

    def generate_regulatory_summary(self, documents: list[FederalDocument]) -> str:
        """Generate summary report of regulatory intel"""
        summary_parts = [
            "# Federal Register Regulatory Intel Summary",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Documents:** {len(documents)}",
            "",
        ]

        # Count by type
        by_type: dict[str, int] = {}
        for doc in documents:
            by_type[doc.document_type] = by_type.get(doc.document_type, 0) + 1

        summary_parts.append("## Document Types")
        for doc_type, count in sorted(by_type.items()):
            summary_parts.append(f"- {doc_type}: {count}")
        summary_parts.append("")

        # Group by vertical
        by_vertical: dict[str, list[FederalDocument]] = {}
        for doc in documents:
            vertical = doc.pnkln_vertical or "other"
            if vertical not in by_vertical:
                by_vertical[vertical] = []
            by_vertical[vertical].append(doc)

        for vertical, vert_docs in sorted(by_vertical.items()):
            summary_parts.append(
                f"## {vertical.replace('_', ' ').title()} ({len(vert_docs)} documents)",
            )
            summary_parts.append("")

            # Top 5 by relevance
            top_docs = sorted(vert_docs, key=lambda x: x.relevance_score, reverse=True)[:5]
            for doc in top_docs:
                summary_parts.append(
                    f"- **[{doc.document_type}]** {doc.title[:60]}... "
                    f"({doc.publication_date.strftime('%Y-%m-%d')}) "
                    f"[{doc.relevance_score:.0%}]",
                )

            if len(vert_docs) > 5:
                summary_parts.append(f"- ... and {len(vert_docs) - 5} more")
            summary_parts.append("")

        # Highlight significant documents
        significant = [d for d in documents if d.significant]
        if significant:
            summary_parts.append("## Significant Documents (Requires Review)")
            summary_parts.append("")
            for doc in significant[:10]:
                summary_parts.append(
                    f"- **{doc.title[:60]}...** - {', '.join(doc.agency_names[:2])}",
                )
            summary_parts.append("")

        # Upcoming deadlines
        deadlines = [
            d for d in documents if d.comment_deadline and d.comment_deadline > datetime.now()
        ]
        deadlines.sort(key=lambda x: x.comment_deadline)
        if deadlines:
            summary_parts.append("## Upcoming Comment Deadlines")
            summary_parts.append("")
            for doc in deadlines[:10]:
                summary_parts.append(
                    f"- **{doc.comment_deadline.strftime('%Y-%m-%d')}**: {doc.title[:50]}...",
                )
            summary_parts.append("")

        return "\n".join(summary_parts)


# Convenience functions
async def crawl_federal_register(days_back: int = 30) -> list[str]:
    """Crawl Federal Register for PNKLN-relevant regulatory intel

    Usage:
        files = await crawl_federal_register(days_back=30)
    """
    crawler = FederalRegisterCrawler()
    documents = await crawler.fetch_documents(days_back=days_back)
    return crawler.save_documents(documents)


async def search_federal_register(keyword: str, days_back: int = 30) -> list[str]:
    """Search Federal Register by keyword

    Usage:
        files = await search_federal_register("artificial intelligence", days_back=30)
    """
    crawler = FederalRegisterCrawler()
    documents = await crawler.search_by_keyword(keyword, days_back)
    return crawler.save_documents(documents)


async def get_upcoming_regulations() -> list[str]:
    """Get pre-publication regulatory documents

    Usage:
        files = await get_upcoming_regulations()
    """
    crawler = FederalRegisterCrawler()
    documents = await crawler.get_public_inspection_documents()
    return crawler.save_documents(documents)
