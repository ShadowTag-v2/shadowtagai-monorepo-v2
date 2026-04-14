"""AiU Digital Mall
Governed AI Marketplace with Pre-execution Compliance

The world's first AI marketplace where every model, dataset, and service
must pass AiUCRM validation before listing.

Value Proposition:
- Verified creators monetize risk-free AI services
- Enterprises shop only from certified safe vendors
- Governments and hospitals purchase with full legal traceability

Target Metrics (2030):
- GMV: $12B
- Fee: 12% = $1.44B ARR
- Margin: 85%
- EV: $10B
"""

from .marketplace import DigitalMall, Product, Transaction, Vendor
from .verification import ProductVerification, VendorVerification

__version__ = "1.0.0"
__all__ = [
    "DigitalMall",
    "Product",
    "ProductVerification",
    "Transaction",
    "Vendor",
    "VendorVerification",
]
