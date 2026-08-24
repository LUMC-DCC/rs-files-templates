"""Metadata-only developer documentation model."""

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

_DocumentationDeveloperRSM = rsm_template_base(
    "_DocumentationDeveloperRSM",
    "project_name",
    "project_manager",
    "community_files",
    "code_review_policy",
    "include_metadata",
    "quality_tools",
    "test_frameworks",
    "test_types",
)


class DocumentationDeveloperModel(_DocumentationDeveloperRSM):
    """Input model for contributor-oriented development guidance."""

    template_name = "documentation_developer.md.j2"
    output_name = "developer.md"

    def template_data(self) -> dict[str, Any]:
        """Resolve manager and quality commands from selected RSM values."""
        data = super().template_data()
        profile = PROJECT_MANAGER_PROFILES.get(str(self.project_manager), {})
        run_prefix = str(profile.get("run_prefix", ""))
        candidates = (
            ("Format", FORMATTER_COMMANDS.get(str(self.quality_tools.formatter))),
            ("Lint", LINTER_COMMANDS.get(str(self.quality_tools.linter))),
            ("Type check", TYPE_CHECKER_COMMANDS.get(str(self.quality_tools.type_checker))),
            (
                "Tests",
                next(
                    (
                        TEST_COMMANDS[str(framework)]
                        for framework in self.test_frameworks.entries
                        if str(framework) in TEST_COMMANDS
                    ),
                    None,
                ),
            ),
        )
        checks = [
            {"name": name, "command": f"{run_prefix}{command}"}
            for name, command in candidates
            if command
        ]
        data.update(setup=str(profile.get("setup", "")), checks=checks)
        return data
