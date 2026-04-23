import glob
import logging
import os
import sys
import textwrap

# Add project root to sys.path to allow 'shared' to be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import langextract as lx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from rag_engine.memory_service import SequentialMemoryService  # noqa: E402
from shared.config import settings  # noqa: E402

load_dotenv(override=True)


# We need a dummy embed function since we haven't wired up Gemini embeddings yet
def dummy_embed(text: str) -> list[float]:
    return [0.0] * 1536


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iCloud_Extractor")


def ingest_icloud_notes(notes_dir: str) -> None:
    logger.info(f"Targeting iCloud Notes Vault: {notes_dir}")

    # Locate all note files (txt and md)
    search_path = os.path.join(notes_dir, "**", "*.txt")
    txt_files = glob.glob(search_path, recursive=True)

    search_path_md = os.path.join(notes_dir, "**", "*.md")
    md_files = glob.glob(search_path_md, recursive=True)

    all_files = txt_files + md_files
    logger.info(f"Detected {len(all_files)} raw note objects.")

    if not all_files:
        logger.warning(f"No text or markdown files found in {notes_dir}.")
        return

    # Define the Extraction Schema for a "Brain" dump
    prompt = textwrap.dedent("""\
        Extract core business concepts, projects, technologies, and actionable intelligence
        from these personal notes. Provide meaningful attributes for each entity to add context.
        Do not hallucinate. If the note is just a grocery list, extract nothing.
    """)

    # High-quality few-shot examples telling LangExtract how to parse the unformatted brain dumps
    examples = [
        lx.data.ExampleData(
            text="Need to migrate the ShadowTag-v2-fastapi-services to Cloud Run and finalize the Stripe webhooks by Friday.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="project",
                    extraction_text="ShadowTag-v2-fastapi-services",
                    attributes={"status": "needs migration", "target": "Cloud Run"},
                ),
                lx.data.Extraction(
                    extraction_class="action_item",
                    extraction_text="finalize the Stripe webhooks",
                    attributes={"deadline": "Friday"},
                ),
            ],
        ),
    ]

    # Initialize Memory Service
    memory_svc = SequentialMemoryService(embed_fn=dummy_embed)
    timeline_id = "icloud_notes_ingest_march_2026"

    # Process files
    for filepath in all_files[:50]:  # Capped at 50 for initial testing
        logger.info(f"Extracting: {os.path.basename(filepath)}")
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not content.strip():
            continue

        # Execute LangExtract against Gemini 2.5 Flash
        # Note: Requires export LANGEXTRACT_API_KEY="your-gemini-api-key"
        try:
            api_key_val = os.environ.get("GEMINI_API_KEY") or os.environ.get("LANGEXTRACT_API_KEY")
            if not api_key_val:
                api_key_val = getattr(settings, "gemini_api_key", "")

            result = lx.extract(
                text_or_documents=content,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-3.1-flash-lite-preview",
                api_key=api_key_val,
            )

            # Format outputs for our RAG chronological timeline
            structured_events = []
            if result.extractions:
                for ext in result.extractions:
                    structured_events.append(
                        {
                            "text": f"[{ext.extraction_class.upper()}] {ext.extraction_text} | Context: {ext.attributes}",
                            "timestamp": "retroactive",
                            "node_type": "icloud_note_extraction",
                        },
                    )

                # Push mathematically tagged structures into the active Sovereign Vector Engine
                memory_svc.persist_traversal(timeline_id, structured_events)
                logger.info(f" -> Upserted {len(structured_events)} structured entities.")

        except Exception as e:
            logger.exception(f"Failed extracting {filepath}: {e!s}")

    logger.info("iCloud Extraction Sequence Complete.")


if __name__ == "__main__":
    NOTES_PATH = "/Users/pikeymickey/Downloads/iCloud Notes"
    ingest_icloud_notes(NOTES_PATH)
