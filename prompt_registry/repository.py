# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from prompt_registry.models import Base, PromptTraceRecord
from shared.config import settings
from shared.types import PromptExecutionRecord


class PromptTraceStore:
  def __init__(self, db_url: str = settings.prompt_registry_db_url):
    self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def log_execution(self, record: PromptExecutionRecord) -> None:
    with self.Session() as session:
      db_record = PromptTraceRecord(
        trace_id=record.trace_id,
        prompt_id=record.prompt_id,
        prompt_version=record.prompt_version,
        agent_id=record.agent_id,
        model=record.model,
        input_hash=record.input_hash,
        output_hash=record.output_hash,
        tags=record.tags,
      )
      session.add(db_record)
      session.commit()

  def get_traces_by_prompt(
    self, prompt_id: str, limit: int = 100
  ) -> list[PromptExecutionRecord]:
    with self.Session() as session:
      rows = (
        session.query(PromptTraceRecord)
        .filter_by(prompt_id=prompt_id)
        .limit(limit)
        .all()
      )
      return [
        PromptExecutionRecord(
          trace_id=r.trace_id,
          prompt_id=r.prompt_id,
          prompt_version=r.prompt_version,
          agent_id=r.agent_id,
          model=r.model,
          input_hash=r.input_hash,
          output_hash=r.output_hash,
          tags=r.tags,
        )
        for r in rows
      ]
