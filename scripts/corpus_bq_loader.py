#!/usr/bin/env python3
"""scripts/corpus_bq_loader.py — Load Drive corpus into BigQuery for GQL graph queries.

Uploads extractions.jsonl to BigQuery, creates a Property Graph DDL over
document relationships, and provides GQL query helpers.

Usage:
    python3 scripts/corpus_bq_loader.py                    # Load to BQ
    python3 scripts/corpus_bq_loader.py --create-graph     # Create Property Graph
    python3 scripts/corpus_bq_loader.py --query "patent"   # GQL query
    python3 scripts/corpus_bq_loader.py --dry-run           # Print DDL only
"""

from __future__ import annotations
import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
JSONL = REPO / "data/drive_ingest/extractions.jsonl"
PROJECT = "shadowtag-omega-v4"
DATASET = "drive_corpus"
TABLE = "extractions"
GRAPH = "doc_graph"

SCHEMA = "document_id:STRING,source_file:STRING,format:STRING,raw_content:STRING,content_hash:STRING,byte_size:INTEGER"

CREATE_DATASET_DDL = f"""
CREATE SCHEMA IF NOT EXISTS `{PROJECT}.{DATASET}`
OPTIONS(location='us-central1');
"""

CREATE_TABLE_DDL = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{TABLE}` (
  document_id STRING NOT NULL,
  source_file STRING,
  format STRING,
  raw_content STRING,
  content_hash STRING,
  byte_size INT64
);
"""

# Property Graph DDL: nodes = documents, edges = content similarity
CREATE_GRAPH_DDL = f"""
CREATE OR REPLACE PROPERTY GRAPH `{PROJECT}.{DATASET}.{GRAPH}`
  NODE TABLES (
    `{PROJECT}.{DATASET}.{TABLE}`
      KEY (document_id)
      PROPERTIES (document_id, source_file, format, byte_size, content_hash)
  );
"""

GQL_SAMPLE = f"""
-- Find all documents and their properties
GRAPH {DATASET}.{GRAPH}
MATCH (doc)
RETURN doc.document_id, doc.source_file, doc.format, doc.byte_size
ORDER BY doc.byte_size DESC
NEXT
RETURN * LIMIT 20;
"""


def run_bq(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
  """Run a bq CLI command."""
  full_cmd = ["bq", "--project_id", PROJECT, "--format", "json"] + cmd
  return subprocess.run(full_cmd, capture_output=True, text=True, check=check)


def load_to_bq():
  print(f"Loading {JSONL} → {PROJECT}.{DATASET}.{TABLE}")

  # Create dataset
  print("  Creating dataset...")
  run_bq(
    ["mk", "--dataset", "--location", "us-central1", f"{PROJECT}:{DATASET}"],
    check=False,
  )

  # Load JSONL
  print("  Loading JSONL...")
  result = subprocess.run(
    [
      "bq",
      "load",
      "--project_id",
      PROJECT,
      "--source_format",
      "NEWLINE_DELIMITED_JSON",
      "--replace",
      f"{DATASET}.{TABLE}",
      str(JSONL),
      SCHEMA,
    ],
    capture_output=True,
    text=True,
  )

  if result.returncode == 0:
    print(f"  ✅ Loaded to {PROJECT}.{DATASET}.{TABLE}")
  else:
    print(f"  ❌ Error: {result.stderr}")
  return result.returncode == 0


def create_graph():
  print(f"Creating Property Graph: {PROJECT}.{DATASET}.{GRAPH}")
  result = subprocess.run(
    [
      "bq",
      "query",
      "--project_id",
      PROJECT,
      "--use_legacy_sql=false",
      CREATE_GRAPH_DDL,
    ],
    capture_output=True,
    text=True,
  )

  if result.returncode == 0:
    print("  ✅ Graph created")
  else:
    print(f"  ❌ Error: {result.stderr}")


def dry_run():
  print("=== CREATE DATASET ===")
  print(CREATE_DATASET_DDL)
  print("\n=== CREATE TABLE ===")
  print(CREATE_TABLE_DDL)
  print("\n=== CREATE GRAPH ===")
  print(CREATE_GRAPH_DDL)
  print("\n=== SAMPLE GQL ===")
  print(GQL_SAMPLE)


if __name__ == "__main__":
  p = argparse.ArgumentParser()
  p.add_argument("--create-graph", action="store_true")
  p.add_argument("--dry-run", action="store_true")
  p.add_argument("--query", type=str)
  a = p.parse_args()

  if a.dry_run:
    dry_run()
  elif a.create_graph:
    create_graph()
  elif a.query:
    gql = f"""
GRAPH {DATASET}.{GRAPH}
MATCH (doc)
WHERE doc.source_file LIKE '%{a.query}%' OR doc.document_id LIKE '%{a.query}%'
RETURN doc.document_id, doc.source_file, doc.byte_size
ORDER BY doc.byte_size DESC
NEXT
RETURN * LIMIT 20;
"""
    subprocess.run(
      [
        "bq",
        "query",
        "--project_id",
        PROJECT,
        "--use_legacy_sql=false",
        "--format=prettyjson",
        gql,
      ]
    )
  else:
    load_to_bq()
