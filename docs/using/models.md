# Models

Every output has an independent model. A caller supplies only the data needed by that file.

The current models are:

- `CitationModel`
- `CodeMetaModel`
- `ZenodoModel`
- `LicenseModel`
- `ChangelogModel`
- `CodeOfConductModel`
- `ContributingModel`
- `GovernanceModel`
- `SecurityModel`
- `SupportModel`


Shared values such as `Person`, `Organization`, `Funding`, `Registry`, and `Interface` come directly
from `rsm_schema`. Each file model selects its required top-level fields from `RSMMetadata`.

All models inherit from `FileTemplateModel`, which provides JSON loading/writing and `render()` method:

```python
from rs_files_templates import SecurityModel

model = SecurityModel.from_json_file("security-input.json")
model.render("output")
```

## License text

`LicenseModel.render()` creates `LICENSE`. A value such as `MIT` is resolved through SPDX and the
authoritative full license text is written. Multiline custom text is written directly; a
single-line value that SPDX does not recognize is also preserved as custom text.
