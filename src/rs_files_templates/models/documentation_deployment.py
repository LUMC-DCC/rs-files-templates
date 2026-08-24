"""Metadata-only deployment documentation model."""

from .base import rsm_template_base

_DocumentationDeploymentRSM = rsm_template_base(
    "_DocumentationDeploymentRSM",
    "project_name",
    "containerization",
    "operating_systems",
    "external_dependencies",
    "external_services",
    "resource_requirements",
)


class DocumentationDeploymentModel(_DocumentationDeploymentRSM):
    """Input model for deployment and operational requirements."""

    template_name = "documentation_deployment.md.j2"
    output_name = "deployment.md"
