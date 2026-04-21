import logging
import os
import textwrap

import ebooklib

try:
    import langextract as lx
except ImportError:
    lx = None
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ebooklib import epub
from pypdf import PdfReader

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, ".beads", "knowledge_base")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "extraction_results.jsonl")

# 🚀 The Critical Distinctions
PROJECT_ID = "shadowtag-omega-v4"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
MODEL_ID = "gemini-3.1-flash-lite-preview"

# Target Directories
BASE_DRIVE = os.path.join(PROJECT_ROOT, "data/drive_ingest/docs")
DOCTRINE_DIR = os.path.join(PROJECT_ROOT, "libs/external/elements-of-python-style")
SOURCE_DIRS = [BASE_DRIVE, DOCTRINE_DIR]

STATE_FILE = os.path.join(OUTPUT_DIR, "processed_registry.txt")

# Extraction Prompt
PROMPT = textwrap.dedent("""\
    Extract key topics, entities, definitions, and relationships found in the text.
    Focus on extracting high-value technical concepts, architectural patterns, and strategic insights.
    Maintain the exact terminology used in the source text.
    """)

# Minimal Example (Required by LangExtract)
try:
    EXAMPLES = [
        lx.data.ExampleData(
            text="The Omega Protocol requires a 3-node consensus mechanism using Raft consensus.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="protocol",
                    extraction_text="Omega Protocol",
                    attributes={"requirement": "3-node consensus mechanism", "algorithm": "Raft"},
                ),
                lx.data.Extraction(
                    extraction_class="mechanism",
                    extraction_text="Raft consensus",
                    attributes={"context": "Omega Protocol"},
                ),
            ],
        ),
    ]
except NameError:
    EXAMPLES = []


def extract_text_from_pdf(filepath: str) -> str:
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(filepath)
        text = ""
        # Limit to 50 pages to prevent massive PDFs from taking forever
        for i, page in enumerate(reader.pages):
            if i > 50:
                break
            extracted = page.extract_text()
            if extracted:
                text += str(extracted) + "\n"
        return text
    except Exception as e:
        logger.exception(f"Failed to read PDF {filepath}: {e}")
        return ""


def extract_text_from_file(filepath: str) -> str:
    """Reads text from a generic text file."""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        logger.exception(f"Failed to read file {filepath}: {e}")
        return ""


def extract_text_from_epub(filepath: str) -> str:
    """Extracts text from an EPUB file."""
    try:
        book = epub.read_epub(filepath)
        text = ""
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_body_content(), "html.parser")
                text += soup.get_text() + "\n"
        return text
    except Exception as e:
        logger.exception(f"Failed to read EPUB {filepath}: {e}")
        return ""


def load_processed_state() -> set:
    """Loads the set of already processed filepaths."""
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_to_processed_state(filepath: str) -> None:
    """Appends a new file to the processed registry."""
    with open(STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{filepath}\n")


def process_file(filepath: str) -> bool:
    """Process a single file and append results to JSONL. Returns True if successful."""
    if lx is None:
        logger.error("langextract is not installed. Aborting ingestion for %s", filepath)
        return False

    logger.info(f"Processing: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    content = ""

    if ext == ".pdf":
        content = extract_text_from_pdf(filepath)
    elif ext in [".txt", ".md", ".json", ".yaml", ".yml"]:
        content = extract_text_from_file(filepath)
    elif ext == ".epub":
        content = extract_text_from_epub(filepath)
    else:
        logger.debug(f"Skipping unsupported file type: {filepath}")
        return False

    # Enforce minimum content bound to save LLM tokens (e.g. at least 50 chars)
    if not content or len(content.strip()) < 50:
        logger.warning(f"Empty or negligible content for {filepath}")
        return False

    try:
        safe_content = content[:300000]
        result = lx.extract(
            text_or_documents=safe_content,
            prompt_description=PROMPT,
            examples=EXAMPLES,
            model_id=MODEL_ID,
        )

        # FIX: Check if any extractions were actually returned
        if not result.extractions:
            logger.warning(f"No extractions found for {filepath}. Skipping save and registry update.")
            return False

        # Add metadata & save temp
        lx.io.save_annotated_documents([result], output_name="temp_output.jsonl", output_dir=OUTPUT_DIR)

        # Append temp content to main file to handle streaming/crashes
        temp_path = os.path.join(OUTPUT_DIR, "temp_output.jsonl")
        if os.path.exists(temp_path):
            with (
                open(temp_path, encoding="utf-8") as f_in,
                open(OUTPUT_FILE, "a", encoding="utf-8") as f_out,
            ):
                f_out.write(f_in.read())
            os.remove(temp_path)

        return True
    except Exception as e:
        logger.exception(f"LangExtract failed for {filepath}: {e}")
        return False


def main() -> None:
    if lx is None:
        logger.error("langextract is missing. Install it before running this ingestion pipeline.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    processed_files = load_processed_state()
    total_files_discovered = 0
    total_files_processed = 0

    for root_dir in SOURCE_DIRS:
        if not os.path.exists(root_dir):
            logger.warning(f"Directory not found: {root_dir}")
            continue

        for root, _dirs, files in os.walk(root_dir):
            for file in files:
                filepath = os.path.join(root, file)
                total_files_discovered += 1

                # Check extension first to optimize out image/video loops
                ext = os.path.splitext(filepath)[1].lower()
                if ext not in [".pdf", ".txt", ".md", ".json", ".yaml", ".yml", ".epub"]:
                    continue

                if filepath in processed_files:
                    continue

                logger.info(f"Discovered uningested target: {filepath}")
                success = process_file(filepath)
                if success:
                    processed_files.add(filepath)
                    append_to_processed_state(filepath)
                    total_files_processed += 1

    logger.info(f"Ingestion scan complete. Discovered {total_files_discovered}. Successfully processed {total_files_processed} new files.")


if __name__ == "__main__":
    main()
