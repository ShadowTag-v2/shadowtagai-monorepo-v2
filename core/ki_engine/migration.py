# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Migration — Item 21: Migration script from KI format to memory-kernel atoms.

Converts existing metadata.json KIs into memory-kernel compatible format
and generates a migration report.

Also handles reverse: memory-kernel atoms → our KI format.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.ki_engine.schema import (
    KIMetadata,
    KIType,
    generate_ki_id,
)


@dataclass
class MigrationResult:
    """Result of KI migration."""

    migrated: list[str]
    skipped: list[str]
    errors: list[str]
    upgraded_fields: dict[str, list[str]]  # KI name → list of fields added


def infer_ki_type(ki: dict) -> KIType:
    """Infer KI type from existing metadata (heuristic).

    Uses name, summary, and tags to guess the appropriate type.
    """
    name_lower = (ki.get("name", "") + " " + ki.get("summary", "")).lower()
    [t.lower() for t in ki.get("tags", [])]

    # Decision indicators
    if any(w in name_lower for w in ["decision", "chose", "selected", "verdict", "approved"]):
        return KIType.DECISION

    # Constraint indicators
    if any(w in name_lower for w in ["constraint", "rule", "forbidden", "must", "never", "always"]):
        return KIType.CONSTRAINT

    # Procedure indicators
    if any(w in name_lower for w in ["how to", "procedure", "workflow", "steps", "guide"]):
        return KIType.PROCEDURE

    # Preference indicators
    if any(w in name_lower for w in ["prefer", "preference", "style", "like"]):
        return KIType.PREFERENCE

    # Open question indicators
    if any(w in name_lower for w in ["question", "todo", "investigate", "unclear", "unknown"]):
        return KIType.OPEN_QUESTION

    # Entity summary indicators
    if any(w in name_lower for w in ["overview", "summary", "description", "about"]):
        return KIType.ENTITY_SUMMARY

    # Belief indicators
    if any(w in name_lower for w in ["believe", "hypothesis", "suspect", "think", "seems"]):
        return KIType.BELIEF

    # Conflict indicators
    if any(w in name_lower for w in ["conflict", "contradiction", "inconsistent", "mismatch"]):
        return KIType.CONFLICT

    # Default: fact
    return KIType.FACT


def migrate_ki_metadata(
    ki_dir: Path,
    dry_run: bool = True,
) -> MigrationResult:
    """Migrate existing KI metadata.json files to enhanced schema.

    Adds new fields (ki_type, status, confidence, ttl_days, classification)
    to existing metadata.json files without removing any existing fields.

    Args:
        ki_dir: Path to KI directory.
        dry_run: If True, report changes without writing.

    Returns:
        MigrationResult with details.
    """
    result = MigrationResult(
        migrated=[],
        skipped=[],
        errors=[],
        upgraded_fields={},
    )

    if not ki_dir.exists():
        result.errors.append(f"KI directory not found: {ki_dir}")
        return result

    for ki_path in sorted(ki_dir.iterdir()):
        if not ki_path.is_dir():
            continue

        metadata_file = ki_path / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            with open(metadata_file) as f:
                raw = json.load(f)

            # Track which fields need adding
            new_fields: list[str] = []

            # Infer type if missing
            if "ki_type" not in raw:
                raw["ki_type"] = infer_ki_type(raw).value
                new_fields.append("ki_type")

            # Add status if missing
            if "status" not in raw:
                raw["status"] = "active"
                new_fields.append("status")

            # Add confidence if missing
            if "confidence" not in raw:
                # Higher confidence for facts/decisions, lower for beliefs
                ki_type = raw.get("ki_type", "fact")
                if ki_type in ("fact", "decision", "constraint"):
                    raw["confidence"] = 1.0
                elif ki_type == "belief":
                    raw["confidence"] = 0.7
                else:
                    raw["confidence"] = 0.9
                new_fields.append("confidence")

            # Add classification if missing
            if "classification" not in raw:
                raw["classification"] = "team"
                new_fields.append("classification")

            # Normalize date fields
            if "createdAt" in raw and "created" not in raw:
                raw["created"] = raw.pop("createdAt")
                new_fields.append("created (renamed from createdAt)")
            if "updatedAt" in raw and "updated" not in raw:
                raw["updated"] = raw.pop("updatedAt")
                new_fields.append("updated (renamed from updatedAt)")

            if not new_fields:
                result.skipped.append(ki_path.name)
                continue

            result.upgraded_fields[ki_path.name] = new_fields

            if not dry_run:
                with open(metadata_file, "w") as f:
                    json.dump(raw, f, indent=2)
                    f.write("\n")

            result.migrated.append(ki_path.name)

        except (json.JSONDecodeError, OSError) as e:
            result.errors.append(f"{ki_path.name}: {e}")

    return result


def export_to_memory_kernel_format(
    ki_dir: Path,
    output_dir: Path,
) -> int:
    """Export KIs to memory-kernel compatible markdown atoms.

    Creates markdown files with YAML frontmatter in memory-kernel format.

    Args:
        ki_dir: Source KI directory.
        output_dir: Output directory for atoms.

    Returns:
        Number of atoms exported.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for ki_path in sorted(ki_dir.iterdir()):
        if not ki_path.is_dir():
            continue

        metadata_file = ki_path / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            ki = KIMetadata.load(metadata_file)

            # Generate atom ID
            atom_id = generate_ki_id(ki.ki_type, ki.name)

            # Build YAML frontmatter
            lines = [
                "---",
                f"id: {atom_id}",
                f"type: {ki.ki_type.value}",
                f"status: {ki.status.value}",
                f"confidence: {ki.confidence}",
                f"created_at: {ki.created}",
                f"updated_at: {ki.updated}",
                f"classification: {ki.classification.value}",
            ]
            if ki.ttl_days is not None:
                lines.append(f"ttl_days: {ki.ttl_days}")
            if ki.tags:
                lines.append("scope:")
                lines.append(f"  tags: [{', '.join(ki.tags)}]")
            lines.append("---")
            lines.append("")
            lines.append(ki.summary)
            lines.append("")

            # Write atom file
            atom_file = output_dir / f"{atom_id}.md"
            atom_file.write_text("\n".join(lines))
            count += 1

        except (json.JSONDecodeError, OSError):
            continue

    return count
