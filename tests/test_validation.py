"""Tests for generated-output schema validation."""

from __future__ import annotations

from rs_files_templates import validation


def test_duplicate_published_enum_values_do_not_change_validation(
    tmp_path,
    monkeypatch,
) -> None:
    """Repeated enum entries are removed before meta-schema checking."""
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "string",
        "enum": ["accepted", "accepted"],
    }
    monkeypatch.setattr(validation, "load_schema", lambda _url: schema)
    output = tmp_path / "value.json"
    output.write_text('"accepted"\n', encoding="utf-8")

    validation.validate_rendered(output, "https://example.org/schema.json", "json")
