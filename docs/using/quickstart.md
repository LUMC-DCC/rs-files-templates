# Quickstart

Install the package in the application that needs to generate files:

```bash
pip install rs-files-templates
```

Create and render a model:

```python
from rs_files_templates import CitationModel, Person

model = CitationModel(
    project_name="Example project",
    project_slug="example-project",
    versioning={"version": "1.2.0"},
    urls={"repository": "https://github.com/example/project"},
    authors={
        "entries": [
            Person(name="Ada Lovelace", given_names="Ada", family_names="Lovelace"),
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
