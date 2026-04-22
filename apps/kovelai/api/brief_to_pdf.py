"""
Brief-to-PDF Conversion Service.

Converts Attorney Brief markdown to court-quality PDF using WeasyPrint.
PDF includes privilege watermarks, Kovel attestation footer, and
professional legal document formatting.

Dependencies:
    pip install weasyprint markdown

@see brief_builder.py — Brief generation
@see WAR_ROOM_ARCHITECTURE.md — Stage 6 output
"""

from __future__ import annotations

import io
import logging
from datetime import datetime, timezone, UTC

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# PDF Stylesheet
# ═══════════════════════════════════════════════════════════

LEGAL_PDF_STYLESHEET = """
@page {
    size: letter;
    margin: 1in 1.25in 1.5in 1.25in;
    @top-center {
        content: "PRIVILEGED AND CONFIDENTIAL — ATTORNEY WORK-PRODUCT";
        font-family: 'Times New Roman', Times, serif;
        font-size: 8pt;
        color: #cc0000;
        font-weight: bold;
    }
    @bottom-left {
        content: "KovelAI War Room — Session: " attr(data-session-id);
        font-family: 'Times New Roman', Times, serif;
        font-size: 7pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Times New Roman', Times, serif;
        font-size: 8pt;
    }
    @bottom-right {
        content: "Generated: " attr(data-timestamp);
        font-family: 'Times New Roman', Times, serif;
        font-size: 7pt;
        color: #666;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #1a1a1a;
}

h1 {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0;
    margin-bottom: 24pt;
    border-bottom: 2pt solid #1a1a1a;
    padding-bottom: 12pt;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 24pt;
    margin-bottom: 12pt;
    color: #1a1a1a;
    border-bottom: 0.5pt solid #999;
    padding-bottom: 4pt;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 8pt;
}

p {
    text-align: justify;
    margin-bottom: 8pt;
    orphans: 3;
    widows: 3;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background-color: #f2f2f2;
    border: 0.5pt solid #999;
    padding: 6pt 8pt;
    text-align: left;
    font-weight: bold;
}

td {
    border: 0.5pt solid #999;
    padding: 4pt 8pt;
    vertical-align: top;
}

code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    background-color: #f5f5f5;
    padding: 1pt 3pt;
}

blockquote {
    border-left: 3pt solid #cc0000;
    margin-left: 0;
    padding-left: 12pt;
    font-style: italic;
    color: #333;
}

.privilege-watermark {
    position: fixed;
    top: 45%;
    left: 10%;
    transform: rotate(-45deg);
    font-size: 60pt;
    color: rgba(200, 0, 0, 0.06);
    font-weight: bold;
    z-index: -1;
    white-space: nowrap;
}

.kovel-attestation {
    border: 2pt solid #cc0000;
    padding: 12pt;
    margin-top: 24pt;
    background-color: #fff5f5;
    page-break-inside: avoid;
}

.kovel-attestation pre {
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    white-space: pre-wrap;
    margin: 0;
}

hr {
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 18pt 0;
}
"""


# ═══════════════════════════════════════════════════════════
# Markdown-to-HTML Conversion
# ═══════════════════════════════════════════════════════════


def _markdown_to_html(markdown_content: str, session_id: str) -> str:
    """Convert markdown brief to styled HTML for PDF rendering."""
    try:
        import markdown
    except ImportError:
        logger.warning("markdown package not installed, using raw text")
        html_body = f"<pre>{markdown_content}</pre>"
    else:
        html_body = markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code", "nl2br"],
        )

    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en" data-session-id="{session_id}" data-timestamp="{now}">
<head>
    <meta charset="utf-8">
    <title>Attorney Work-Product Brief — {session_id}</title>
    <style>{LEGAL_PDF_STYLESHEET}</style>
</head>
<body>
    <div class="privilege-watermark">PRIVILEGED</div>
    {html_body}
</body>
</html>"""


# ═══════════════════════════════════════════════════════════
# PDF Generation
# ═══════════════════════════════════════════════════════════


def brief_markdown_to_pdf(
    markdown_content: str,
    session_id: str,
) -> bytes:
    """
    Convert a markdown attorney brief to PDF.

    Args:
        markdown_content: Full markdown text of the brief
        session_id: Session ID for header/footer

    Returns:
        PDF file content as bytes

    Raises:
        ImportError: If weasyprint is not installed
    """
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise ImportError(
            "weasyprint is required for PDF generation. "
            "Install with: pip install weasyprint"
        ) from exc

    html_content = _markdown_to_html(markdown_content, session_id)

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    logger.info(
        "Generated PDF for session %s: %d bytes",
        session_id,
        len(pdf_bytes),
    )
    return pdf_bytes


def brief_markdown_to_pdf_file(
    markdown_content: str,
    session_id: str,
    output_path: str,
) -> str:
    """
    Convert markdown brief to PDF and save to disk.

    Args:
        markdown_content: Full markdown text of the brief
        session_id: Session ID for header/footer
        output_path: File path to write the PDF

    Returns:
        The output file path
    """
    pdf_bytes = brief_markdown_to_pdf(markdown_content, session_id)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    logger.info("Saved PDF to %s", output_path)
    return output_path
