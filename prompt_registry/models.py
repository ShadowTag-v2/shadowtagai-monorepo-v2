# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PromptTraceRecord(Base):
  __tablename__ = "prompt_traces"
  trace_id = Column(String, primary_key=True)
  prompt_id = Column(String, nullable=False, index=True)
  prompt_version = Column(String, nullable=False)
  agent_id = Column(String, index=True)
  model = Column(String, nullable=False)
  input_hash = Column(String, nullable=False)
  output_hash = Column(String, nullable=False)
  tags = Column(JSON, default=dict)
