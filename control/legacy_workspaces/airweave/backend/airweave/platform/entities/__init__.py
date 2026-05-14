# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""The Airweave entities module.

Contains entity schemas for various data sources and destinations.
"""

from ._base import BaseEntity, Breadcrumb, CodeFileEntity, FileEntity
from .github import (
    GitHubCodeFileEntity,
    GithubContentEntity,
    GitHubDirectoryEntity,
    GitHubFileDeletionEntity,
    GithubRepoEntity,
    GitHubRepositoryEntity,
)

__all__ = [
    "BaseEntity",
    "Breadcrumb",
    "CodeFileEntity",
    "FileEntity",
    "GitHubCodeFileEntity",
    "GitHubDirectoryEntity",
    "GitHubFileDeletionEntity",
    "GitHubRepositoryEntity",
    "GithubRepoEntity",
    "GithubContentEntity",
]
