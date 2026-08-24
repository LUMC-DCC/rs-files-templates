"""Model for the bundled ``.github/ISSUE_TEMPLATE`` files.

GitHub reads issue forms from several files at once (a routing ``config.yml``
plus one file per form), so this model renders all of them together into one
downloadable ``.zip`` archive instead of owning a single Jinja template.
"""

from __future__ import annotations

from typing import Any

from .base import rsm_template_base

_IssueTemplateRSM = rsm_template_base(
    "_IssueTemplateRSM",
    "urls",
    "support_routes",
)


class IssueTemplateModel(_IssueTemplateRSM):
    """Input model for the bundled ``.github/ISSUE_TEMPLATE`` archive."""

    template_name = "issue_template_config.yml.j2"
    output_name = ".github/ISSUE_TEMPLATE.zip"
    media_type = "zip"

    def _config_data(self) -> dict[str, Any]:
        """Deduplicate support routes that already point at the documentation URL."""
        documentation_url = self.urls.documentation
        routes = [
            {"system": route.system, "url": route.url}
            for route in self.support_routes.entries
            if route.url and route.url != documentation_url
        ]
        return {"documentation_url": documentation_url, "routes": routes}

    def archive_entries(self) -> dict[str, str]:
        """Render the routing config and the static issue forms for the archive."""
        from ..renderer import render_template

        return {
            "config.yml": render_template("issue_template_config.yml.j2", self._config_data()),
            "bug_report.yml": render_template("issue_template_bug_report.yml.j2", {}),
            "feature_request.yml": render_template("issue_template_feature_request.yml.j2", {}),
        }
