"""Rendering tests for packaged templates."""

from __future__ import annotations

import json
import zipfile

import yaml

from rs_files_templates import (
    BiotoolsModel,
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    ContributingModel,
    Contributor,
    DocumentationDeploymentModel,
    DocumentationDeveloperModel,
    DocumentationLegalModel,
    DocumentationOverviewModel,
    DocumentationReferenceModel,
    DocumentationUserModel,
    GovernanceModel,
    IssueTemplateModel,
    LicenseModel,
    Person,
    PullRequestTemplateModel,
    ReadmeModel,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    render_many,
    render_readme_text,
    render_text,
)


def test_documentation_pages_render_as_independent_rsm_models(tmp_path) -> None:
    """Every documentation page should render without archive or presentation inputs."""
    models = [
        DocumentationOverviewModel(
            project_name="Example",
            project_slug="example",
            project_short_description="Reusable research software.",
            topics={
                "entries": [
                    {
                        "term": "Data management",
                        "uri": "https://edamontology.org/topic_3071",
                    }
                ]
            },
        ),
        DocumentationUserModel(
            project_name="Example",
            project_slug="example",
            project_manager="uv",
            programming_languages={"entries": [{"name": "Python"}]},
        ),
        DocumentationDeploymentModel(project_name="Example"),
        DocumentationDeveloperModel(project_name="Example", project_manager="uv"),
        DocumentationReferenceModel(project_name="Example"),
        DocumentationLegalModel(project_name="Example", licensing={"license": "MIT"}),
    ]

    results = render_many(models, tmp_path)

    assert [result.path.name for result in results] == [
        "overview.md",
        "usage.md",
        "deployment.md",
        "developer.md",
        "reference.md",
        "legal.md",
    ]
    assert "# Example overview" in (tmp_path / "overview.md").read_text()
    assert (
        "[Data management](https://edamontology.org/topic_3071)"
        in (tmp_path / "overview.md").read_text()
    )
    assert "python -m pip install ." in (tmp_path / "usage.md").read_text()
    assert "uv sync --all-extras" in (tmp_path / "developer.md").read_text()


def test_readme_renders_complete_standalone_project_entry_point() -> None:
    """README generation should remain useful without a repository template."""
    rendered = render_readme_text(
        ReadmeModel(
            project_name="Example Analyzer",
            project_slug="example-analyzer",
            project_short_description="Analyze research data reproducibly.",
            project_long_description="A reusable analyzer for structured datasets.",
            versioning={"version": "0.1.0"},
            motivation={"purpose": "Turn raw tables into validated summaries."},
            topics={"entries": [{"term": "Data analysis"}]},
            audiences={"entries": ["Researchers (academia)"]},
            urls={
                "repository": "https://github.com/example/analyzer",
                "documentation": "https://example.org/docs",
            },
            include_metadata=True,
            support_routes={
                "entries": [
                    {
                        "system": "Issue tracker",
                        "url": "https://github.com/example/analyzer/issues",
                    }
                ]
            },
            licensing={"license": "MIT"},
            access={"type": "free", "details": "Available without charge."},
            software_functions={"entries": [{"cmd": "example-analyzer input.csv"}]},
        )
    )

    for heading in (
        "## Purpose",
        "## Research Topics",
        "## Intended Audience",
        "## Installation",
        "## Usage",
        "## Citation",
        "## Support",
        "## Access",
        "## Legal and Licensing",
    ):
        assert heading in rendered
    assert "Analyze research data reproducibly." in rendered
    assert "- Data analysis" in rendered
    assert "example-analyzer input.csv" in rendered
    assert "CITATION.cff" in rendered


def test_readme_resolves_installation_and_support_from_rsm() -> None:
    """README setup and linked files should be derived from RSM fields in place."""
    assert "badges" not in ReadmeModel.model_fields
    assert "installation" not in ReadmeModel.model_fields
    assert "usage" not in ReadmeModel.model_fields

    rendered = render_readme_text(
        ReadmeModel(
            project_name="Example",
            project_slug="example",
            project_manager="uv",
            distribution_channels={"entries": ["PyPI"]},
            software_functions={"entries": [{"cmd": "example --help"}]},
            include_metadata=True,
            community_files={"entries": ["SUPPORT.md", "CONTRIBUTING.md"]},
        )
    )

    assert "python -m pip install example" in rendered
    assert "example --help" in rendered
    assert "[`CITATION.cff`](CITATION.cff)" in rendered
    assert "[`SUPPORT.md`](SUPPORT.md)" in rendered


