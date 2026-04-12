"""
Starlink Ingress Detection & Routing.
Detects if current request is coming via Starlink IP ranges.
"""

import ipaddress

import requests

# Known Starlink IP ranges (Mock - usually fetched from GeoIP DB)
STARLINK_RANGES = ["98.97.0.0/16", "206.214.224.0/19"]


def is_starlink_ip(ip: str) -> bool:
    """Check if IP belongs to Starlink ASN."""
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in ipaddress.ip_network(cidr) for cidr in STARLINK_RANGES)
    except ValueError:
        return False


def get_public_ip() -> str:
    try:
        return requests.get("https://api.ipify.org", timeout=2).text
    except:
        return "127.0.0.1"
