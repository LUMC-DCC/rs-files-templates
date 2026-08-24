"""Rendering engine for file-template models."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .models import FileTemplateModel
from .validation import validate_rendered


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    """Result of rendering one file model.

    Parameters
    ----------
    model
        Concrete model class name used for rendering.
    path
        Generated file path.
    validated
        Whether an output schema was checked successfully.
    """

    model: str
    path: Path
    validated: bool


def _environment() -> Environment:
    """Create the package Jinja environment."""
    template_dir = files("rs_files_templates.templates")
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_text(model: FileTemplateModel) -> str:
    """Render one model without writing it to disk.

    Parameters
    ----------
    model
        Validated file-template model.

    Returns
    -------
    str
        Rendered content.
    """
    template = _environment().get_template(model.template_name)
    return template.render(model=model.template_data())


def render_file(
    model: FileTemplateModel,
    output_dir: str | Path,
    *,
    validate_schema: bool = False,
) -> GeneratedFile:
    """Render one model to its default output path.

    Parameters
    ----------
    model
        Validated file-template model.
    output_dir
        Directory receiving the generated file.
    validate_schema
        Validate the rendered file when the model declares a schema.

    Returns
    -------
    GeneratedFile
        Generation result.
    """
    root = Path(output_dir)
    target = root / model.output_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_text(model), encoding="utf-8")

    validated = False
    if validate_schema and model.schema_url:
        validate_rendered(target, model.schema_url, model.media_type)
        validated = True

    return GeneratedFile(type(model).__name__, target, validated)


def render_many(
    models: Iterable[FileTemplateModel],
    output_dir: str | Path,
    *,
    validate_schemas: bool = False,
) -> list[GeneratedFile]:
    """Render several independent file models into one directory."""
    return [render_file(model, output_dir, validate_schema=validate_schemas) for model in models]
