"""AiY Aerospace Expansion Module (Cor.19)
========================================

Comprehensive aerospace and edge compute infrastructure system integrating:
- Civil aviation AI verification and compliance (DO-178C, DO-326A)
- Defense-grade AI governance kernels
- Starlink + CoreWeave + Tesla edge mesh architecture
- Satellite GPU edge compute infrastructure
- Cell tower GPU integration
- Economic modeling and valuation systems

Part of the ShadowTag-v4 global infrastructure ecosystem.
"""

__version__ = "1.0.0"
__author__ = "ShadowTag-v4 Infrastructure Team"
__license__ = "MIT"

from .economics.roi_calculator import ROICalculator
from .infrastructure.edge_mesh import EdgeMeshArchitecture
from .models.business_plan import AerospaceBusinessPlan
from .valuation.enterprise_value import EnterpriseValuationModel

__all__ = [
    "AerospaceBusinessPlan",
    "EdgeMeshArchitecture",
    "EnterpriseValuationModel",
    "ROICalculator",
]
