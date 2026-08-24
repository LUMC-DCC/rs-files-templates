# Upstream contract compatibility

The package depends on the published `rsm-schema` Python package.
File models remain small and independently usable by selecting only their fields from
`RSMMetadata` with `rsm_template_base()`.

`validate_contract_compatibility()` checks a model against a projected subset of the published RSM
JSON Schema.

```python
from rs_files_templates import CitationModel, validate_contract_compatibility

model = CitationModel(project_name="Example", project_slug="example")
validate_contract_compatibility(model)
```

The canonical schema URL is exposed as `RSM_SCHEMA_URL`.