def test_citation_renders_yaml(author: Person) -> None:
    """CFF output is syntactically valid YAML."""
    rendered = render_text(
        CitationModel(
            project_name="Example",
            project_slug="example",
            urls={"repository": "https://github.com/example/project"},
            contributors={"entries": [author]},
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
            contributors={"entries": [author]},
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
            contributors={"entries": [author]},
            interfaces={"entries": [{"type": "Library"}]},
            motivation={"purpose": "Analyze data"},
            topics={"entries": [{"uri": "https://edamontology.org/topic_0080"}]},
            software_functions={
                "entries": [
                    {
                        "operations": [{"uri": "https://edamontology.org/operation_2939"}],
                        "inputs": [
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
    assert parsed["schema:featureList"] == ["https://edamontology.org/operation_2939"]
    assert parsed["applicationSubCategory"] == ["https://edamontology.org/topic_0080"]
    assert parsed["supportingData"] == [
        {
            "@id": "https://example.org/input.csv",
            "@type": "DataFeed",
            "name": "CSV",
            "url": "https://example.org/input.csv",
        }
    ]


def test_codemeta_maps_access_and_structured_funders() -> None:
    """Access terms and funder identifiers should remain machine-readable."""
    rendered = render_text(
        CodeMetaModel(
            project_name="Example",
            project_slug="example",
            access={
                "type": "free-with-restrictions",
                "details": "https://example.org/access",
            },
            funding={
                "entries": [
                    {
                        "funder": "Example Foundation",
                        "funder_identifier": "012345678",
                        "funder_identifier_type": "ror",
                        "funder_url": "https://example.org/foundation",
                        "award_number": "ABC-123",
                    }
                ]
            },
        )
    )
    parsed = json.loads(rendered)
    assert parsed["isAccessibleForFree"] is True
    assert parsed["schema:usageInfo"] == "https://example.org/access"
    assert parsed["funder"] == [
        {
            "@id": "https://ror.org/012345678",
            "@type": "Organization",
            "name": "Example Foundation",
            "url": "https://example.org/foundation",
        }
    ]
    assert parsed["funding"] == ["ABC-123"]


def test_codemeta_maps_commercial_access_and_prose_details() -> None:
    """Commercial access and prose terms should retain their meaning."""
    parsed = json.loads(
        render_text(
            CodeMetaModel(
                project_name="Example",
                project_slug="example",
                access={
                    "type": "commercial",
                    "details": "A paid institutional subscription is required.",
                },
            )
        )
    )
    assert parsed["isAccessibleForFree"] is False
    assert parsed["schema:usageInfo"] == {
        "@type": "CreativeWork",
        "description": "A paid institutional subscription is required.",
    }


def test_codemeta_subcategory_falls_back_to_topic_term() -> None:
    """A topic without a URI still contributes its term (schema allows Text or URL)."""
    rendered = render_text(
        CodeMetaModel(
            project_name="Example",
            project_slug="example",
            topics={
                "entries": [
                    {"uri": "https://edamontology.org/topic_0080"},
                    {"term": "Arcade Game"},
                ]
            },
        )
    )
    parsed = json.loads(rendered)
    assert parsed["applicationSubCategory"] == [
        "https://edamontology.org/topic_0080",
        "Arcade Game",
    ]


def test_zenodo_renders_normalized_json(author: Person) -> None:
    """Zenodo output maps shared people, grants, and publications."""
    maintainer = Contributor(
        name="Grace Hopper",
        orcid="https://orcid.org/0000-0002-1825-0097",
        affiliations=[{"name": "LUMC"}],
        roles=["Maintainer", "Principal investigator"],
    )
    rendered = render_text(
        ZenodoModel(
            project_name="Example",
            project_slug="example",
            project_short_description="Example software",
            licensing={"license": "Apache-2.0"},
            keywords={"entries": ["research software"]},
            contributors={"entries": [author, maintainer]},
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


def test_biotools_renders_registry_metadata(author: Person) -> None:
    """bio.tools output maps RSM discovery and function metadata."""
    rendered = render_text(
        BiotoolsModel(
            project_name="Example Analyzer",
            project_slug="example-analyzer",
            project_short_description="Analyze biological sequence data.",
            development_status="active",
            versioning={"version": "0.2.0"},
            urls={
                "homepage": "https://example.org/analyzer",
                "repository": "https://github.com/example/analyzer",
                "documentation": "https://example.org/analyzer/docs",
            },
            registries={"entries": [{"name": "bio.tools", "url_or_id": "example-analyzer"}]},
            persistent_identifiers={"entries": [{"type": "doi", "identifier": "10.1234/example"}]},
            topics={
                "entries": [
                    {
                        "term": "Data analysis",
                        "uri": "https://edamontology.org/topic_3474",
                    }
                ]
            },
            interfaces={"entries": [{"type": "Command-line tool"}]},
            operating_systems={"entries": [{"name": "macOS"}, {"name": "Linux"}]},
            programming_languages={"entries": [{"name": "Python"}]},
            licensing={"license": "MIT"},
            access={"type": "free-with-restrictions"},
            software_functions={
                "entries": [
                    {
                        "operations": [
                            {
                                "term": "Sequence analysis",
                                "uri": "https://edamontology.org/operation_2403",
                            }
                        ],
                        "inputs": [
                            {
                                "data": {
                                    "term": "Sequence",
                                    "uri": "https://edamontology.org/data_2044",
                                },
                                "format": [
                                    {
                                        "term": "FASTA",
                                        "uri": "https://edamontology.org/format_1929",
                                    }
                                ],
                            }
                        ],
                        "cmd": "example-analyzer input.fasta",
                    }
                ]
            },
            publications={"entries": [{"doi": "10.1234/example", "preferred": True}]},
            contributors={"entries": [author]},
        )
    )

    parsed = json.loads(rendered)
    assert len(parsed) == 1
    tool = parsed[0]
    assert tool["name"] == "Example Analyzer"
    assert tool["homepage"] == "https://example.org/analyzer"
    assert tool["biotoolsID"] == "example-analyzer"
    assert tool["version"] == ["0.2.0"]
    assert tool["otherID"] == [{"type": "doi", "value": "10.1234/example"}]
    assert tool["toolType"] == ["Command-line tool"]
    assert tool["topic"] == [{"term": "Data analysis", "uri": "http://edamontology.org/topic_3474"}]
    assert tool["operatingSystem"] == ["Mac", "Linux"]
    assert tool["language"] == ["Python"]
    assert tool["license"] == "MIT"
    assert tool["maturity"] == "Mature"
    assert tool["cost"] == "Free of charge (with restrictions)"
    assert tool["accessibility"] == "Restricted access"
    assert tool["function"][0]["operation"] == [
        {
            "term": "Sequence analysis",
            "uri": "http://edamontology.org/operation_2403",
        }
    ]
    assert tool["function"][0]["input"][0]["format"] == [
        {"term": "FASTA", "uri": "http://edamontology.org/format_1929"}
    ]
    assert tool["link"][0] == {
        "url": "https://github.com/example/analyzer",
        "type": ["Repository"],
    }
    assert tool["publication"] == [
        {"doi": "10.1234/example", "type": ["Primary"], "version": "0.2.0"}
    ]
    assert tool["credit"] == [
        {"name": "Ada Lovelace", "typeEntity": "Person", "typeRole": ["Developer"]}
    ]

    custom_license = json.loads(
        render_text(
            BiotoolsModel(
                project_slug="example",
                licensing={"license": "Institutional research license\nTerms follow."},
            )
        )
    )
    assert custom_license[0]["license"] == "Other"


def test_contributing_maps_selected_tools_to_commands() -> None:
    """Contributing guidance keeps command normalization out of the template."""
    rendered = render_text(
        ContributingModel(
            code_review_policy="At least **two reviewers** must approve each change.",
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
    assert "## Code review" in rendered
    assert "At least **two reviewers** must approve each change." in rendered
    assert "poetry add <package>" in rendered
    assert "`poetry run ruff format --check .`" in rendered
    assert "| Metadata | metadata is included | Validate generated metadata files. |" in rendered
    assert "- .zenodo.json" in rendered
    assert "\n\n\n" not in rendered


def test_contributing_maps_r_tooling_commands() -> None:
    """R managers and quality tools should render native contributor commands."""
    rendered = render_text(
        ContributingModel(
            project_manager="rix",
            quality_tools={"formatter": "styler", "linter": "lintr"},
            test_types={"entries": ["Unit tests"]},
            test_frameworks={"entries": ["testthat"]},
            documentation_builder="pkgdown",
            documentation_types={"entries": ["developer"]},
        )
    )
    assert "Rscript environment.R" in rendered
    assert "nix-shell" in rendered
    assert 'styler::style_pkg(dry = "fail")' in rendered
    assert "lintr::lint_package()" in rendered
    assert "testthat::test_local()" in rendered
    assert "pkgdown::build_site()" not in rendered


def test_contributing_omits_unknown_tool_commands() -> None:
    """Selected tools without a safe generic command do not produce guesses."""
    rendered = render_text(
        ContributingModel(
            project_manager="rix",
            quality_tools={"formatter": "clang-format", "linter": "clang-tidy"},
            test_frameworks={"entries": ["GoogleTest"]},
        )
    )
    assert "## Development setup" in rendered
    assert "## Local checks" not in rendered
    assert "## Continuous integration" in rendered


def test_contributing_supports_zensical() -> None:
    """Builder selection affects CI guidance without owning builder commands."""
    rendered = render_text(
        ContributingModel(project_manager="uv", documentation_builder="zensical")
    )
    assert "zensical build" not in rendered
    assert "| Documentation | documentation is included | Build the documentation. |" in rendered


def test_pull_request_template_lists_selected_checklist_items() -> None:
    """Optional checklist items only appear when the matching capability is selected."""
    rendered = render_text(
        PullRequestTemplateModel(
            code_review_policy="At least one approval is required.",
            include_metadata=True,
            documentation_types={"entries": ["user"]},
            test_types={"entries": ["Unit tests"]},
        )
    )
    assert "Metadata files are updated" in rendered
    assert "code-review policy in `CONTRIBUTING.md`" in rendered
    assert "Documentation is updated" in rendered
    assert "Tests cover new behavior" in rendered

    minimal = render_text(PullRequestTemplateModel())
    assert "Metadata files are updated" not in minimal
    assert "Documentation is updated" not in minimal
    assert "Tests cover new behavior" not in minimal
    assert "code-review policy in `CONTRIBUTING.md`" not in minimal


def test_issue_template_bundles_config_and_forms_into_one_archive() -> None:
    """The issue templates render as one zip with all three GitHub files."""
    entries = IssueTemplateModel(
        urls={"documentation": "https://example.org/docs"},
        support_routes={
            "entries": [
                {"system": "Slack", "url": "https://example.org/slack"},
                {"system": "Docs mirror", "url": "https://example.org/docs"},
            ]
        },
    ).archive_entries()

    assert set(entries) == {"config.yml", "bug_report.yml", "feature_request.yml"}

    config = yaml.safe_load(entries["config.yml"])
    assert config["contact_links"] == [
        {
            "name": "Documentation",
            "url": "https://example.org/docs",
            "about": "Check the project documentation before opening an issue.",
        },
        {
            "name": "Slack",
            "url": "https://example.org/slack",
            "about": "Use this route for project support.",
        },
    ]

    bug_report = yaml.safe_load(entries["bug_report.yml"])
    assert bug_report["title"] == "fix: "
    assert bug_report["labels"] == ["bug", "triage"]

    feature_request = yaml.safe_load(entries["feature_request.yml"])
    assert feature_request["title"] == "feat: "
    assert feature_request["labels"] == ["enhancement", "triage"]


def test_issue_template_config_omits_contact_links_when_empty() -> None:
    """No contact links section is emitted without a documentation URL or route."""
    config = yaml.safe_load(IssueTemplateModel().archive_entries()["config.yml"])
    assert config == {"blank_issues_enabled": False}


def test_issue_template_writes_a_single_zip_file(tmp_path) -> None:
    """Rendering the model to disk produces one downloadable archive."""
    path = IssueTemplateModel().render(tmp_path)
    assert path == tmp_path / ".github" / "ISSUE_TEMPLATE.zip"
    with zipfile.ZipFile(path) as archive:
        assert sorted(archive.namelist()) == [
            "bug_report.yml",
            "config.yml",
            "feature_request.yml",
        ]
        yaml.safe_load(archive.read("config.yml"))
        yaml.safe_load(archive.read("bug_report.yml"))
        yaml.safe_load(archive.read("feature_request.yml"))


def test_all_models_render_without_template_expressions(tmp_path, author: Person) -> None:
    """Every shipped model renders its packaged template cleanly."""
    models = [
        BiotoolsModel(
            project_name="Example", project_slug="example", contributors={"entries": [author]}
        ),
        CitationModel(
            project_name="Example", project_slug="example", contributors={"entries": [author]}
        ),
        CodeMetaModel(
            project_name="Example", project_slug="example", contributors={"entries": [author]}
        ),
        ZenodoModel(
            project_name="Example", project_slug="example", contributors={"entries": [author]}
        ),
        ChangelogModel(),
        CodeOfConductModel(contributors={"entries": [author]}),
        ContributingModel(),
        DocumentationOverviewModel(project_slug="example"),
        DocumentationUserModel(project_slug="example"),
        DocumentationDeploymentModel(),
        DocumentationDeveloperModel(),
        DocumentationReferenceModel(),
        DocumentationLegalModel(),
        GovernanceModel(contributors={"entries": [author]}),
        LicenseModel(licensing={"license": "Custom project terms\nAll rights reserved."}),
        SecurityModel(contributors={"entries": [author]}),
        SupportModel(),
        PullRequestTemplateModel(),
        ReadmeModel(project_name="Example", project_slug="example"),
        IssueTemplateModel(),
    ]
    results = render_many(models, tmp_path)
    assert len(results) == len(models)
    for result in results:
        if result.path.suffix == ".zip":
            with zipfile.ZipFile(result.path) as archive:
                for name in archive.namelist():
                    text = archive.read(name).decode("utf-8")
                    assert "{{" not in text
                    assert "{%" not in text
            continue
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
