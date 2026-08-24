"""Model for ``GOVERNANCE.md``."""

from typing import Any

from rsm_schema.generated import Person

from .base import rsm_template_base
from .utils import (
    MAINTAINER_ROLES,
    PRINCIPAL_INVESTIGATOR_ROLES,
    contributors_with_roles,
    person_label,
    primary_affiliation,
)

_GovernanceRSM = rsm_template_base(
    "_GovernanceRSM",
    "governance_notes",
    "contributors",
    "continuity_plan",
    "retirement_criteria",
)


class GovernanceModel(_GovernanceRSM):
    """Input model for ``GOVERNANCE.md``."""

    template_name = "GOVERNANCE.md.j2"
    output_name = "GOVERNANCE.md"

    @staticmethod
    def _role_line(person: Person) -> str:
        """Format one governance role line."""
        line = person_label(person)
        if person.email:
            line += f" <{person.email}>"
        if affiliation := primary_affiliation(person):
            line += f", {affiliation.name}"
        return line

    def template_data(self) -> dict[str, Any]:
        """Prepare readable role lines for the governance template."""
        return {
            "governance_notes": self.governance_notes,
            "maintainer_lines": [
                self._role_line(person)
                for person in contributors_with_roles(self.contributors.entries, MAINTAINER_ROLES)
            ],
            "principal_investigator_lines": [
                self._role_line(person)
                for person in contributors_with_roles(
                    self.contributors.entries, PRINCIPAL_INVESTIGATOR_ROLES
                )
            ],
            "continuity_plan": self.continuity_plan,
            "retirement_criteria": self.retirement_criteria.entries,
        }
