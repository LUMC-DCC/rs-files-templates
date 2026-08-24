"""Compatibility tests against the external project-context contract."""

from __future__ import annotations

import pytest

from rs_files_templates import (
    BiotoolsModel,
    ChangelogModel,
    CitationModel,
    CodeMetaModel,
    CodeOfConductModel,
    ContributingModel,
    DocumentationDeploymentModel,
    DocumentationDeveloperModel,
    DocumentationLegalModel,
    DocumentationOverviewModel,
    DocumentationReferenceModel,
    DocumentationUserModel,
    GovernanceModel,
    IssueTemplateModel,
    LicenseModel,
    PullRequestTemplateModel,
    ReadmeModel,
    SecurityModel,
    SupportModel,
    ZenodoModel,
    validate_contract_compatibility,
)


@pytest.mark.network
@pytest.mark.parametrize(
    "model",
    [
        BiotoolsModel(project_name="Example", project_slug="example"),
        CitationModel(project_name="Example", project_slug="example"),
        CodeMetaModel(project_name="Example", project_slug="example"),
        ChangelogModel(),
        CodeOfConductModel(),
        ContributingModel(),
        DocumentationOverviewModel(project_slug="example"),
        DocumentationUserModel(project_slug="example"),
        DocumentationDeploymentModel(),
        DocumentationDeveloperModel(),
        DocumentationReferenceModel(),
        DocumentationLegalModel(),
        GovernanceModel(),
        LicenseModel(),
        SecurityModel(),
        SupportModel(),
        ZenodoModel(project_name="Example", project_slug="example"),
        PullRequestTemplateModel(),
        IssueTemplateModel(),
        ReadmeModel(project_name="Example", project_slug="example"),
    ],
)
def test_model_is_compatible_with_external_contract(model: object) -> None:
    """Overlapping model fields remain accepted by the external contract."""
    validate_contract_compatibility(model)  # type: ignore[arg-type]
