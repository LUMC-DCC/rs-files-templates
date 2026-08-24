"""Model for ``CHANGELOG.md``."""

from .base import rsm_template_base

_ChangelogRSM = rsm_template_base(
    "_ChangelogRSM",
    "versioning",
    "urls",
    "distribution_channels",
)


class ChangelogModel(_ChangelogRSM):
    """Input model for ``CHANGELOG.md``."""

    template_name = "CHANGELOG.md.j2"
    output_name = "CHANGELOG.md"
