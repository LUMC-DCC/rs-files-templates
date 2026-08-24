"""Metadata-only technical reference documentation model."""

from .base import rsm_template_base

_DocumentationReferenceRSM = rsm_template_base(
    "_DocumentationReferenceRSM",
    "project_name",
    "programming_languages",
    "software_functions",
    "interfaces",
)


class DocumentationReferenceModel(_DocumentationReferenceRSM):
    """Input model for public functions and interfaces."""

    template_name = "documentation_reference.md.j2"
    output_name = "reference.md"
