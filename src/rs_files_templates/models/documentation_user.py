"""Metadata-only user documentation model."""

from __future__ import annotations

from typing import Any

from .base import rsm_template_base
from .readme import ReadmeModel

_DocumentationUserRSM = rsm_template_base(
    "_DocumentationUserRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_manager",
    "programming_languages",
    "distribution_channels",
    "software_functions",
    "interfaces",
    "urls",
)


def _language_names(entries: list[Any]) -> set[str]:
    """Return normalized programming-language names."""
    return {str(entry.name).strip().lower() for entry in entries if entry.name}


class DocumentationUserModel(_DocumentationUserRSM):
    """Input model for installation and usage guidance."""

    template_name = "documentation_user.md.j2"
    output_name = "usage.md"

    def _installation(self) -> tuple[str, str, str]:
        """Resolve installation prose and a command from RSM fields."""
        return ReadmeModel.model_validate(self.model_dump())._installation()

    def _usage_command(self) -> tuple[str, str]:
        """Return a declared command or a metadata-derived language fallback."""
        return ReadmeModel.model_validate(self.model_dump())._usage_command()

    def template_data(self) -> dict[str, Any]:
        """Add installation and usage commands derived from RSM metadata."""
        data = super().template_data()
        installation_text, installation_command, installation_language = self._installation()
        usage_command, usage_language = self._usage_command()
        data.update(
            installation_text=installation_text,
            installation_command=installation_command,
            installation_language=installation_language,
            usage_command=usage_command,
            usage_language=usage_language,
        )
        return data
