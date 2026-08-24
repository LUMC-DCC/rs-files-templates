"""Canonical commands shared by generated repository files and documentation."""

from __future__ import annotations

from typing import Any

PROJECT_MANAGER_PROFILES: dict[str, dict[str, Any]] = {
    "renv": {
        "setup": (
            'Rscript -e \'if (!requireNamespace("renv", quietly = TRUE)) '
            'install.packages("renv"); if (file.exists("renv.lock")) '
            "renv::restore() else renv::init()'"
        ),
        "setup_commands": ("R -e 'renv::restore()'",),
        "setup_group": "Rscript -e 'renv::install()'",
        "add": "Rscript -e 'renv::install(\"<package>\")'",
        "run_prefix": "",
        "lock": "Rscript -e 'renv::snapshot()'",
        "lockfile": "renv.lock",
        "setup_creates_lock": True,
    },
    "rix": {
        "setup": "Rscript environment.R && nix-shell",
        "setup_commands": ("Rscript environment.R", "nix-shell"),
        "setup_group": "Rscript environment.R && nix-shell",
        "add": "Add the package to environment.R, then run Rscript environment.R.",
        "run_prefix": "",
        "lock": "Rscript environment.R",
        "lockfile": "default.nix",
        "setup_creates_lock": True,
    },
    "uv": {
        "setup": "uv sync --all-extras",
        "setup_commands": ("uv sync",),
        "setup_group": "uv sync --extra {group}",
        "add": "uv add <package>",
        "run_prefix": "uv run ",
        "lock": "uv lock",
        "lockfile": "uv.lock",
        "setup_creates_lock": True,
    },
    "poetry": {
        "setup": "poetry install --all-extras",
        "setup_commands": ("poetry install",),
        "setup_group": 'poetry install --extras "{group}"',
        "add": "poetry add <package>",
        "run_prefix": "poetry run ",
        "lock": "poetry lock",
        "lockfile": "poetry.lock",
        "setup_creates_lock": True,
    },
    "pdm": {
        "setup": "pdm install -G :all",
        "setup_commands": ("pdm install",),
        "setup_group": "pdm install -G {group}",
        "add": "pdm add <package>",
        "run_prefix": "pdm run ",
        "lock": "pdm lock",
        "lockfile": "pdm.lock",
        "setup_creates_lock": True,
    },
    "hatch": {
        "setup": "hatch env create",
        "setup_commands": ("hatch env create",),
        "setup_group": "hatch env create",
        "add": "Add the dependency to pyproject.toml, then run hatch env prune.",
        "run_prefix": "hatch run ",
        "lock": "hatch env lock default",
        "lockfile": "pylock.toml",
        "setup_creates_lock": True,
    },
    "pixi": {
        "setup": "pixi install",
        "setup_commands": ("pixi install",),
        "setup_group": "pixi install",
        "add": "pixi add --pypi <package>",
        "run_prefix": "pixi run ",
        "lock": "pixi lock",
        "lockfile": "pixi.lock",
        "setup_creates_lock": True,
    },
    "pip": {
        "setup": 'python -m pip install -e ".[all]"',
        "setup_commands": (
            "python -m venv .venv",
            ".venv/bin/python -m pip install -e .",
        ),
        "setup_group": 'python -m pip install -e ".[{group}]"',
        "add": "python -m pip install <package>",
        "run_prefix": "",
        "lock": "python -m pip lock -o pylock.toml -e .",
        "lockfile": "pylock.toml",
        "setup_creates_lock": False,
    },
    "cargo": {
        "setup": "cargo build",
        "setup_commands": ("cargo build",),
        "add": "cargo add <crate>",
        "run_prefix": "",
    },
    "npm": {
        "setup": "npm install",
        "setup_commands": ("npm install",),
        "add": "npm install <package>",
        "run_prefix": "npm run ",
    },
    "pnpm": {
        "setup": "pnpm install",
        "setup_commands": ("pnpm install",),
        "add": "pnpm add <package>",
        "run_prefix": "pnpm ",
    },
    "yarn": {
        "setup": "yarn install",
        "setup_commands": ("yarn install",),
        "add": "yarn add <package>",
        "run_prefix": "yarn ",
    },
    "maven": {
        "setup": "mvn verify",
        "setup_commands": ("mvn verify",),
        "add": "",
        "run_prefix": "",
    },
    "gradle": {
        "setup": "./gradlew build",
        "setup_commands": ("./gradlew build",),
        "add": "",
        "run_prefix": "",
    },
    "cmake": {
        "setup": "cmake -S . -B build",
        "setup_commands": ("cmake -S . -B build",),
        "add": "",
        "run_prefix": "",
    },
}

FORMATTER_COMMANDS = {
    "ruff": "ruff format --check .",
    "black": "black --check .",
    "styler": "Rscript -e 'styler::style_pkg(dry = \"fail\")'",
    "prettier": "prettier --check .",
    "rustfmt": "cargo fmt --check",
}

LINTER_COMMANDS = {
    "ruff": "ruff check .",
    "flake8": "flake8",
    "pylint": "pylint src",
    "lintr": (
        "Rscript -e 'lints <- lintr::lint_package(); print(lints); "
        "quit(status = length(lints) > 0L)'"
    ),
    "eslint": "eslint .",
    "clippy": "cargo clippy -- -D warnings",
}

TYPE_CHECKER_COMMANDS = {
    "mypy": "mypy src",
    "pyright": "pyright",
    "basedpyright": "basedpyright",
    "pyre": "pyre check",
    "tsc": "tsc --noEmit",
    "rustc": "cargo check",
    "Flow": "flow check",
}

TEST_COMMANDS = {
    "pytest": "python -m pytest",
    "unittest": "python -m unittest",
    "testthat": "Rscript -e 'testthat::test_local()'",
    "cargo test": "cargo test",
    "Vitest": "vitest run",
    "Jest": "jest",
    "bats-core": "bats test",
}


def project_manager_profile(name: str) -> dict[str, Any]:
    """Return a copy of one canonical project-manager command profile."""
    return dict(PROJECT_MANAGER_PROFILES.get(str(name), {}))
