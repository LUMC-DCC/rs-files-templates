# Models

Every output has an independent model. A caller supplies only the published
rsm-schema metadata needed by that file.

The documentation models are ordinary Markdown file models:

- `DocumentationOverviewModel` writes `overview.md`.
- `DocumentationUserModel` writes `usage.md`.
- `DocumentationDeploymentModel` writes `deployment.md`.
- `DocumentationDeveloperModel` writes `developer.md`.
- `DocumentationReferenceModel` writes `reference.md`.
- `DocumentationLegalModel` writes `legal.md`.

The models do not select or configure a documentation builder. Callers choose the
pages they need and provide any builder configuration.

```python
from rs_files_templates import (
    DocumentationOverviewModel,
    DocumentationUserModel,
    render_many,
)

render_many(
    [
        DocumentationOverviewModel(
            project_name="Example",
            project_slug="example",
            project_short_description="Reusable research software.",
        ),
        DocumentationUserModel(
            project_name="Example",
            project_slug="example",
            project_manager="uv",
            programming_languages={"entries": [{"name": "Python"}]},
        ),
    ],
    "docs",
)
```

`ReadmeModel` produces a complete metadata-only README. Installation,
usage, citation, support, licensing, and development guidance are resolved from
its rsm-schema fields. Repository generators can post-process the Markdown to add
repository-specific content, such as a badge for a generated workflow. Top-level EDAM `topics`
appear as project research domains. `CodeMetaModel` maps them to
`applicationSubCategory`, while `BiotoolsModel` maps them to bio.tools EDAM
topics and combines them with function-level EDAM operations, inputs, and outputs.

```python
from rs_files_templates import ReadmeModel, render_readme

render_readme(
    ReadmeModel(
        project_name="Example",
        project_slug="example",
        project_manager="uv",
        topics={"entries": [{"term": "Data analysis"}]},
        software_functions={"entries": [{"cmd": "example --help"}]},
    ),
    "output",
)
```

The other models are `BiotoolsModel`, `CitationModel`, `CodeMetaModel`, `ZenodoModel`,
`LicenseModel`, `ChangelogModel`, `CodeOfConductModel`, `ContributingModel`,
`GovernanceModel`, `SecurityModel`, `SupportModel`, `PullRequestTemplateModel`,
and `IssueTemplateModel`.

All inherit from `FileTemplateModel`, which provides JSON loading, JSON writing,
and `render()`. Use `render_many()` for independent files rendered into one
directory.

## License text

`LicenseModel.render()` creates `LICENSE`. SPDX identifiers resolve to their license
text. Multiline custom terms and unrecognized single-line terms are used verbatim.

## Archive models

Most models render one template to one output file. `IssueTemplateModel` writes the
multi-file GitHub issue-template set to `.github/ISSUE_TEMPLATE.zip`.
