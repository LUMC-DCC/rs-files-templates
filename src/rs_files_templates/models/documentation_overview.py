"""Metadata-only project overview documentation model."""

from .base import rsm_template_base

_DocumentationOverviewRSM = rsm_template_base(
    "_DocumentationOverviewRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "motivation",
    "topics",
    "audiences",
    "related_software",
    "urls",
    "access",
    "funding",
)


class DocumentationOverviewModel(_DocumentationOverviewRSM):
    """Input model for the project overview page."""

    template_name = "documentation_overview.md.j2"
    output_name = "overview.md"
