"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from rs_files_templates import Person


@pytest.fixture
def author() -> Person:
    """Return a valid example author."""
    return Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")
