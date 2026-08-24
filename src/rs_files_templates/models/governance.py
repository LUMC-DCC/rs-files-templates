"""Model for ``GOVERNANCE.md``."""

from typing import Any

from rsm_schema.generated import Person

from .base import rsm_template_base
from .utils import person_label

_GovernanceRSM = rsm_template_base(
    "_GovernanceRSM",
    "governance_notes",
    "maintainers",
    "principal_investigators",
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
        if person.affiliation:
            line += f", {person.affiliation.name}"
        return line

    def template_data(self) -> dict[str, Any]:
        """Prepare readable role lines for the governance template."""
        return {
            "governance_notes": self.governance_notes,
            "maintainer_lines": [self._role_line(person) for person in self.maintainers.entries],
            "principal_investigator_lines": [
                self._role_line(person) for person in self.principal_investigators.entries
            ],
            "continuity_plan": self.continuity_plan,
            "retirement_criteria": self.retirement_criteria.entries,
        }
