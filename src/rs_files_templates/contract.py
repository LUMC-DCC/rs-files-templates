"""Development-time compatibility checks against the upstream context contract.

The external contract is intentionally not a runtime model for this package.
Concrete file models remain small and independent. These helpers only verify
that overlapping field names and values are still compatible with the upstream
JSON Schema when maintainers choose to run the check.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from jsonschema import Draft202012Validator

from .models import FileTemplateModel
from .validation import load_schema

RSM_SCHEMA_URL = "https://lumc-dcc.github.io/rsm-schema/schema/1.0.0/rsm.schema.json"


def projected_contract_schema(
    model_type: type[FileTemplateModel],
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a partial upstream schema containing fields used by one model.

    Parameters
    ----------
    model_type
        Concrete file model class.
    schema
        Full upstream JSON Schema.

    Returns
    -------
    dict[str, Any]
        JSON Schema containing only overlapping top-level fields plus ``$defs``.

    Raises
    ------
    ValueError
        If the model contains a field that is absent from the upstream contract.
    """
    properties = schema.get("properties", {})
    missing = sorted(set(model_type.model_fields) - set(properties))
    if missing:
        raise ValueError(
            f"{model_type.__name__} fields are not present in the upstream contract: "
            + ", ".join(missing)
        )

    return {
        "$schema": schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$defs": schema.get("$defs", {}),
        "type": "object",
        "additionalProperties": False,
        "properties": {name: properties[name] for name in model_type.model_fields},
    }


def contract_payload(
    model: FileTemplateModel,
) -> dict[str, Any]:
    """Serialize a file model in the published RSM contract shape."""
    return model.model_dump(mode="json", exclude_none=True)


def validate_contract_compatibility(
    model: FileTemplateModel,
    *,
    schema: Mapping[str, Any] | None = None,
    schema_url: str = RSM_SCHEMA_URL,
) -> None:
    """Validate one model's overlapping data against the upstream contract.

    This is intended for tests and maintenance checks. Supplying ``schema`` keeps
    the operation offline; otherwise ``schema_url`` is fetched.
    """
    resolved = dict(schema) if schema is not None else load_schema(schema_url)
    projected = projected_contract_schema(type(model), resolved)
    Draft202012Validator(projected).validate(contract_payload(model))
