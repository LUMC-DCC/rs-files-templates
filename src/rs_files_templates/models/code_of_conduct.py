"""Model for ``CODE_OF_CONDUCT.md``."""

from typing import Any

from .base import rsm_template_base
from .utils import MAINTAINER_ROLES, contributors_with_roles

_CodeOfConductRSM = rsm_template_base(
    "_CodeOfConductRSM",
    "contacts",
    "contributors",
)


class CodeOfConductModel(_CodeOfConductRSM):
    """Input model for ``CODE_OF_CONDUCT.md``."""

    template_name = "CODE_OF_CONDUCT.md.j2"
    output_name = "CODE_OF_CONDUCT.md"

    def template_data(self) -> dict[str, Any]:
        """Expose whether a contributor has the maintainer role."""
        data = super().template_data()
        data["has_maintainers"] = bool(
            contributors_with_roles(self.contributors.entries, MAINTAINER_ROLES)
        )
        return data
