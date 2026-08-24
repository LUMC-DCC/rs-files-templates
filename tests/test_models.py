"""Tests for per-file Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from rs_files_templates import CitationModel, Contributor, Person, SecurityModel


def test_person_requires_usable_name() -> None:
    """People must have a display name or structured name."""
    with pytest.raises(ValidationError):
        Person(given_names="Ada")


def test_contributor_requires_a_role() -> None:
    """The updated RSM contributor type cannot omit its project roles."""
    with pytest.raises(ValidationError):
        Contributor(name="Ada Lovelace", roles=[])


def test_file_models_reject_unrelated_fields() -> None:
    """A file model does not silently accept another generator's fields."""
    with pytest.raises(ValidationError):
        SecurityModel(project_name="not-a-security-field")


def test_json_round_trip(author: Contributor) -> None:
    """File models can be loaded from their own JSON representation."""
    original = CitationModel(
        project_name="Example", project_slug="example", contributors={"entries": [author]}
    )
    restored = CitationModel.from_json(original.model_dump_json())
    assert restored == original
