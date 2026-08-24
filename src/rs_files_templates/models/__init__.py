"""Public input models."""

from rsm_schema.generated import (
    Containerization,
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
from .changelog import ChangelogModel
from .citation import CitationModel
from .code_of_conduct import CodeOfConductModel
from .codemeta import CodeMetaModel
from .governance import GovernanceModel
from .license import LicenseModel
from .security import SecurityModel
from .support import SupportModel
from .zenodo import ZenodoModel

__all__ = [
    "ChangelogModel",
    "CitationModel",
    "CodeMetaModel",
    "CodeOfConductModel",
    "Containerization",
    "DataFormat",
    "EdamTerm",
    "ExternalDependency",
    "ExternalService",
    "FileTemplateModel",
    "FunctionIo",
    "Funding",
    "GovernanceModel",
    "Interface",
    "LicenseModel",
    "OperatingSystem",
    "Organization",
    "PersistentIdentifier",
    "Person",
    "ProgrammingLanguage",
    "Publication",
    "RSMMetadata",
    "Registry",
    "RelatedSoftware",
    "SecurityModel",
    "SoftwareFunction",
    "SupportModel",
    "SupportRoute",
    "ZenodoModel",
]
