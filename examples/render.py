"""Render a small set of example files."""

from pathlib import Path

from rs_files_templates import (
    CitationModel,
    CodeMetaModel,
    Contributor,
    LicenseModel,
    SecurityModel,
    render_many,
)

person = Contributor(
    name="Ada Lovelace",
    given_names="Ada",
    family_names="Lovelace",
    roles=["Original author", "Maintainer"],
)
common = {
    "project_name": "Example research software",
    "project_slug": "example-research-software",
    "versioning": {"version": "1.0.0"},
    "urls": {"repository": "https://github.com/example/research-software"},
    "contributors": {"entries": [person]},
}

models = [
    CitationModel(**common),
    CodeMetaModel(**common),
    LicenseModel(licensing={"license": "MIT"}),
    SecurityModel(contacts={"security": "security@example.org"}),
]

render_many(models, Path("generated"))
