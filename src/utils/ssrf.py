import socket
import ipaddress

class SSRFGuard:
    def __init__(self):
        self.blocked = [ipaddress.ip_network('169.254.0.0/16'), ipaddress.ip_network('100.64.0.0/10')]

    def resolve_and_verify(self, hostname: str):
        ip_str = socket.gethostbyname(hostname) # Resolve before TCP handshake
        ip = ipaddress.ip_address(ip_str)
        
        if ip.is_loopback: return ip_str
        for net in self.blocked:
            if ip in net:
                raise PermissionError(f"SSRF BLOCK: Attempt to access internal/CGNAT IP: {ip_str}")
        return ip_str
