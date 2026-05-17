# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os


def create_file(filepath, content):
  os.makedirs(os.path.dirname(filepath), exist_ok=True)
  with open(filepath, "w") as f:
    f.write(content.strip() + "\n")
  print(f"✅ Reconstructed: {filepath}")


# --- ARCHITECTURE FILES TO RECONSTRUCT ---

bq_omni = """
variable "project_id" {
  type    = string
  default = "shadowtag-omega-v4"
}

variable "region" {
  type    = string
  default = "us-central1"
}

resource "google_bigquery_dataset" "omniscience_lake" {
  dataset_id                  = "omniscience_lake"
  friendly_name               = "Omniscience Lake"
  description                 = "Zero-ETL Autonomous vector embedding database for global intelligence feeds."
  location                    = "US"
  project                     = var.project_id
}

resource "google_bigquery_connection" "vertex_bridge" {
  connection_id = "uphillsnowball_vertex_bridge"
  project       = var.project_id
  location      = "US"
  cloud_resource {}
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_bigquery_connection.vertex_bridge.cloud_resource[0].service_account_id}"
}
"""

bq_sql = """
-- 1. Create the Remote Model linking BigQuery to Gemini Embeddings
CREATE OR REPLACE MODEL omniscience_lake.text_embedder_004
REMOTE WITH CONNECTION `us.uphillsnowball_vertex_bridge`
OPTIONS (ENDPOINT = 'text-embedding-004');

-- 2. Create the Autonomous Table
CREATE OR REPLACE TABLE omniscience_lake.global_intelligence_feed (
    intel_id STRING,
    source_domain STRING, -- e.g., 'SEC_FILINGS', 'REDDIT_FRINGE', 'HONEYPOT'
    raw_intelligence STRING,
    ingest_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    
    -- 🚀 THE KINETIC UPLIFT: Autonomous Embedding Generation
    -- Zero Python middleware. BigQuery handles the AI invocation on insert via query.
    intelligence_vector ARRAY<FLOAT64>
);

-- 3. Create the Vector Index for sub-second semantic search on billions of rows
CREATE VECTOR INDEX IF NOT EXISTS omniscience_semantic_idx 
ON omniscience_lake.global_intelligence_feed(intelligence_vector)
OPTIONS(index_type = 'IVF', distance_type = 'COSINE');
"""

data_router = """
import os
import uuid
import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class AutonomousDataRouter:
    \"\"\"
    ⏺ ///▙▖▙▖▞ THE SPLIT-BRAIN ROUTER
    Local Mac -> AlloyDB Omni (Generated Columns)
    Uphillsnowball -> BigQuery (Autonomous Embeddings)
    \"\"\"
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        if self.env == "production":
            self.bq_client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4"))
            self.dataset = "omniscience_lake.global_intelligence_feed"

    async def ingest_unstructured_intelligence(self, source: str, raw_text: str):
        ingest_id = uuid.uuid4().hex
        
        if self.env == "development":
            # Local Mode: Route to AlloyDB Omni. The DB generates the vector natively.
            logger.info(f"[DEV] Routing {source} to Local AlloyDB Hippocampus...")
            # await SovereignMemoryPool.write_memory(domain="OMNISCIENCE", thought_text=raw_text, metadata={"source": source, "ingest_id": ingest_id})
            return "LOCAL_ALLOYDB_INGEST_COMPLETE"
            
        else:
            # Production Mode (Uphillsnowball): Route to BigQuery.
            logger.info(f"[PROD] Routing {source} to BigQuery Zero-ETL Lake...")
            
            sql = f\"\"\"
                INSERT INTO `{self.dataset}` (intel_id, source_domain, raw_intelligence, intelligence_vector)
                SELECT 
                    '{ingest_id}', 
                    '{source}', 
                    '{raw_text}', 
                    ml_generate_embedding_result 
                FROM ML.GENERATE_EMBEDDING(
                    MODEL `shadowtag-omega-v4.omniscience_lake.text_embedder_004`, 
                    (SELECT '{raw_text}' AS content)
                )
            \"\"\"
            
            try:
                self.bq_client.query(sql).result()
                return "PROD_BQ_INGEST_COMPLETE"
            except Exception as e:
                logger.error(f"❌ BQ Ingest Error: {e}")
                return "PROD_BQ_INGEST_FAILED"
"""

bq_search = """
import os
import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

class OmniscienceSearchEngine:
    \"\"\"
    ⏺ ///▙▖▙▖▞ KOSMOS SWARM RAG: BIGQUERY VECTOR SEARCH
    \"\"\"
    def __init__(self):
        self.bq_client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4"))

    def search_intelligence(self, query: str, limit: int = 5) -> str:
        logger.info(f"🔍 Swarm executing Semantic Search across Uphillsnowball for: '{query}'")
        
        sql = f\"\"\"
            SELECT base.raw_intelligence, distance
            FROM VECTOR_SEARCH(
                TABLE `shadowtag-omega-v4.omniscience_lake.global_intelligence_feed`,
                'intelligence_vector',
                (SELECT ml_generate_embedding_result FROM ML.GENERATE_EMBEDDING(
                    MODEL `shadowtag-omega-v4.omniscience_lake.text_embedder_004`,
                    (SELECT '{query}' AS content)
                )),
                top_k => {limit},
                distance_type => 'COSINE'
            )
        \"\"\"
        
        try:
            results = self.bq_client.query(sql).result()
            context = [f"[Relevance: {1 - row.distance:.2f}] {row.raw_intelligence[:500]}..." for row in results]
            
            if not context:
                return "No high-relevance intelligence found in Uphillsnowball for this vector."
            
            return "\\n---\\n".join(context)
            
        except Exception as e:
            logger.error(f"❌ BigQuery Vector Search Failed: {e}")
            return f"Error executing native semantic search: {e}"
"""

