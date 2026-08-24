"""Render a small set of example files."""

from pathlib import Path

from rs_files_templates import (
    CitationModel,
    CodeMetaModel,
    LicenseModel,
    Person,
    SecurityModel,
    render_many,
)

person = Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace")
common = {
    "project_name": "Example research software",
    "project_slug": "example-research-software",
    "versioning": {"version": "1.0.0"},
    "urls": {"repository": "https://github.com/example/research-software"},
    "authors": {"entries": [person]},
}

models = [
    CitationModel(**common),
    CodeMetaModel(**common),
    LicenseModel(licensing={"license": "MIT"}),
    SecurityModel(contacts={"security": "security@example.org"}),
]

render_many(models, Path("generated"))
