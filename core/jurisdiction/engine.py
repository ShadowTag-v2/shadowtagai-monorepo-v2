# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from core.jurisdiction.policies import get_allowed_zones
from shared.config import settings
from shared.types import DeploymentZone


class JurisdictionEngine:
  """Enforces that execution strictly occurs within an allowed physical boundary."""

  def __init__(self, current_zone: str = settings.deployment_zone):
    try:
      self.current_zone = DeploymentZone(current_zone)
    except ValueError:
      self.current_zone = DeploymentZone.US

  def check_routing_allowed(self, client_tier: str, data_class: str) -> bool:
    allowed = get_allowed_zones(client_tier, data_class)
    return self.current_zone in allowed

  def raise_if_prohibited(self, client_tier: str, data_class: str) -> None:
    if not self.check_routing_allowed(client_tier, data_class):
      raise PermissionError(
        f"[JURISDICTION_BLOCK] Execution in {self.current_zone.value} prohibited for tier={client_tier}, class={data_class}."
      )
