"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from rs_files_templates import Contributor


@pytest.fixture
def author() -> Contributor:
    """Return a valid example author."""
    return Contributor(
        name="Ada Lovelace",
        given_names="Ada",
        family_names="Lovelace",
        roles=["Original author"],
    )
