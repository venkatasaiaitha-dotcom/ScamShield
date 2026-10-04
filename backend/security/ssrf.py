import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_HOSTNAMES = {
    "localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal",
    "instance-data", "169.254.169.254"
}

def is_safe_external_url(url: str) -> Tuple[bool, str]:
    """
    Validates that a URL does not point to internal networks, localhost,
    link-local, cloud metadata services, or non-HTTP schemes (SSRF Protection).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False, f"Unsupported scheme '{parsed.scheme}'. Only http and https are permitted."

        hostname = (parsed.hostname or "").lower().strip()
        if not hostname:
            return False, "URL hostname is missing or empty."

        if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".localhost") or hostname.endswith(".internal"):
            return False, f"Access to internal or loopback host '{hostname}' is strictly forbidden."

        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                return False, f"Access to private/reserved IP '{hostname}' is strictly forbidden."
        except ValueError:
            # It's a domain name; do not resolve arbitrarily to prevent DNS rebinding or internal scanning
            pass

        return True, "URL is safe for metadata inspection."
    except Exception as e:
        return False, f"Malformed URL: {str(e)}"
