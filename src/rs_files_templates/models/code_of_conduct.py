"""Model for ``CODE_OF_CONDUCT.md``."""

from .base import rsm_template_base

_CodeOfConductRSM = rsm_template_base(
    "_CodeOfConductRSM",
    "contacts",
    "maintainers",
)


class CodeOfConductModel(_CodeOfConductRSM):
    """Input model for ``CODE_OF_CONDUCT.md``."""

    template_name = "CODE_OF_CONDUCT.md.j2"
    output_name = "CODE_OF_CONDUCT.md"
