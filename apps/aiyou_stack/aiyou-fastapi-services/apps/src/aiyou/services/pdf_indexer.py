#!/usr/bin/env python3
"""
PDF Indexer for Scholarly Papers
Indexes PDFs for Flying n-autoresearch/Kosmos/BioAgents research corpus.
Apertus-style scholarly document ingestion.
"""

from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from src.shadowtag_v4.services.corpus_indexer import CorpusIndexer
from src.shadowtag_v4.services.safety_scanner import SafetyScanner


@dataclass
class PDFMetadata:
    """Extracted PDF metadata."""

    title: str
    authors: list[str]
    abstract: str
    pages: int
    tokens: int
    arxiv_id: str | None
    doi: str | None


class PDFIndexer:
    """
    Scholarly PDF indexer for Flying n-autoresearch/Kosmos/BioAgents corpus.

    Extracts text, metadata, and indexes for searchable research.
    """

    def __init__(self, es_host: str = None):
        self.corpus = CorpusIndexer(es_host)
        self.scanner = SafetyScanner()

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        if not fitz:
            raise ImportError("PyMuPDF (fitz) not installed: pip install pymupdf")

        doc = fitz.open(pdf_path)
        text_parts = []

        for page in doc:
            text_parts.append(page.get_text())

        doc.close()
        return "\n\n".join(text_parts)

    def extract_metadata(self, pdf_path: str, text: str) -> PDFMetadata:
        """Extract metadata from PDF and text."""
        if not fitz:
            return PDFMetadata(
                title=Path(pdf_path).stem,
                authors=[],
                abstract="",
                pages=0,
                tokens=len(text) // 4,
                arxiv_id=None,
                doi=None,
            )

        doc = fitz.open(pdf_path)
        meta = doc.metadata

        # Extract title
        title = meta.get("title", "") or Path(pdf_path).stem

        # Extract authors
        authors = []
        if meta.get("author"):
            authors = [a.strip() for a in meta["author"].split(",")]

        # Extract abstract (first ~500 chars after "Abstract")
        abstract = ""
        abstract_match = text.lower().find("abstract")
        if abstract_match != -1:
            abstract_end = text.find("\n\n", abstract_match + 8)
            if abstract_end == -1:
                abstract_end = abstract_match + 1000
            abstract = text[abstract_match:abstract_end].strip()[:1000]

        # Look for arXiv ID
        arxiv_id = None
        import re

        arxiv_match = re.search(r"arXiv:(\d{4}\.\d{4,5})", text)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)

        # Look for DOI
        doi = None
        doi_match = re.search(r"10\.\d{4,}/[^\s]+", text)
        if doi_match:
            doi = doi_match.group(0)

        doc.close()

        return PDFMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            pages=len(doc) if doc else 0,
            tokens=len(text) // 4,
            arxiv_id=arxiv_id,
            doi=doi,
        )

    def index_pdf(self, pdf_path: str, category: str = "paper") -> str:
        """
        Index a single PDF.

        Args:
            pdf_path: Path to PDF file
            category: paper, thesis, report, etc.

        Returns:
            Document ID
        """
        # Extract text
        text = self.extract_text(pdf_path)

        # Safety scan
        scan = self.scanner.scan_content(text, pdf_path)
        if not scan.safe:
            print(f"///▞ WARNING: Safety flags on {pdf_path}: {scan.flags}")

        # Extract metadata
        meta = self.extract_metadata(pdf_path, text)

        # Index to corpus
        doc_id = self.corpus.index_document(
            content=text,
            source_path=pdf_path,
            title=meta.title,
            doc_type=category,
            language="en",  # Assume English for papers
            metadata={
                "authors": meta.authors,
                "abstract": meta.abstract,
                "pages": meta.pages,
                "arxiv_id": meta.arxiv_id,
                "doi": meta.doi,
                "safety_flags": scan.flags,
            },
        )

        print(f"///▞ Indexed PDF: {meta.title[:50]} ({meta.tokens} tokens)")
        return doc_id

    def index_directory(self, dir_path: str, recursive: bool = True) -> list[str]:
        """
        Index all PDFs in directory.

        Args:
            dir_path: Directory to scan
            recursive: Search subdirectories

        Returns:
            List of document IDs
        """
        indexed = []
        path = Path(dir_path)

        pattern = "**/*.pdf" if recursive else "*.pdf"

        for pdf_file in path.glob(pattern):
            try:
                doc_id = self.index_pdf(str(pdf_file))
                indexed.append(doc_id)
            except Exception as e:
                print(f"///▞ ERROR indexing {pdf_file}: {e}")

        return indexed

    def index_arxiv_list(self, arxiv_ids: list[str], download_dir: str = "/tmp/arxiv") -> list[str]:
        """
        Download and index papers from arXiv.

        Args:
            arxiv_ids: List of arXiv IDs (e.g., ["2301.00001", "2301.00002"])
            download_dir: Directory to save PDFs

        Returns:
            List of document IDs
        """
        import urllib.request

        Path(download_dir).mkdir(parents=True, exist_ok=True)
        indexed = []

        for arxiv_id in arxiv_ids:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            pdf_path = f"{download_dir}/{arxiv_id.replace('/', '_')}.pdf"

            try:
                print(f"///▞ Downloading arXiv:{arxiv_id}")
                urllib.request.urlretrieve(pdf_url, pdf_path)

                doc_id = self.index_pdf(pdf_path, category="arxiv")
                indexed.append(doc_id)

            except Exception as e:
                print(f"///▞ ERROR with arXiv:{arxiv_id}: {e}")

        return indexed

    def search_papers(self, query: str, limit: int = 10) -> list[dict]:
        """Search indexed papers."""
        return self.corpus.search(query=query, doc_type="paper", limit=limit)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="PDF Indexer")
    subparsers = parser.add_subparsers(dest="command")

    # Index single PDF
    pdf_parser = subparsers.add_parser("pdf", help="Index a PDF")
    pdf_parser.add_argument("file", help="PDF file to index")

    # Index directory
    dir_parser = subparsers.add_parser("dir", help="Index directory of PDFs")
    dir_parser.add_argument("path", help="Directory path")
    dir_parser.add_argument("--no-recursive", action="store_true")

    # Index from arXiv
    arxiv_parser = subparsers.add_parser("arxiv", help="Index from arXiv IDs")
    arxiv_parser.add_argument("ids", nargs="+", help="arXiv IDs")
    arxiv_parser.add_argument("--download-dir", default="/tmp/arxiv")

    # Search
    search_parser = subparsers.add_parser("search", help="Search papers")
    search_parser.add_argument("query", help="Search query")

    args = parser.parse_args()
    indexer = PDFIndexer()

    if args.command == "pdf":
        indexer.index_pdf(args.file)

    elif args.command == "dir":
        indexed = indexer.index_directory(args.path, not args.no_recursive)
        print(f"\nIndexed {len(indexed)} PDFs")

    elif args.command == "arxiv":
        indexed = indexer.index_arxiv_list(args.ids, args.download_dir)
        print(f"\nIndexed {len(indexed)} papers from arXiv")

    elif args.command == "search":
        results = indexer.search_papers(args.query)
        for r in results:
            print(f"{r['score']:.2f} {r['title'][:50]}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
