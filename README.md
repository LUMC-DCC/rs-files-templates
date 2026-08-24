# rs-files-templates

This Python package generates standard research-software project files from typed
Pydantic models and Jinja templates.

The documentation is available at [lumc-dcc.github.io/rs-files-templates](https://lumc-dcc.github.io/rs-files-templates/).

Included generators:

- `README.md`
- independent `overview.md`, `usage.md`, `deployment.md`, `developer.md`,
  `reference.md`, and `legal.md` documentation pages
- `CITATION.cff`
- `codemeta.json`
- `biotools.json`
- `.zenodo.json`
- `LICENSE`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `GOVERNANCE.md`
- `SECURITY.md`
- `SUPPORT.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE.zip` (config, bug report, and feature request, bundled as one download)

## Quick start

```bash
pip install rs-files-templates
```

Python 3.14 is required.

## Example usage

```python
from rs_files_templates import CitationModel, Contributor

citation = CitationModel(
    project_name="Example project",
    project_slug="example-project",
    versioning={"version": "1.0.0"},
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

citation.render(".", validate_schema=True)
```

README content uses the same RSM contract. Installation, usage, citation,
support, licensing, and development guidance are resolved from metadata in the
model itself:

```python
from rs_files_templates import ReadmeModel, render_readme

readme = ReadmeModel(
    project_name="Example project",
    project_slug="example-project",
    project_short_description="Analyze research data reproducibly.",
    audiences={"entries": ["Researcher"]},
    topics={"entries": [{"term": "Data analysis"}]},
    project_manager="uv",
    software_functions={"entries": [{"cmd": "example-project --help"}]},
)
render_readme(readme, ".")
```

Top-level EDAM `topics` are rendered as project research domains and mapped to
CodeMeta `applicationSubCategory`. `BiotoolsModel` maps the same topics and the
declared software functions to bio.tools registry metadata.

The package maps supported project managers, quality tools, and test frameworks
to metadata-derived commands. Each documentation model renders one Markdown file.
Repository generators supply documentation-builder configuration.

Each generated file has a model composed only of fields from
[`rsm-schema`](https://lumc-dcc.github.io/rsm-schema), version 1.0.0.

## Development

```bash
poetry install --with dev,docs
poetry run pre-commit install
poetry run pre-commit run --all-files
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

---

## License

This project is licensed under Apache 2.0. See the [LICENSE](LICENSE) file for details.
