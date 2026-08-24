"""Model and command normalization for ``CONTRIBUTING.md``."""

from __future__ import annotations

from typing import Any

from ..commands import (
    FORMATTER_COMMANDS,
    LINTER_COMMANDS,
    PROJECT_MANAGER_PROFILES,
    TEST_COMMANDS,
    TYPE_CHECKER_COMMANDS,
)
from .base import rsm_template_base

_ContributingRSM = rsm_template_base(
    "_ContributingRSM",
    "community_files",
    "code_review_policy",
    "documentation_builder",
    "documentation_types",
    "include_metadata",
    "licensing",
    "project_manager",
    "quality_tools",
    "test_frameworks",
    "test_types",
    "distribution_channels",
)


class ContributingModel(_ContributingRSM):
    """Input model for ``CONTRIBUTING.md``."""

    template_name = "CONTRIBUTING.md.j2"
    output_name = "CONTRIBUTING.md"

    def _manager_commands(self) -> tuple[list[str], str, str | None]:
        """Return setup, dependency, and command-runner values for one manager."""
        profile = PROJECT_MANAGER_PROFILES.get(str(self.project_manager), {})
        run_prefix = str(profile.get("run_prefix", ""))
        runner = f"{run_prefix}{{command}}" if run_prefix else None
        return (
            list(profile.get("setup_commands", ())),
            str(profile.get("add", "")),
            runner,
        )

    @staticmethod
    def _check(name: str, command: str | None, runner: str | None) -> dict[str, str] | None:
        """Build one local-check record without guessing unknown commands."""
        if not command:
            return None
        return {"name": name, "command": runner.format(command=command) if runner else command}

    def _local_checks(self, runner: str | None) -> list[dict[str, str]]:
        """Return checks in the order contributors should normally run them."""
        selected = (
            ("Format", FORMATTER_COMMANDS.get(str(self.quality_tools.formatter))),
            ("Lint", LINTER_COMMANDS.get(str(self.quality_tools.linter))),
            ("Type check", TYPE_CHECKER_COMMANDS.get(str(self.quality_tools.type_checker))),
            ("Tests", self._test_command()),
        )
        return [
            record for name, command in selected if (record := self._check(name, command, runner))
        ]

    def _test_command(self) -> str | None:
        """Return the first recognized test-framework command in RSM order."""
        return next(
            (
                TEST_COMMANDS[str(framework)]
                for framework in self.test_frameworks.entries
                if str(framework) in TEST_COMMANDS
            ),
            None,
        )

    def _ci_stages(
        self,
        *,
        has_metadata: bool,
        has_documentation: bool,
        has_tests: bool,
        has_distribution: bool,
    ) -> list[dict[str, str]]:
        """Describe capability-driven CI stages in stable presentation order."""
        stages: list[dict[str, str]] = []
        if has_metadata:
            stages.append(
                {
                    "name": "Metadata",
                    "condition": "metadata is included",
                    "behavior": "Validate generated metadata files.",
                }
            )
        if has_documentation:
            stages.append(
                {
                    "name": "Documentation",
                    "condition": "documentation is included",
                    "behavior": "Build the documentation.",
                }
            )
        if any(
            (
                self.quality_tools.formatter,
                self.quality_tools.linter,
                self.quality_tools.type_checker,
            )
        ):
            stages.append(
                {
                    "name": "Quality",
                    "condition": "quality tools are selected",
                    "behavior": "Run applicable formatting, linting, and type checks.",
                }
            )
        if has_tests:
            stages.append(
                {
                    "name": "Tests",
                    "condition": "test types or frameworks are selected",
                    "behavior": "Run the selected test suite.",
                }
            )
        if has_distribution:
            stages.append(
                {
                    "name": "Distribution",
                    "condition": "distribution channels are selected",
                    "behavior": "Build and check release artifacts.",
                }
            )
        return stages

    def _release_files(self, *, has_metadata: bool, has_changelog: bool) -> list[str]:
        """List project files that are relevant when preparing a release."""
        files: list[str] = []
        if has_metadata:
            files.extend(["CITATION.cff", "codemeta.json"])
        if self.licensing.license:
            files.append("LICENSE")
        if has_changelog:
            files.append("CHANGELOG.md")
        if "Zenodo" in {str(channel) for channel in self.distribution_channels.entries}:
            files.append(".zenodo.json")
        files.append("Package artifacts for the selected distribution channels")
        return files

    def template_data(self) -> dict[str, Any]:
        """Prepare concise contributor guidance from selected RSM capabilities."""
        development_setup, dependency_command, runner = self._manager_commands()
        has_metadata = self.include_metadata
        has_documentation = bool(self.documentation_builder or self.documentation_types.entries)
        has_tests = bool(self.test_types.entries or self.test_frameworks.entries)
        has_changelog = "CHANGELOG.md" in {str(file) for file in self.community_files.entries}
        has_distribution = bool(self.distribution_channels.entries)
        return {
            "code_review_policy": self.code_review_policy,
            "development_setup": development_setup,
            "dependency_command": dependency_command,
            "local_checks": self._local_checks(runner),
            "ci_stages": self._ci_stages(
                has_metadata=has_metadata,
                has_documentation=has_documentation,
                has_tests=has_tests,
                has_distribution=has_distribution,
            ),
            "has_metadata": has_metadata,
            "has_documentation": has_documentation,
            "has_tests": has_tests,
            "has_changelog": has_changelog,
            "has_distribution": has_distribution,
            "release_files": self._release_files(
                has_metadata=has_metadata,
                has_changelog=has_changelog,
            )
            if has_distribution
            else [],
        }
