import pytest
from scanner.security import is_ip_allowed, resolve_hostname

def test_is_ip_allowed():
    # Allowed
    assert is_ip_allowed("8.8.8.8") is True
    assert is_ip_allowed("1.1.1.1") is True
    
    # Blocked
    assert is_ip_allowed("127.0.0.1") is False
    assert is_ip_allowed("10.0.0.1") is False
    assert is_ip_allowed("192.168.1.1") is False
    assert is_ip_allowed("172.16.0.1") is False
    assert is_ip_allowed("0.0.0.0") is False
    assert is_ip_allowed("169.254.169.254") is False  # AWS metadata
    assert is_ip_allowed("::1") is False

@pytest.mark.asyncio
async def test_resolve_hostname():
    ips = await resolve_hostname("google.com")
    assert len(ips) > 0
    
    # Check that they are allowed
    for ip in ips:
        assert is_ip_allowed(ip)

@pytest.mark.asyncio
async def test_resolve_localhost():
    ips = await resolve_hostname("localhost")
    # depending on OS, could be 127.0.0.1 or ::1
    assert len(ips) > 0
    for ip in ips:
        assert not is_ip_allowed(ip)
