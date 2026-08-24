"""Tests for reusable command profiles."""

from rs_files_templates import (
    FORMATTER_COMMANDS,
    PROJECT_MANAGER_PROFILES,
)


def test_project_manager_commands_have_one_canonical_profile() -> None:
    """README, docs, and contributor callers can share manager commands."""
    assert PROJECT_MANAGER_PROFILES["uv"]["setup"] == "uv sync --all-extras"
    assert PROJECT_MANAGER_PROFILES["uv"]["run_prefix"] == "uv run "
    assert PROJECT_MANAGER_PROFILES["renv"]["lockfile"] == "renv.lock"
    assert FORMATTER_COMMANDS["ruff"] == "ruff format --check ."
