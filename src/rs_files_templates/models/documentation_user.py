"""Metadata-only user documentation model."""

from __future__ import annotations

from typing import Any

from .base import rsm_template_base

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
        slug = str(self.project_slug or "project")
        distribution_name = slug.replace("_", "-")
        channels = {str(entry).strip().lower() for entry in self.distribution_channels.entries}
        languages = _language_names(list(self.programming_languages.entries))
        if "pypi" in channels:
            return (
                "Install the published package from PyPI:",
                f"python -m pip install {distribution_name}",
                "bash",
            )
        if "cran" in channels:
            return (
                "Install the published package from CRAN:",
                f'install.packages("{slug}")',
                "r",
            )
        if "bioconductor" in channels:
            return (
                "Install the published package with BiocManager:",
                f'BiocManager::install("{slug}")',
                "r",
            )
        if "r" in languages or str(self.project_manager) in {"renv", "rix"}:
            return "Install the package from a source checkout:", "R CMD INSTALL .", "bash"
        if "python" in languages or str(self.project_manager) in {
            "hatch",
            "pdm",
            "pip",
            "pixi",
            "poetry",
            "uv",
        }:
            return (
                "Install the package from a source checkout:",
                "python -m pip install .",
                "bash",
            )
        repository = str(self.urls.repository or "")
        if repository:
            return "Clone the source repository:", f"git clone {repository}\ncd {slug}", "bash"
        return "", "", "bash"

    def _usage_command(self) -> str:
        """Return a declared command or a metadata-derived language fallback."""
        declared = next(
            (str(function.cmd) for function in self.software_functions.entries if function.cmd),
            "",
        )
        if declared:
            return declared
        slug = str(self.project_slug or "project")
        languages = _language_names(list(self.programming_languages.entries))
        if "r" in languages or str(self.project_manager) in {"renv", "rix"}:
            return f"library({slug})"
        if "python" in languages:
            return f"python -m {slug}"
        return ""

    def template_data(self) -> dict[str, Any]:
        """Add installation and usage commands derived from RSM metadata."""
        data = super().template_data()
        installation_text, installation_command, installation_language = self._installation()
        data.update(
            installation_text=installation_text,
            installation_command=installation_command,
            installation_language=installation_language,
            usage_command=self._usage_command(),
        )
        return data
