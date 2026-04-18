#!/usr/bin/env python3
"""Evidence-Grade Ingestion Pipeline.

Architecture:
1. Ingest: Fetch raw metadata (HN, RSS).
2. Filter: Local LLM (Ollama/Llama 3) strict classification.
3. Capture: Headless Browser (Playwright) forensic PDF with timestamp.
4. Verify: SHA-256 Hashing of evidence.
5. Index: Vector DB (ChromaDB) for semantic search.
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

import aiohttp

# Third-party imports
try:
    import ssl

    import certifi
    import chromadb
    from playwright.async_api import async_playwright
    from pypdf import PdfReader
except ImportError as e:
    raise ImportError(
        f"Missing dependency: {e}. Run: pip install chromadb pypdf playwright aiohttp",
    )

# --- CONFIGURATION ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
ARTIFACTS_DIR = Path("data/legal_evidence")
DB_PATH = Path("data/legal_knowledge_graph")

# Ensure directories exist
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- INITIALIZE VECTOR DATABASE ---
# PersistentClient saves data to disk so it survives restarts.
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))
collection = chroma_client.get_or_create_collection(name="legal_briefs")


class IngestionItem:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.analysis = {}
        self.evidence_path = None
        self.file_hash = None
        self.id = str(uuid.uuid4())


# --- MODULE 1: AI CLASSIFICATION (Ollama) ---
async def consult_ollama(session, text):
    """Asks local Llama 3 if the content is relevant."""
    system_prompt = """
    You are a Legal Tech & Emerging Tech Research Assistant.
    Analyze the input. Return JSON only:
    { "relevant": boolean, "category": "Legal Tech" | "Emerging Tech" | "Irrelevant", "reason": "short text" }
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nINPUT: {text}",
        "format": "json",
        "stream": False,
    }
    try:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return json.loads(data["response"])
    except Exception as e:
        logging.warning(f"Ollama classification failed: {e}")
    return {"relevant": False}


# --- MODULE 2: FORENSIC CAPTURE (Playwright) ---
async def capture_evidence(browser, item):
    """Renders page, injects timestamp, saves PDF, and hashes it."""
    safe_title = "".join([c for c in item.title if c.isalnum() or c in (" ", "-", "_")]).strip()[
        :50
    ]
    filename = f"{datetime.now().strftime('%Y%m%d')}_{safe_title}.pdf"
    filepath = ARTIFACTS_DIR / filename

    page = await browser.new_page()
    try:
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 LegalTechBot/1.0"})
        # 30s timeout, wait for network to settle
        await page.goto(item.url, wait_until="networkidle", timeout=30000)

        # Inject Visual Watermark
        timestamp = datetime.now().isoformat()
        footer_script = f"""
        const div = document.createElement('div');
        div.style.cssText = 'position:fixed;bottom:0;right:0;background:white;border:1px solid black;padding:5px;z-index:9999;font-size:10px;color:black;';
        div.innerText = 'EVIDENCE CAPTURE: {timestamp}';
        document.body.appendChild(div);
        """
        await page.evaluate(footer_script)
        await page.pdf(path=str(filepath), format="A4")

        # Integrity Hash
        with open(filepath, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        return filepath, file_hash
    except Exception as e:
        logging.exception(f"Capture failed for {item.url}: {e}")
        return None, None
    finally:
        await page.close()


# --- MODULE 3: INDEXING (Vector Store) ---
def index_document(item):
    """Extracts text from the PDF and stores it in ChromaDB with metadata."""
    try:
        if not item.evidence_path:
            return False

        # 1. Extract Text from PDF
        reader = PdfReader(str(item.evidence_path))
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"

        # 2. Chunking (Simple sliding window or per-page)
        # Limit context window for embedding model
        if len(text_content) > 8000:
            text_content = text_content[:8000]

        # 3. Insert into Vector DB
        collection.add(
            documents=[text_content],
            metadatas=[
                {
                    "title": item.title,
                    "url": item.url,
                    "category": item.analysis.get("category", "Unknown"),
                    "evidence_file": str(item.evidence_path),
                    "evidence_hash": item.file_hash,
                    "capture_date": datetime.now().isoformat(),
                },
            ],
            ids=[item.id],
        )
        logging.info(f"🧠 Indexed: {item.title}")
        return True
    except Exception as e:
        logging.exception(f"Indexing failed for {item.title}: {e}")
        return False


# --- ORCHESTRATOR ---
async def process_item(session, browser, item):
    # Phase 1: Filter
    ai_result = await consult_ollama(session, item.title)
    item.analysis = ai_result

    if not ai_result.get("relevant"):
        return None

    # Phase 2: Capture
    logging.info(f"📸 Capturing: {item.title}")
    path, file_hash = await capture_evidence(browser, item)

    if path:
        item.evidence_path = path
        item.file_hash = file_hash

        # Phase 3: Index (Run in executor to avoid blocking async loop)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, index_document, item)

        return item
    return None


async def run_pipeline():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with async_playwright() as p:
            # Launch Browser (Headless)
            browser = await p.chromium.launch(headless=True)

            # Fetch Source
            print("🔌 Connecting to Hacker News...")
            try:
                async with session.get(
                    "https://hacker-news.firebaseio.com/v0/topstories.json",
                ) as resp:
                    ids = (await resp.json())[:10]  # Process top 10 for demo

                tasks = [
                    session.get(f"https://hacker-news.firebaseio.com/v0/item/{i}.json") for i in ids
                ]
                items = []
                for r in await asyncio.gather(*tasks):
                    d = await r.json()
                    if d and "url" in d:
                        items.append(IngestionItem(d["title"], d["url"]))
            except Exception as e:
                logging.exception(f"Failed to fetch from HN: {e}")
                items = []

            print(f"📥 Processing {len(items)} items...")

            # Concurrency Control
            semaphore = asyncio.Semaphore(2)  # Low concurrency to save resources

            async def protected_process(item):
                async with semaphore:
                    return await process_item(session, browser, item)

            tasks = [protected_process(item) for item in items]
            results = await asyncio.gather(*tasks)

            print("\n=== 🏁 PIPELINE COMPLETE ===")
            print(f"Items Indexed: {len([r for r in results if r])}")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
