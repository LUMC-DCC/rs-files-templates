"""Model and command normalization for ``CONTRIBUTING.md``."""

from __future__ import annotations

from typing import Any

from .base import rsm_template_base

_ContributingRSM = rsm_template_base(
    "_ContributingRSM",
    "community_files",
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


_MANAGER_COMMANDS: dict[str, tuple[list[str], str, str | None]] = {
    "uv": (["uv sync"], "uv add <package>", "uv run {command}"),
    "poetry": (["poetry install"], "poetry add <package>", "poetry run {command}"),
    "pdm": (["pdm install"], "pdm add <package>", "pdm run {command}"),
    "hatch": (["hatch env create"], "", "hatch run {command}"),
    "pixi": (["pixi install"], "pixi add <package>", "pixi run {command}"),
    "pip": (
        ["python -m venv .venv", ".venv/bin/python -m pip install -e ."],
        ".venv/bin/python -m pip install <package>",
        None,
    ),
    "renv": (["R -e 'renv::restore()'"], "R -e 'renv::install(\"<package>\")'", None),
    "cargo": (["cargo build"], "cargo add <crate>", None),
    "npm": (["npm install"], "npm install <package>", None),
    "pnpm": (["pnpm install"], "pnpm add <package>", None),
    "yarn": (["yarn install"], "yarn add <package>", None),
    "maven": (["mvn verify"], "", None),
    "gradle": (["./gradlew build"], "", None),
    "cmake": (["cmake -S . -B build"], "", None),
}

_FORMATTER_COMMANDS = {
    "ruff": "ruff format --check .",
    "black": "black --check .",
    "prettier": "prettier --check .",
    "rustfmt": "cargo fmt --check",
}
_LINTER_COMMANDS = {
    "ruff": "ruff check .",
    "flake8": "flake8",
    "pylint": "pylint src",
    "lintr": "Rscript -e 'lintr::lint_package()'",
    "eslint": "eslint .",
    "clippy": "cargo clippy -- -D warnings",
}
_TYPE_CHECKER_COMMANDS = {
    "mypy": "mypy .",
    "pyright": "pyright",
    "basedpyright": "basedpyright",
    "pyre": "pyre check",
    "tsc": "tsc --noEmit",
    "rustc": "cargo check",
    "Flow": "flow check",
}
_TEST_COMMANDS = {
    "pytest": "pytest",
    "unittest": "python -m unittest",
    "testthat": "Rscript -e 'testthat::test_local()'",
    "cargo test": "cargo test",
    "Vitest": "vitest run",
    "Jest": "jest",
    "bats-core": "bats test",
}
_DOCUMENTATION_COMMANDS = {
    "mkdocs": "mkdocs build --strict",
    "sphinx": "sphinx-build -W -b html docs docs/_build/html",
    "pkgdown": "Rscript -e 'pkgdown::build_site()'",
}


class ContributingModel(_ContributingRSM):
    """Input model for ``CONTRIBUTING.md``."""

    template_name = "CONTRIBUTING.md.j2"
    output_name = "CONTRIBUTING.md"

    def _manager_commands(self) -> tuple[list[str], str, str | None]:
        """Return setup, dependency, and command-runner values for one manager."""
        return _MANAGER_COMMANDS.get(str(self.project_manager), ([], "", None))

    @staticmethod
    def _check(name: str, command: str | None, runner: str | None) -> dict[str, str] | None:
        """Build one local-check record without guessing unknown commands."""
        if not command:
            return None
        return {"name": name, "command": runner.format(command=command) if runner else command}

    def _local_checks(self, runner: str | None) -> list[dict[str, str]]:
        """Return checks in the order contributors should normally run them."""
        selected = (
            ("Format", _FORMATTER_COMMANDS.get(str(self.quality_tools.formatter))),
            ("Lint", _LINTER_COMMANDS.get(str(self.quality_tools.linter))),
            ("Type check", _TYPE_CHECKER_COMMANDS.get(str(self.quality_tools.type_checker))),
            ("Tests", self._test_command()),
            ("Documentation", _DOCUMENTATION_COMMANDS.get(str(self.documentation_builder))),
        )
        return [
            record for name, command in selected if (record := self._check(name, command, runner))
        ]

    def _test_command(self) -> str | None:
        """Return the first recognized test-framework command in RSM order."""
        return next(
            (
                _TEST_COMMANDS[str(framework)]
                for framework in self.test_frameworks.entries
                if str(framework) in _TEST_COMMANDS
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
