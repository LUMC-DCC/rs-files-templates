"""Model for ``SECURITY.md``."""

from typing import Any

from .base import rsm_template_base
from .utils import MAINTAINER_ROLES, contributors_with_roles

_SecurityRSM = rsm_template_base(
    "_SecurityRSM",
    "contacts",
    "contributors",
    "security_measures",
    "data_management",
    "public_risk_notes",
    "regulatory_requirements",
)


class SecurityModel(_SecurityRSM):
    """Input model for ``SECURITY.md``."""

    template_name = "SECURITY.md.j2"
    output_name = "SECURITY.md"

    def template_data(self) -> dict[str, Any]:
        """Expose whether a contributor has the maintainer role."""
        data = super().template_data()
        data["has_maintainers"] = bool(
            contributors_with_roles(self.contributors.entries, MAINTAINER_ROLES)
        )
        return data
