"""URL validation for incoming scan requests.

This is intentionally narrow for Part 1: it only rejects malformed or
disallowed URLs before a Scan record is created. Real SSRF protection
(blocking private/internal IP ranges, DNS re-binding checks, redirect
inspection, etc.) belongs with the actual scanner and will be added
when that pipeline is introduced - not here.
"""

from urllib.parse import urlsplit, urlunsplit

ALLOWED_SCHEMES = {"http", "https"}


class InvalidUrlError(ValueError):
    """Raised when a submitted URL fails validation."""


def validate_and_normalize_url(raw_url: str) -> str:
    raw_url = (raw_url or "").strip()
    if not raw_url:
        raise InvalidUrlError("URL is required.")

    parts = urlsplit(raw_url)

    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise InvalidUrlError("Only http:// and https:// URLs are allowed.")

    if not parts.netloc:
        raise InvalidUrlError("URL must include a valid host.")

    hostname = parts.hostname or ""
    if "." not in hostname and hostname != "localhost":
        raise InvalidUrlError("URL host looks invalid.")

    # Normalize: lowercase scheme/host, drop fragment, collapse empty path.
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path or "/"

    normalized = urlunsplit((scheme, netloc, path, parts.query, ""))
    return normalized
