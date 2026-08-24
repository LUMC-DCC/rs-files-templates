# rs-files-templates

This repository is a Python package for generating standardized project files from small,
typed Pydantic models. It keeps reusable Jinja templates, rendering logic, and validation in one
place so multiple projects can produce the same metadata and policy files consistently.

The documentation is available at [lumc-dcc.github.io/rs-files-templates](https://lumc-dcc.github.io/rs-files-templates/).

Included generators:

- `CITATION.cff`
- `codemeta.json`
- `.zenodo.json`
- `LICENSE`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `GOVERNANCE.md`
- `SECURITY.md`
- `SUPPORT.md`

## Quick start

```bash
pip install rs-files-templates
```

Python 3.14 is required.

## Example usage

```python
from rs_files_templates import CitationModel, Person

citation = CitationModel(
    project_name="Example project",
    project_slug="example-project",
    versioning={"version": "1.0.0"},
    urls={"repository": "https://github.com/example/project"},
    authors={"entries": [Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")]},
)

citation.render(".", validate_schema=True)
```

Each generated file has its own model derived from the fields in
[`rsm-schema`](https://lumc-dcc.github.io/rsm-schema) package, derived from schema version 1.0.0.

## Development

```bash
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

---

## License

This project is licensed under Apache 2.0. See the [LICENSE](LICENSE) file for details.
