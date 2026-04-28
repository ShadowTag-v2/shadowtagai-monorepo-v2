# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Repo Oracle — Workspace Indexer and Pattern Query Engine.

Indexes the monorepo's truth surfaces (manifest, packages, scripts,
skills) and answers "does X already exist?" queries to prevent
reinvention and enforce reuse.

Usage:
    from packages.repo_oracle import RepoOracle

    oracle = RepoOracle(repo_root=Path("."))
    oracle.index()
    print(oracle.has_package("aiyou-core"))
    print(oracle.has_script("auth_github_app"))
"""

from packages.repo_oracle.oracle import RepoOracle

__all__ = ["RepoOracle"]
__version__ = "1.0.0"
