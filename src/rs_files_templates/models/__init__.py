"""Public input models."""

from rsm_schema.generated import (
    Containerization,
    Contributor,
    DataFormat,
    EdamTerm,
    ExternalDependency,
    ExternalService,
    FunctionIo,
    Funding,
    Interface,
    OperatingSystem,
    Organization,
    PersistentIdentifier,
    Person,
    ProgrammingLanguage,
    Publication,
    Registry,
    RelatedSoftware,
    RSMMetadata,
    SoftwareFunction,
    SupportRoute,
)

from .base import FileTemplateModel
from .biotools import BiotoolsModel
from .changelog import ChangelogModel
from .citation import CitationModel
from .code_of_conduct import CodeOfConductModel
from .codemeta import CodeMetaModel
from .contributing import ContributingModel
from .documentation_deployment import DocumentationDeploymentModel
from .documentation_developer import DocumentationDeveloperModel
from .documentation_legal import DocumentationLegalModel
from .documentation_overview import DocumentationOverviewModel
from .documentation_reference import DocumentationReferenceModel
from .documentation_user import DocumentationUserModel
from .governance import GovernanceModel
from .issue_template import IssueTemplateModel
from .license import LicenseModel
from .pull_request_template import PullRequestTemplateModel
from .readme import ReadmeModel
from .security import SecurityModel
from .support import SupportModel
from .zenodo import ZenodoModel

__all__ = [
    "BiotoolsModel",
    "ChangelogModel",
    "CitationModel",
    "CodeMetaModel",
    "CodeOfConductModel",
    "Containerization",
    "ContributingModel",
    "Contributor",
    "DataFormat",
    "DocumentationDeploymentModel",
    "DocumentationDeveloperModel",
    "DocumentationLegalModel",
    "DocumentationOverviewModel",
    "DocumentationReferenceModel",
    "DocumentationUserModel",
    "EdamTerm",
    "ExternalDependency",
    "ExternalService",
    "FileTemplateModel",
    "FunctionIo",
    "Funding",
    "GovernanceModel",
    "Interface",
    "IssueTemplateModel",
    "LicenseModel",
    "OperatingSystem",
    "Organization",
    "PersistentIdentifier",
    "Person",
    "ProgrammingLanguage",
    "Publication",
    "PullRequestTemplateModel",
    "RSMMetadata",
    "ReadmeModel",
    "Registry",
    "RelatedSoftware",
    "SecurityModel",
    "SoftwareFunction",
    "SupportModel",
    "SupportRoute",
    "ZenodoModel",
]
