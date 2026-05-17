# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from shared.types import DeploymentZone


def get_allowed_zones(tier: str, data_class: str) -> set[DeploymentZone]:
  """Map the product tier and data classification to allowed physical deployment zones."""
  if data_class == "ITAR" or data_class == "FEDRAMP":
    return {DeploymentZone.US}
  if data_class == "GDPR_STRICT":
    return {DeploymentZone.EU}
  if tier == "GLOBAL":
    return {
      DeploymentZone.US,
      DeploymentZone.EU,
      DeploymentZone.UK,
      DeploymentZone.APAC,
    }
  # Default to home region
  return {DeploymentZone.US}
