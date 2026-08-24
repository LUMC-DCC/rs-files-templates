"""Compatibility tests against the external project-context contract."""

from __future__ import annotations

import pytest

from rs_files_templates import (
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    ContributingModel,
    GovernanceModel,
    LicenseModel,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    validate_contract_compatibility,
)


@pytest.mark.network
@pytest.mark.parametrize(
    "model",
    [
        CitationModel(project_name="Example", project_slug="example"),
        CodeMetaModel(project_name="Example", project_slug="example"),
        ChangelogModel(),
        CodeOfConductModel(),
        ContributingModel(),
        GovernanceModel(),
        LicenseModel(),
        SecurityModel(),
        SupportModel(),
        ZenodoModel(project_name="Example", project_slug="example"),
    ],
)
def test_model_is_compatible_with_external_contract(model: object) -> None:
    """Overlapping model fields remain accepted by the external contract."""
    validate_contract_compatibility(model)  # type: ignore[arg-type]
