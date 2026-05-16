# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load variables from .env file into the os environment
load_dotenv()


@dataclass(frozen=True)
class Settings:
  vector_backend: str = os.getenv("VECTOR_BACKEND", "chroma")  # chroma|memory
  openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
  eval_judge_model: str = os.getenv("EVAL_JUDGE_MODEL", "gpt-4-turbo")
  deployment_zone: str = os.getenv("DEPLOYMENT_ZONE", "us")

  # Vector DB settings
  chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./.chroma_db")

  # Observability & GCP
  gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4")
  sigstore_identity: str = os.getenv(
    "SIGSTORE_IDENTITY",
    "headless-runner@shadowtag-omega-v4.iam.gserviceaccount.com",
  )
  prompt_registry_db_url: str = os.getenv(
    "PROMPT_REGISTRY_DB_URL", "sqlite:///prompt_registry.db"
  )
  pii_salt: str = os.getenv("PII_SALT", "rotate-me")


settings = Settings()
