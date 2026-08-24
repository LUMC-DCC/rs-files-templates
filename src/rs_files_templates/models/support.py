"""Model for ``SUPPORT.md``."""

from .base import rsm_template_base

_SupportRSM = rsm_template_base(
    "_SupportRSM",
    "urls",
    "contacts",
    "support_routes",
    "maintenance_level",
)


class SupportModel(_SupportRSM):
    """Input model for ``SUPPORT.md``."""

    template_name = "SUPPORT.md.j2"
    output_name = "SUPPORT.md"
