"""Metadata-only model and renderer for ``README.md``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..commands import (
    FORMATTER_COMMANDS,
    LINTER_COMMANDS,
    PROJECT_MANAGER_PROFILES,
    TEST_COMMANDS,
    TYPE_CHECKER_COMMANDS,
)
from .base import rsm_template_base

_ReadmeRSM = rsm_template_base(
    "_ReadmeRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "versioning",
    "motivation",
    "topics",
    "audiences",
    "related_software",
    "urls",
    "persistent_identifiers",
    "publications",
    "licensing",
    "access",
    "include_metadata",
    "support_routes",
    "contacts",
    "operating_systems",
    "software_functions",
    "interfaces",
    "community_files",
    "project_manager",
    "programming_languages",
    "distribution_channels",
    "documentation_types",
    "quality_tools",
    "test_frameworks",
    "test_types",
    "resource_requirements",
    "maintenance_level",
    "continuity_plan",
    "retirement_criteria",
    "public_risk_notes",
    "security_measures",
    "data_management",
)

DOCUMENTATION_LABELS = {
    "user": "User guide: installation, configuration, usage, and examples",
    "deployment": "Deployment notes: environment setup and operational assumptions",
    "developer": "Developer guide: development, tests, contribution, and reference",
}


def _publication_url(publication: Any) -> str:
    """Resolve the best public URL for one associated publication."""
    if publication.doi:
        doi = str(publication.doi)
        return doi if doi.startswith(("http://", "https://")) else f"https://doi.org/{doi}"
    if publication.url:
        return str(publication.url)
    if publication.pmcid:
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{publication.pmcid}/"
    if publication.pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{publication.pmid}/"
    return ""


def _publication_label(publication: Any) -> str:
    """Return one compact human-readable publication label."""
    return str(
        publication.title
        or publication.citation
        or (f"DOI {publication.doi}" if publication.doi else "")
        or (f"PMID {publication.pmid}" if publication.pmid else "")
        or publication.pmcid
        or publication.url
        or "Associated publication"
    )


def _primary_publication(publications: list[Any]) -> Any | None:
    """Select the preferred or first populated publication."""
    populated = [
        publication
        for publication in publications
        if any(
            (
                publication.title,
                publication.citation,
                publication.doi,
                publication.url,
                publication.pmid,
                publication.pmcid,
            )
        )
    ]
    return next((item for item in populated if item.preferred), populated[0] if populated else None)


def _related_software_label(software: Any) -> str:
    """Format one related-software record."""
    name = str(software.name or "")
    url = str(software.url_or_doi or "")
    relationship = str(software.relationship or "")
    label = f"[{name}]({url})" if name and url else name or url or "Related software"
    return f"{label} - {relationship}" if relationship else label


def _term_lines(key: str, records: list[dict[str, Any]]) -> list[str]:
    """Render a bio.tools term collection as YAML lines."""
    lines = [f"{key}:"] if records else []
    for record in records:
        values = [(name, record.get(name)) for name in ("term", "uri") if record.get(name)]
        if not values:
            continue
        first_name, first_value = values[0]
        lines.append(f"- {first_name}: {json.dumps(first_value)}")
        lines.extend(f"  {name}: {json.dumps(value)}" for name, value in values[1:])
    return lines


def _io_lines(key: str, records: list[dict[str, Any]]) -> list[str]:
    """Render bio.tools input or output metadata as YAML lines."""
    lines = [f"{key}:"] if records else []
    for record in records:
        data = record.get("data") or {}
        lines.append("- data:")
        for name in ("term", "uri"):
            if data.get(name):
                lines.append(f"    {name}: {json.dumps(data[name])}")
        formats = record.get("format") or []
        if formats:
            lines.append("  format:")
            for item in formats:
                values = [(name, item.get(name)) for name in ("term", "uri") if item.get(name)]
                for value_index, (name, value) in enumerate(values):
                    prefix = "  - " if value_index == 0 else "    "
                    lines.append(f"{prefix}{name}: {json.dumps(value)}")
    return lines


def _function_blocks(entries: list[dict[str, Any]]) -> str:
    """Render README function metadata directly from RSM software functions."""
    blocks = []
    for entry in entries:
        yaml_lines = ["# biotools-function"]
        yaml_lines.extend(_term_lines("operation", entry.get("operations") or []))
        yaml_lines.extend(_io_lines("input", entry.get("inputs") or []))
        yaml_lines.extend(_io_lines("output", entry.get("outputs") or []))
        if command := entry.get("cmd"):
            yaml_lines.append(f"cmd: {json.dumps(command)}")
        if note := entry.get("note"):
            yaml_lines.append(f"note: {json.dumps(note)}")
        if len(yaml_lines) == 1:
            continue
        operations = [
            item.get("term", "") for item in entry.get("operations") or [] if item.get("term")
        ]
        label = ", ".join(operations) or "Software function"
        block = "\n".join(yaml_lines)
        blocks.append(
            f"<details>\n<summary>{label}</summary>\n\n```yaml\n{block}\n```\n\n</details>"
        )
    return "## Functions\n\n" + "\n\n".join(blocks) if blocks else ""


class ReadmeModel(_ReadmeRSM):
    """Published RSM fields used by the reusable project README."""

    template_name = "README.md.j2"
    output_name = "README.md"

    def _first_doi(self) -> str:
        """Return the first normalized software DOI."""
        for identifier in self.persistent_identifiers.entries:
            if str(identifier.type).lower() != "doi":
                continue
            value = str(identifier.identifier)
            for prefix in (
                "https://doi.org/",
                "http://doi.org/",
                "http://dx.doi.org/",
                "doi:",
            ):
                if value.lower().startswith(prefix):
                    return value[len(prefix) :]
            return value
        return ""

    def _installation(self) -> tuple[str, str, str]:
        """Return installation prose, command, and fence language from RSM."""
        slug = str(self.project_slug or "project")
        channels = {str(value).strip().lower() for value in self.distribution_channels.entries}
        languages = {
            str(language.name).strip().lower()
            for language in self.programming_languages.entries
            if language.name
        }
        if "pypi" in channels:
            return (
                "Install the published package from PyPI:",
                f"python -m pip install {slug.replace('_', '-')}",
                "bash",
            )
        if "cran" in channels:
            return "Install the published package from CRAN:", f'install.packages("{slug}")', "r"
        if "bioconductor" in channels:
            return (
                "Install the published package with BiocManager:",
                f'BiocManager::install("{slug}")',
                "r",
            )
        if "r" in languages or str(self.project_manager) in {"renv", "rix"}:
            return "Install from a source checkout:", "R CMD INSTALL .", "bash"
        if "python" in languages or str(self.project_manager) in {
            "hatch",
            "pdm",
            "pip",
            "pixi",
            "poetry",
            "uv",
        }:
            return "Install from a source checkout:", "python -m pip install .", "bash"
        if self.urls.repository:
            return (
                "Clone the source repository:",
                f"git clone {self.urls.repository}\ncd {slug}",
                "bash",
            )
        return "", "", "bash"

    def _usage_command(self) -> tuple[str, str]:
        """Return a declared command or a language-derived fallback."""
        declared = next(
            (str(function.cmd) for function in self.software_functions.entries if function.cmd),
            "",
        )
        slug = str(self.project_slug or "project")
        languages = {
            str(language.name).strip().lower()
            for language in self.programming_languages.entries
            if language.name
        }
        if "r" in languages or str(self.project_manager) in {"renv", "rix"}:
            command = f"library({slug})"
            if declared:
                command += f"\n{declared}"
            return command, "r"
        if declared:
            return declared, "bash"
        if "python" in languages:
            return f"python -m {slug}", "bash"
        return "", "bash"

    def _development(self) -> dict[str, Any]:
        """Resolve setup and checks entirely from RSM selections."""
        profile = PROJECT_MANAGER_PROFILES.get(str(self.project_manager), {})
        run_prefix = str(profile.get("run_prefix", ""))
        test_command = next(
            (
                TEST_COMMANDS[str(framework)]
                for framework in self.test_frameworks.entries
                if str(framework) in TEST_COMMANDS
            ),
            "",
        )
        if not test_command and self.test_types.entries:
            if str(self.project_manager) in {"renv", "rix"}:
                test_command = TEST_COMMANDS["testthat"]
            else:
                test_command = TEST_COMMANDS["pytest"]
        candidates = (
            FORMATTER_COMMANDS.get(str(self.quality_tools.formatter), ""),
            LINTER_COMMANDS.get(str(self.quality_tools.linter), ""),
            TYPE_CHECKER_COMMANDS.get(str(self.quality_tools.type_checker), ""),
            test_command,
        )
        return {
            "setup": str(profile.get("setup", "")),
            "checks": [f"{run_prefix}{command}" for command in candidates if command],
        }

    def _platform_lines(self) -> list[str]:
        """Return detailed supported-platform labels."""
        lines = []
        for system in self.operating_systems.entries:
            if not system.name:
                continue
            label = str(system.name)
            if system.specification:
                label += f" {system.specification}"
            if system.status:
                label += f" - {system.status}"
            lines.append(label)
        return lines

    def template_data(self) -> dict[str, Any]:
        """Prepare a complete README from RSM values only."""
        project = self.model_dump(mode="json", exclude_none=False)
        publication = _primary_publication(list(self.publications.entries))
        installation_text, installation_command, installation_language = self._installation()
        usage_command, usage_language = self._usage_command()
        return {
            "project": project,
            "title": self.project_name or self.project_slug or "Project",
            "purpose_categories": (
                [str(value) for value in self.motivation.categories.entries]
                if self.motivation.categories
                else []
            ),
            "related_software": [
                _related_software_label(item) for item in self.related_software.entries
            ],
            "preferred_publication": (
                {"label": _publication_label(publication), "url": _publication_url(publication)}
                if publication is not None
                else None
            ),
            "publication_note": (
                f"Publication: [{_publication_label(publication)}]({_publication_url(publication)})"
                if publication is not None and _publication_url(publication)
                else f"Publication: {_publication_label(publication)}"
                if publication is not None
                else ""
            ),
            "doi": self._first_doi(),
            "platforms": self._platform_lines(),
            "installation_text": installation_text,
            "installation_command": installation_command,
            "installation_language": installation_language,
            "usage_command": usage_command,
            "usage_language": usage_language,
            "documentation": [
                DOCUMENTATION_LABELS.get(str(value).strip().lower(), str(value))
                for value in self.documentation_types.entries
            ],
            "functions_section": _function_blocks(project["software_functions"]["entries"]),
            "development": self._development(),
            "citation_file": "CITATION.cff" if self.include_metadata else "",
            "support_file": (
                "SUPPORT.md"
                if "SUPPORT.md" in {str(value) for value in self.community_files.entries}
                else ""
            ),
            "license_file": (
                "LICENSE.md"
                if "r"
                in {
                    str(language.name).strip().lower()
                    for language in self.programming_languages.entries
                    if language.name
                }
                and str(self.licensing.license) == "MIT"
                else "LICENSE"
            ),
        }


def render_readme_text(model: ReadmeModel) -> str:
    """Render a README whose only inputs are validated RSM fields."""
    from ..renderer import render_template

    return render_template(model.template_name, model.template_data())


def render_readme(model: ReadmeModel, output_dir: str | Path) -> Path:
    """Write a metadata-only README and return its path."""
    target = Path(output_dir) / model.output_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_readme_text(model), encoding="utf-8")
    return target
