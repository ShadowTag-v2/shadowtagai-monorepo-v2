# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pydantic schemas for GitHub artifact generation (shared envelope)."""

from typing import List, Literal, Union
from pydantic import BaseModel


class GitHubCommonSpec(BaseModel):
    title: str
    summary: str
    tags: list[str]
    token: str  # short unique token; used in filename and embedded in body
    created_at: str


class Section(BaseModel):
    heading: str
    body: str


class MarkdownContent(BaseModel):
    sections: list[Section]


class CodeSnippet(BaseModel):
    body: str


class PythonContent(BaseModel):
    functions: list[CodeSnippet]
    classes: list[CodeSnippet]
    example: str


class KVPair(BaseModel):
    key: str
    value: str


class JSONContent(BaseModel):
    attributes: list[KVPair]
    metadata: list[KVPair]


class GitHubArtifact(BaseModel):
    type: Literal["markdown", "python", "json"]
    common: GitHubCommonSpec
    content: MarkdownContent | PythonContent | JSONContent
