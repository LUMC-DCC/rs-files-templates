"""Resolve SPDX license identifiers to authoritative full license text."""

from __future__ import annotations

import json
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

SPDX_LICENSE_URL = "https://spdx.org/licenses/{identifier}.json"


class UnknownSpdxLicense(ValueError):
    """Raised when SPDX does not recognize a supplied identifier."""


@lru_cache(maxsize=64)
def fetch_spdx_license_text(identifier: str, timeout: float = 15.0) -> str:
    """Fetch and cache the full text for one SPDX license identifier."""
    normalized = identifier.strip()
    url = SPDX_LICENSE_URL.format(identifier=quote(normalized, safe=""))
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read())
    except HTTPError as error:
        if error.code == 404:
            raise UnknownSpdxLicense(normalized) from error
        raise RuntimeError(f"Could not fetch SPDX license {normalized!r}") from error
    except (OSError, URLError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not fetch SPDX license {normalized!r}") from error

    if payload.get("licenseId") != normalized or not payload.get("licenseText"):
        raise RuntimeError(f"SPDX returned invalid license data for {normalized!r}")
    return str(payload["licenseText"]).rstrip()


def resolve_license_text(value: str | None) -> str:
    """Resolve an SPDX identifier, or preserve unrecognized input as custom text."""
    supplied = str(value or "").strip()
    if not supplied:
        return "REPLACE_WITH_LICENSE_TEXT"
    if "\n" in supplied:
        return supplied
    try:
        return fetch_spdx_license_text(supplied)
    except UnknownSpdxLicense:
        return supplied
