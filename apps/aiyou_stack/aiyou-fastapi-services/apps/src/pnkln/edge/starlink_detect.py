# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Starlink Detection Agent
-----------------------
Identifies if the current request session is originating from a Starlink satellite connection.
Used to route traffic to local CoreWeave edge pods.

Author: Pnkln Strategy
Date: 2025-12-10
"""

import argparse
import ipaddress
import json
from typing import Any

# Mock Database of Starlink IP Ranges (CIDR blocks)
# In production, this would be a live lookup against GeoIP/ASN databases
STARLINK_IPV4_RANGES = ["98.97.0.0/16", "206.214.224.0/19", "129.222.0.0/16"]


def is_starlink_ip(ip_addr: str) -> bool:
    """Checks if an IP address belongs to known Starlink CIDR blocks."""
    try:
        ip = ipaddress.ip_address(ip_addr)
        return any(ip in ipaddress.ip_network(cidr) for cidr in STARLINK_IPV4_RANGES)
    except ValueError:
        return False


def get_routing_decision(ip_addr: str) -> dict[str, Any]:
    """Returns the routing payload based on ingress source."""
    is_satellite = is_starlink_ip(ip_addr)

    return {
        "ingress_ip": ip_addr,
        "is_satellite": is_satellite,
        "provider": "SpaceX Starlink" if is_satellite else "Standard ISP",
        "routing_action": {
            "use_edge_node": is_satellite,
            "target_gateway": "us-west-denver-01" if is_satellite else "cloud-central",
            "latency_target_ms": 50 if is_satellite else 150,
        },
        "billing_tier": "edge_premium" if is_satellite else "standard",
    }


def main():
    parser = argparse.ArgumentParser(description="Starlink Ingress Detector")
    parser.add_argument("--test-ip", type=str, help="IP address to test", required=True)
    args = parser.parse_args()

    decision = get_routing_decision(args.test_ip)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
