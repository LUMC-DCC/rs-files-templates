# Upstream contract compatibility

The package depends on the published `rsm-schema` Python package.
Each file model selects its fields from `RSMMetadata` with `rsm_template_base()`.

`validate_contract_compatibility()` checks a model against a projected subset of the published RSM
JSON Schema.

```python
from rs_files_templates import CitationModel, validate_contract_compatibility

model = CitationModel(project_name="Example", project_slug="example")
validate_contract_compatibility(model)
```

The canonical schema URL is exposed as `RSM_SCHEMA_URL`.

All template inputs must be declared rsm-schema fields. Repository state and
presentation settings belong in the calling application, which can post-process
rendered text when needed.

The six documentation models produce independent Markdown files. Repository
templaters select pages and add builder files and commands.
