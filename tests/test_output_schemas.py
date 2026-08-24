"""Network-backed tests for published output schemas."""

from __future__ import annotations

import pytest

from rs_files_templates import CitationModel, CodeMetaModel, Person, ZenodoModel, render_file


@pytest.mark.network
def test_citation_matches_published_schema(tmp_path) -> None:
    """Generated CFF validates against the configured CFF 1.2.0 schema."""
    model = CitationModel(
        project_name="Example",
        project_slug="example",
        urls={"repository": "https://github.com/example/project"},
        authors={
            "entries": [Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")]
        },
    )
    result = render_file(model, tmp_path, validate_schema=True)
    assert result.validated


@pytest.mark.network
def test_codemeta_matches_published_schema(tmp_path) -> None:
    """Generated CodeMeta validates against the configured LUMC schema."""
    model = CodeMetaModel(
        project_name="Example",
        project_slug="example",
        urls={"repository": "https://github.com/example/project"},
        licensing={"license": "MIT"},
        authors={
            "entries": [Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")]
        },
        persistent_identifiers={
            "entries": [{"type": "url", "identifier": "https://example.org/project"}]
        },
    )
    result = render_file(model, tmp_path, validate_schema=True)
    assert result.validated


@pytest.mark.network
def test_zenodo_matches_published_schema(tmp_path) -> None:
    """Generated Zenodo metadata validates against its legacy deposit schema."""
    model = ZenodoModel(
        project_name="Example",
        project_slug="example",
        project_short_description="Example research software",
        licensing={"license": "MIT"},
        authors={
            "entries": [Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")]
        },
        publications={"entries": [{"doi": "10.1234/example"}]},
    )
    result = render_file(model, tmp_path, validate_schema=True)
    assert result.validated
