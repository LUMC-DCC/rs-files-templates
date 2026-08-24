# Validation

Pydantic validates generator inputs. Structured generated outputs can additionally be validated
against their published JSON Schemas.

```python
citation.render("output", validate_schema=True)
```

Currently configured output schemas:

- CFF 1.2.0: `https://citation-file-format.github.io/1.2.0/schema.json`
- LUMC CodeMeta 1.0.0: `https://lumc-dcc.github.io/rs-metadata/schema/1.0.0/codemeta-lumc.schema.json`

Output-schema validation performs network access and follows external schema references when
required. Normal rendering does not perform network access.
