"""Model for ``.github/pull_request_template.md``."""

from __future__ import annotations

from typing import Any

from .base import rsm_template_base

_PullRequestTemplateRSM = rsm_template_base(
    "_PullRequestTemplateRSM",
    "code_review_policy",
    "include_metadata",
    "documentation_types",
    "test_types",
)


class PullRequestTemplateModel(_PullRequestTemplateRSM):
    """Input model for ``.github/pull_request_template.md``."""

    template_name = "pull_request_template.md.j2"
    output_name = ".github/pull_request_template.md"

    def template_data(self) -> dict[str, Any]:
        """Expose which optional checklist items apply to this project."""
        return {
            "has_code_review_policy": bool(self.code_review_policy),
            "has_metadata": self.include_metadata,
            "has_documentation": bool(self.documentation_types.entries),
            "has_tests": bool(self.test_types.entries),
        }
