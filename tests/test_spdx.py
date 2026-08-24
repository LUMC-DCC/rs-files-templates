"""Tests for SPDX full-license-text resolution."""

import pytest

from rs_files_templates.external.spdx import fetch_spdx_license_text


@pytest.mark.network
def test_fetch_spdx_license_text() -> None:
    """A recognized identifier resolves to authoritative full text."""
    text = fetch_spdx_license_text("MIT")
    assert "MIT License" in text
    assert "Permission is hereby granted" in text
