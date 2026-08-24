"""Metadata-only legal documentation model."""

from .base import rsm_template_base

_DocumentationLegalRSM = rsm_template_base(
    "_DocumentationLegalRSM",
    "project_name",
    "licensing",
    "access",
    "regulatory_requirements",
)


class DocumentationLegalModel(_DocumentationLegalRSM):
    """Input model for licensing, access, and regulatory information."""

    template_name = "documentation_legal.md.j2"
    output_name = "legal.md"
