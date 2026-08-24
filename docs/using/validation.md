# Validation

Pydantic validates generator inputs. Structured outputs can also be checked against
their published JSON Schemas.

```python
citation.render("output", validate_schema=True)
```

Supported output schemas:

- CFF 1.2.0: `https://citation-file-format.github.io/1.2.0/schema.json`
- LUMC CodeMeta 1.0.0: `https://lumc-dcc.github.io/rs-metadata/schema/1.0.0/codemeta-lumc.schema.json`
- bio.tools: `https://raw.githubusercontent.com/bio-tools/biotoolsSchema/refs/heads/main/jsonschema/biotoolsj.json`

The LUMC CodeMeta profile validates the access and funding mappings.

Output-schema validation uses the network when it must retrieve a schema or follow
an external reference. Rendering without schema validation is local.
