"""Regression tests for human-readable project documentation and metadata."""

import json
import re

import pytest

from rs_files_templates import (
    CitationModel,
    CodeMetaModel,
    DocumentationUserModel,
    ReadmeModel,
    ZenodoModel,
    render_text,
)


@pytest.mark.parametrize("model_type", [ReadmeModel, DocumentationUserModel])
@pytest.mark.parametrize(
    ("manager", "source", "published", "prefix"),
    [
        ("uv", "uv sync", "uv pip install example", "uv run "),
        ("poetry", "poetry install", "poetry add example", "poetry run "),
        ("pdm", "pdm install", "pdm add example", "pdm run "),
        ("hatch", "hatch env create", "hatch run python -m pip install example", "hatch run "),
        ("pixi", "pixi install", "pixi add --pypi example", "pixi run "),
        ("pip", "pip install", "python -m pip install example", ""),
    ],
)
def test_installation_and_usage_follow_manager(model_type, manager, source, published, prefix):
    """Both public entry points use the same selected environment manager."""
    model = model_type(
        project_slug="example",
        project_manager=manager,
        programming_languages={"entries": [{"name": "Python"}]},
        software_functions={"entries": [{"cmd": "example --help"}]},
    )
    assert source in render_text(model)
    assert prefix + "example --help" in render_text(model)
    model = model_type.model_validate(
        model.model_dump()
        | {
            "distribution_channels": {"entries": ["PyPI"]},
        }
    )
    assert published in render_text(model)


def test_readme_lists_topics_separately_and_finishes_with_citation_and_license():
    """Inline conditionals must not swallow Markdown list separators."""
    rendered = render_text(
        ReadmeModel(
            project_name="Example",
            project_slug="example",
            project_manager="poetry",
            topics={
                "entries": [
                    {"term": "Genomics", "uri": "https://edamontology.org/topic_0622"},
                    {"term": "Data analysis"},
                    {"uri": "https://edamontology.org/topic_3071"},
                ]
            },
            support_routes={
                "entries": [
                    {"system": "Issues", "url": "https://example.org/issues"},
                    {"system": "Help", "url": "https://example.org/help"},
                ]
            },
            urls={"documentation": "https://example.org/docs"},
            licensing={"license": "MIT"},
        )
    )
    assert ")\n- Data analysis\n- https://edamontology.org/topic_3071" in rendered
    assert ")\n- [Help]" in rendered
    assert "## Documentation\n\nRead the [project documentation]" in rendered
    assert re.findall(r"^## (.+)$", rendered, re.MULTILINE)[-2:] == [
        "Citation",
        "Legal and Licensing",
    ]


@pytest.mark.parametrize("model_type", [ReadmeModel, DocumentationUserModel])
def test_missing_information_is_omitted(model_type):
    """An empty field must not produce an apologetic placeholder section."""
    rendered = render_text(model_type(project_slug="example"))
    for heading in ("Installation", "Usage", "Run the software", "Support", "Intended Audience"):
        assert f"## {heading}" not in rendered
    assert "not yet" not in rendered
    assert "not available" not in rendered


@pytest.mark.parametrize("model_type", [CodeMetaModel, CitationModel, ZenodoModel])
def test_metadata_keywords_include_unique_edam_labels(model_type):
    """Topic URIs stay structured; their labels also improve keyword discovery."""
    model = model_type(
        project_slug="example",
        keywords={"entries": ["genomics", "research software"]},
        topics={
            "entries": [
                {"term": "Genomics", "uri": "https://edamontology.org/topic_0622"},
                {"term": "Data analysis"},
                {"uri": "https://edamontology.org/topic_3071"},
            ]
        },
    )
    assert model.template_data()["keywords"] == ["genomics", "research software", "Data analysis"]


def test_codemeta_keeps_language_requirements_readable_and_not_in_runtime_platform():
    """Language declarations do not imply a platform, especially for compiled code."""
    rendered = render_text(
        CodeMetaModel(
            project_slug="example",
            programming_languages={
                "entries": [
                    {"name": "Python", "version_constraint": ">=3.12"},
                    {"name": "C++"},
                ]
            },
        )
    )
    parsed = json.loads(rendered)
    assert parsed["programmingLanguage"][0]["version"] == ">=3.12"
    assert "runtimePlatform" not in parsed
    assert "\\u003e" not in rendered
