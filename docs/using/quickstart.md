# Quickstart

Install the package in the application that needs to generate files:

```bash
pip install rs-files-templates
```

Create and render a model:

```python
from rs_files_templates import CitationModel, Contributor

model = CitationModel(
    project_name="Example project",
    project_slug="example-project",
    versioning={"version": "1.2.0"},
    urls={"repository": "https://github.com/example/project"},
    contributors={
        "entries": [
            Contributor(
                name="Ada Lovelace",
                given_names="Ada",
                family_names="Lovelace",
                roles=["Original author"],
            ),
        ]
    },
)

path = model.render("generated")
```

Multiple unrelated files can be rendered together:

```python
from rs_files_templates import LicenseModel, SecurityModel, SupportModel, render_many

render_many(
    [
        LicenseModel(licensing={"license": "MIT"}),
        SecurityModel(contacts={"security": "security@example.org"}),
        SupportModel(urls={"documentation": "https://example.org/docs"}),
    ],
    "generated",
)
```

Generate bio.tools registry metadata from the same RSM fields:

```python
from rs_files_templates import BiotoolsModel

BiotoolsModel(
    project_name="Example",
    project_slug="example",
    project_short_description="Analyze biological research data.",
    urls={"homepage": "https://example.org"},
    topics={"entries": [{"term": "Data analysis"}]},
    software_functions={"entries": [{"operations": [{"term": "Statistical calculation"}]}]},
).render("generated", validate_schema=True)
```

README content is resolved from rsm-schema metadata in the model itself:

```python
from rs_files_templates import ReadmeModel, render_readme

render_readme(
    ReadmeModel(
        project_name="Example",
        project_slug="example",
        project_manager="uv",
        software_functions={"entries": [{"cmd": "example --help"}]},
    ),
    "generated",
)
```

Documentation pages are independent Markdown models. Select and render the
ones your application needs:

```python
from rs_files_templates import (
    DocumentationOverviewModel,
    DocumentationUserModel,
    render_many,
)

render_many(
    [
        DocumentationOverviewModel(project_name="Example", project_slug="example"),
        DocumentationUserModel(project_name="Example", project_slug="example"),
    ],
    "docs",
)
```

The consuming repository generator selects and configures a documentation builder.