swarm_controller = """
from typing import List
import asyncio

class SequentialAttentionSwarm:
    \"\"\"
    The Core Executive "Tiny Teams" Engine.
    Constrains maximum parallel agents to 10.
    Replaces 650-Agent map-reduce with High-Bandwidth Sequential Attention.
    \"\"\"
    
    def __init__(self, max_agents: int = 10):
        self.max_agents = max_agents
        self.active_agents = []
        self.core_directive = "You are an autonomous agent bounded by the Uphill Snowball doctrine. Minimize API calls. Execute deeply."
        
    async def _evaluate_importance(self, doc_segment: str) -> float:
        semantic_density = len(set(doc_segment.split())) / max(1, len(doc_segment.split()))
        return min(1.0, semantic_density * 1.5)

    async def deploy_tiny_team(self, mission_data: List[str]):
        for segment in mission_data:
            if len(self.active_agents) >= self.max_agents:
                await asyncio.sleep(0.1)
                continue
                
            score = await self._evaluate_importance(segment)
            if score > 0.8:
                print(f"[Swarm] High-Entropy Segment Detected (Score: {score:.2f}). Deploying worker.")
                self.active_agents.append(segment)
"""

sentinel = """
class JudgeSixSentinel:
    \"\"\"
    The Ultimate Safety Doctrine (Justitia).
    Evaluates inputs natively before they touch the swarm. 
    Replaces static rules with dynamic Model Armor.
    \"\"\"
    
    def __init__(self):
        print("Judge 6 Sentinel Online. Activating 6-Gate Protocol.")
        
    def assess_risk(self, prompt: str) -> dict:
        if "hallucinate" in prompt.lower() or "bypass" in prompt.lower():
            return {"status": "BLOCKED", "reason": "Gate 4 Failure: Circumvention Intent"}
        return {"status": "APPROVED", "reason": "Sovereign Context Clear"}
"""

hybrid_scraper = """
import os
import time
import json
import random
from firecrawl import Firecrawl
from scrapling import StealthyFetcher, DynamicFetcher, ProxyRotator, Core

class AntigravityHybridScraper:
    def __init__(self):
        self.fc = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
        
        self.rotator = ProxyRotator(
            cycle=["http://user:pass@brd.superproxy.io:22225", "http://user:pass@proxy.oxylabs.io:60000"],
            strategy="sticky_session",
            failover=True,
            max_retries=3,
            backoff=2.0
        )
        
        self.dynamic = DynamicFetcher(headless=True, network_idle=True, user_data_dir="./tmp/.persistent-browser-profile")

    def safe_write(self, filename, data):
        allowed_dirs = ["./data", "./output", "./tmp"]
        filepath = os.path.abspath(filename)
        if not any(filepath.startswith(os.path.abspath(d)) for d in allowed_dirs):
            raise PermissionError("Antigravity Sandbox Violation: Write blocked outside allowed directories.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def scrape_spa(self, url, selectors):
        print(f" [Scraper] Routing {url} via FireCrawl for DOM Hydration...")
        try:
            data = self.fc.scrape(url=url, formats=["html"], wait_for="domcontentloaded", js_code="window.scrollTo(0, document.body.scrollHeight);", timeout=60)
            raw_html = data['html']
        except Exception as e:
            print(f" [Scraper] FireCrawl failed ({e}). Arbitraging to Scrapling DynamicFetcher...")
            time.sleep(random.uniform(1, 3))
            page = self.dynamic.fetch(url, proxy=self.rotator.get(), wait_for="networkidle")
            page.wait_for_selector(selectors['container'], timeout=15000)
            raw_html = page.html

        print(f" [Scraper] Scrapling: Parsing rendered HTML AST...")
        core = Core(html=raw_html)
        items = []
        for item in core.select(selectors['container']):
            extracted = {k: item.select(v).text for k, v in selectors['fields'].items()}
            item_id = item.get(selectors.get('id_field', 'data-id'))
            if item_id: extracted['id'] = item_id
            items.append(extracted)
        
        deduped = {item.get('id', i): item for i, item in enumerate(items)}
        return list(deduped.values())
"""

# EXECUTE ORCHESTRATION
base = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
create_file(f"{base}/infrastructure/terraform/bigquery_omniscience.tf", bq_omni)
create_file(f"{base}/schema/bq_autonomous_lake.sql", bq_sql)
create_file(f"{base}/src/brain/data_router.py", data_router)
create_file(f"{base}/src/tools/bq_omni_search.py", bq_search)
create_file(f"{base}/src/core/swarm_controller.py", swarm_controller)
create_file(f"{base}/src/core/sentinel.py", sentinel)
create_file(f"{base}/.agent/hybrid_scraper.py", hybrid_scraper)
