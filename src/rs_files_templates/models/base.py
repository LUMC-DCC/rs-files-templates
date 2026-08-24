"""Base classes for file-template input models."""

from __future__ import annotations

import json
from abc import ABC
from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, create_model
from rsm_schema import RSMMetadata


class FileTemplateModel(BaseModel, ABC):
    """Base class for data consumed by one generated file.

    Models are deliberately small: each concrete model selects only the
    published RSM fields needed by its generated file.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    template_name: ClassVar[str]
    output_name: ClassVar[str]
    schema_url: ClassVar[str | None] = None
    media_type: ClassVar[str] = "text"

    @classmethod
    def from_json(cls, value: str | bytes | bytearray) -> Self:
        """Build a model from JSON text.

        Parameters
        ----------
        value
            JSON document containing model fields.

        Returns
        -------
        FileTemplateModel
            Validated concrete model instance.
        """
        return cls.model_validate_json(value)

    @classmethod
    def from_json_file(cls, path: str | Path) -> Self:
        """Build a model from a UTF-8 JSON file."""
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def to_json_file(self, path: str | Path, *, indent: int = 2) -> None:
        """Write this model to a JSON file."""
        payload = self.model_dump(mode="json", exclude_none=True)
        Path(path).write_text(json.dumps(payload, indent=indent) + "\n", encoding="utf-8")

    def template_data(self) -> dict[str, Any]:
        """Return JSON-compatible data for Jinja rendering."""
        # Preserve optional keys as ``None`` so readable templates can use
        # straightforward conditionals under Jinja's ``StrictUndefined``.
        return self.model_dump(mode="json", exclude_none=False)

    def render(
        self,
        output_dir: str | Path,
        *,
        validate_schema: bool = False,
    ) -> Path:
        """Render this model to its default output file.

        Parameters
        ----------
        output_dir
            Directory receiving the generated file.
        validate_schema
            Validate schema-backed output after rendering.

        Returns
        -------
        pathlib.Path
            Generated file path.
        """
        from rs_files_templates.renderer import render_file

        return render_file(self, output_dir, validate_schema=validate_schema).path


def rsm_template_base(name: str, *field_names: str) -> type[FileTemplateModel]:
    """Create a file-model base from selected published RSM fields.

    Copying the source ``FieldInfo`` values preserves the schema package's
    annotations, defaults, constraints, aliases, and nested generated models.
    """
    unknown = set(field_names) - set(RSMMetadata.model_fields)
    if unknown:
        raise ValueError(f"Unknown RSM fields for {name}: {', '.join(sorted(unknown))}")
    definitions = {
        field_name: (
            deepcopy(RSMMetadata.model_fields[field_name].annotation),
            deepcopy(RSMMetadata.model_fields[field_name]),
        )
        for field_name in field_names
    }
    return create_model(name, __base__=FileTemplateModel, **definitions)
