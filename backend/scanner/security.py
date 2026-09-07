import asyncio
import ipaddress
import logging
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SecurityBlockedError(Exception):
    """Raised when a request is blocked by SSRF protection."""


def is_ip_allowed(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    
    # Block private, loopback, link-local, multicast, reserved
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return False
        
    return True


async def resolve_hostname(hostname: str) -> list[str]:
    loop = asyncio.get_running_loop()
    try:
        # socket.getaddrinfo returns a list of tuples: (family, type, proto, canonname, sockaddr)
        # sockaddr is a tuple (address, port) for IPv4, or (address, port, flow info, scope id) for IPv6
        addr_info = await loop.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        ips = [info[4][0] for info in addr_info]
        return ips
    except socket.gaierror as e:
        logger.warning(f"Failed to resolve {hostname}: {e}")
        return []


async def security_route_handler(route):
    """
    Playwright route handler to intercept requests, perform DNS resolution,
    and block any that resolve to private or forbidden IPs.
    """
    url = route.request.url
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        await route.abort("blockedbyclient")
        return

    # First, check if the hostname itself looks like a direct IP
    try:
        ip = ipaddress.ip_address(hostname)
        if not is_ip_allowed(str(ip)):
            logger.warning(f"SSRF Protection: Blocked direct IP {url}")
            await route.abort("blockedbyclient")
            return
    except ValueError:
        pass

    # Resolve hostname
    ips = await resolve_hostname(hostname)
    
    if not ips:
        # If it doesn't resolve, let the browser handle the failure natively
        await route.continue_()
        return

    for ip in ips:
        if not is_ip_allowed(ip):
            logger.warning(f"SSRF Protection: Blocked {url} resolving to internal IP {ip}")
            await route.abort("blockedbyclient")
            return

    await route.continue_()
