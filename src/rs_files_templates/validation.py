"""Validation helpers for generated structured files."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import yaml
from jsonschema.validators import validator_for
from referencing import Registry, Resource


@lru_cache(maxsize=32)
def load_schema(url: str, timeout: float = 15.0) -> dict[str, Any]:
    """Fetch and cache a JSON Schema from a trusted schema URL."""
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read())


def _retrieve_resource(uri: str) -> Resource[Any]:
    """Retrieve a schema referenced by another schema."""
    return Resource.from_contents(load_schema(uri))


def parse_rendered(path: str | Path, media_type: str) -> Any:
    """Parse a rendered file according to its declared media type."""
    text = Path(path).read_text(encoding="utf-8")
    if media_type == "json":
        return json.loads(text)
    if media_type == "yaml":
        return yaml.safe_load(text)
    return text


def validate_rendered(path: str | Path, schema_url: str, media_type: str) -> None:
    """Validate a JSON or YAML file against a JSON Schema."""
    schema = load_schema(schema_url)
    instance = parse_rendered(path, media_type)
    validator_cls = validator_for(schema)
    validator_cls.check_schema(schema)
    registry = Registry(retrieve=_retrieve_resource).with_resource(
        schema_url,
        Resource.from_contents(schema),
    )
    validator_cls(schema, registry=registry).validate(instance)
