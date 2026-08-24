"""Network-backed tests for published output schemas."""

from __future__ import annotations

import pytest

from rs_files_templates import (
    BiotoolsModel,
    CitationModel,
    CodeMetaModel,
    Contributor,
    ZenodoModel,
    render_file,
)


@pytest.mark.network
def test_citation_matches_published_schema(tmp_path) -> None:
    """Generated CFF validates against the configured CFF 1.2.0 schema."""
    model = CitationModel(
        project_name="Example",
        project_slug="example",
        urls={"repository": "https://github.com/example/project"},
        contributors={
            "entries": [
                Contributor(
                    name="Ada Lovelace",
                    given_names="Ada",
                    family_names="Lovelace",
                    roles=["Original author"],
                )
            ]
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
        access={
            "type": "free-with-restrictions",
            "details": "https://example.org/access",
        },
        funding={
            "entries": [
                {
                    "funder": "Example Foundation",
                    "funder_identifier": "https://ror.org/012345678",
                    "funder_identifier_type": "ror",
                    "funder_url": "https://example.org/foundation",
                    "award_number": "ABC-123",
                }
            ]
        },
        contributors={
            "entries": [
                Contributor(
                    name="Ada Lovelace",
                    given_names="Ada",
                    family_names="Lovelace",
                    roles=["Original author"],
                )
            ]
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
        contributors={
            "entries": [
                Contributor(
                    name="Ada Lovelace",
                    given_names="Ada",
                    family_names="Lovelace",
                    roles=["Original author"],
                )
            ]
        },
        publications={"entries": [{"doi": "10.1234/example"}]},
    )
    result = render_file(model, tmp_path, validate_schema=True)
    assert result.validated


@pytest.mark.network
def test_biotools_matches_published_schema(tmp_path) -> None:
    """Generated bio.tools metadata validates against the upstream schema."""
    model = BiotoolsModel(
        project_name="Example",
        project_slug="example",
        project_short_description="Example research software",
        urls={"homepage": "https://example.org/project"},
        versioning={"version": "0.1.0"},
        licensing={"license": "MIT"},
        topics={
            "entries": [
                {
                    "term": "Data analysis",
                    "uri": "https://edamontology.org/topic_3474",
                }
            ]
        },
        software_functions={
            "entries": [
                {
                    "operations": [
                        {
                            "term": "Sequence analysis",
                            "uri": "https://edamontology.org/operation_2403",
                        }
                    ]
                }
            ]
        },
        contributors={
            "entries": [
                Contributor(
                    name="Ada Lovelace",
                    given_names="Ada",
                    family_names="Lovelace",
                    roles=["Original author"],
                )
            ]
        },
    )
    result = render_file(model, tmp_path, validate_schema=True)
    assert result.validated
