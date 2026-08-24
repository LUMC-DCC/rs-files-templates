"""Rendering tests for packaged templates."""

from __future__ import annotations

import json

import yaml

from rs_files_templates import (
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    ContributingModel,
    GovernanceModel,
    LicenseModel,
    Person,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    render_many,
    render_text,
)


def test_citation_renders_yaml(author: Person) -> None:
    """CFF output is syntactically valid YAML."""
    rendered = render_text(
        CitationModel(
            project_name="Example",
            project_slug="example",
            urls={"repository": "https://github.com/example/project"},
            authors={"entries": [author]},
        )
    )
    parsed = yaml.safe_load(rendered)
    assert parsed["title"] == "Example"
    assert parsed["authors"][0]["family-names"] == "Lovelace"


def test_codemeta_renders_json(author: Person) -> None:
    """CodeMeta output is syntactically valid JSON."""
    rendered = render_text(
        CodeMetaModel(
            project_name="Example",
            project_slug="example",
            urls={"repository": "https://github.com/example/project"},
            licensing={"license": "MIT"},
            authors={"entries": [author]},
        )
    )
    parsed = json.loads(rendered)
    assert parsed["name"] == "Example"
    assert parsed["author"][0]["familyName"] == "Lovelace"


def test_codemeta_maps_ci_categories_and_supporting_data(author: Person) -> None:
    """Complex RSM values are normalized by the model, not the Jinja layout."""
    rendered = render_text(
        CodeMetaModel(
            project_slug="example",
            urls={"repository": "https://github.com/example/project"},
            include_metadata=True,
            authors={"entries": [author]},
            interfaces={"entries": [{"type": "Library"}]},
            motivation={
                "purpose": "Analyze data",
                "categories": {"entries": ["Data analysis"]},
            },
            software_functions={
                "entries": [
                    {
                        "summary": "Analyze data",
                        "input": [
                            {
                                "format": [
                                    {
                                        "term": "CSV",
                                        "sample_url": "https://example.org/input.csv",
                                    }
                                ]
                            }
                        ],
                    }
                ]
            },
        )
    )
    parsed = json.loads(rendered)
    assert parsed["continuousIntegration"] == "https://github.com/example/project/actions"
    assert parsed["applicationSubCategory"] == ["Data analysis"]
    assert parsed["supportingData"] == [
        {
            "@id": "https://example.org/input.csv",
            "@type": "DataFeed",
            "name": "CSV",
            "url": "https://example.org/input.csv",
        }
    ]


def test_zenodo_renders_normalized_json(author: Person) -> None:
    """Zenodo output maps shared people, grants, and publications."""
    maintainer = Person(
        name="Grace Hopper",
        orcid="https://orcid.org/0000-0002-1825-0097",
        affiliation={"name": "LUMC"},
    )
    rendered = render_text(
        ZenodoModel(
            project_name="Example",
            project_slug="example",
            project_short_description="Example software",
            licensing={"license": "Apache-2.0"},
            keywords={"entries": ["research software"]},
            authors={"entries": [author]},
            maintainers={"entries": [author, maintainer]},
            principal_investigators={"entries": [maintainer]},
            funding={
                "entries": [
                    {"award_number": "10.13039/501100000780::675191"},
                    {"award_number": "local-award"},
                ]
            },
            publications={"entries": [{"doi": "10.1234/example"}]},
        )
    )
    parsed = json.loads(rendered)
    assert parsed["creators"] == [{"name": "Lovelace, Ada"}]
    assert parsed["contributors"] == [
        {
            "affiliation": "LUMC",
            "name": "Grace Hopper",
            "orcid": "0000-0002-1825-0097",
            "type": "ContactPerson",
        }
    ]
    assert parsed["grants"] == [{"id": "10.13039/501100000780::675191"}]
    assert parsed["related_identifiers"] == [
        {
            "identifier": "10.1234/example",
            "relation": "isDocumentedBy",
            "resource_type": "publication-article",
            "scheme": "doi",
        }
    ]


def test_contributing_maps_selected_tools_to_commands() -> None:
    """Contributing guidance keeps command normalization out of the template."""
    rendered = render_text(
        ContributingModel(
            project_manager="poetry",
            quality_tools={"formatter": "ruff", "linter": "ruff", "type_checker": "mypy"},
            test_frameworks={"entries": ["pytest"]},
            test_types={"entries": ["Unit tests"]},
            documentation_builder="sphinx",
            documentation_types={"entries": ["user"]},
            include_metadata=True,
            licensing={"license": "MIT"},
            community_files={"entries": ["CHANGELOG.md"]},
            distribution_channels={"entries": ["PyPI", "Zenodo"]},
        )
    )
    assert "poetry install" in rendered
    assert "poetry add <package>" in rendered
    assert "`poetry run ruff format --check .`" in rendered
    assert "| Metadata | metadata is included | Validate generated metadata files. |" in rendered
    assert "- .zenodo.json" in rendered
    assert "\n\n\n" not in rendered


def test_contributing_omits_unknown_tool_commands() -> None:
    """Selected tools without a safe generic command do not produce guesses."""
    rendered = render_text(
        ContributingModel(
            project_manager="rix",
            quality_tools={"formatter": "styler", "linter": "clang-tidy"},
            test_frameworks={"entries": ["GoogleTest"]},
        )
    )
    assert "## Development setup" not in rendered
    assert "## Local checks" not in rendered
    assert "## Continuous integration" in rendered


def test_all_models_render_without_template_expressions(tmp_path, author: Person) -> None:
    """Every shipped model renders its packaged template cleanly."""
    models = [
        CitationModel(
            project_name="Example", project_slug="example", authors={"entries": [author]}
        ),
        CodeMetaModel(
            project_name="Example", project_slug="example", authors={"entries": [author]}
        ),
        ZenodoModel(project_name="Example", project_slug="example", authors={"entries": [author]}),
        ChangelogModel(),
        CodeOfConductModel(maintainers={"entries": [author]}),
        ContributingModel(),
        GovernanceModel(maintainers={"entries": [author]}),
        LicenseModel(licensing={"license": "Custom project terms\nAll rights reserved."}),
        SecurityModel(maintainers={"entries": [author]}),
        SupportModel(),
    ]
    results = render_many(models, tmp_path)
    assert len(results) == len(models)
    for result in results:
        text = result.path.read_text(encoding="utf-8")
        assert "{{" not in text
        assert "{%" not in text


def test_license_renders_custom_text(monkeypatch) -> None:
    """An unrecognized SPDX value is preserved as custom license text."""
    from rs_files_templates.external.spdx import UnknownSpdxLicense

    def unknown(identifier: str) -> str:
        raise UnknownSpdxLicense(identifier)

    monkeypatch.setattr("rs_files_templates.external.spdx.fetch_spdx_license_text", unknown)
    assert render_text(LicenseModel(licensing={"license": "Custom project terms"})) == (
        "Custom project terms\n"
    )


def test_license_renders_fetched_spdx_text(monkeypatch) -> None:
    """A recognized SPDX identifier renders the fetched full license text."""
    monkeypatch.setattr(
        "rs_files_templates.models.license.resolve_license_text",
        lambda value: "Full MIT license text" if value == "MIT" else "",
    )
    assert render_text(LicenseModel(licensing={"license": "MIT"})) == "Full MIT license text\n"
