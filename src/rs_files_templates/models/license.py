"""Model for generating a full-text ``LICENSE`` file."""

from __future__ import annotations

from typing import Any

from rs_files_templates.external.spdx import resolve_license_text

from .base import rsm_template_base

_LicenseRSM = rsm_template_base("_LicenseRSM", "licensing")


class LicenseModel(_LicenseRSM):
    """Published RSM licensing fields needed to render ``LICENSE``."""

    template_name = "LICENSE.j2"
    output_name = "LICENSE"

    def template_data(self) -> dict[str, Any]:
        return {"license_text": resolve_license_text(self.licensing.license)}
