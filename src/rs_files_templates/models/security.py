"""Model for ``SECURITY.md``."""

from .base import rsm_template_base

_SecurityRSM = rsm_template_base(
    "_SecurityRSM",
    "contacts",
    "maintainers",
    "security_measures",
    "data_management",
    "public_risk_notes",
    "regulatory_requirements",
)


class SecurityModel(_SecurityRSM):
    """Input model for ``SECURITY.md``."""

    template_name = "SECURITY.md.j2"
    output_name = "SECURITY.md"
