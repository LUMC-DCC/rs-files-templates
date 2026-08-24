"""Model and normalization logic for ``biotools.json``."""

from __future__ import annotations

import re
from typing import Any

from rsm_schema.generated import Contributor

from .base import rsm_template_base
from .utils import normalize_orcid, person_name

BIOTOOLS_SCHEMA_URL = (
    "https://raw.githubusercontent.com/bio-tools/biotoolsSchema/"
    "refs/heads/main/jsonschema/biotoolsj.json"
)

_BiotoolsRSM = rsm_template_base(
    "_BiotoolsRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "development_status",
    "topics",
    "contributors",
    "funding",
    "urls",
    "registries",
    "persistent_identifiers",
    "publications",
    "licensing",
    "access",
    "support_routes",
    "programming_languages",
    "software_functions",
    "interfaces",
    "operating_systems",
    "versioning",
)

_MATURITY = {
    "concept": "Emerging",
    "wip": "Emerging",
    "active": "Mature",
    "inactive": "Legacy",
    "suspended": "Legacy",
    "abandoned": "Legacy",
    "unsupported": "Legacy",
    "moved": "Legacy",
}
_COST = {
    "free": "Free of charge",
    "free-with-restrictions": "Free of charge (with restrictions)",
    "commercial": "Commercial",
}
_OPERATING_SYSTEM = {
    "Linux": "Linux",
    "macOS": "Mac",
    "Windows": "Windows",
    "Android": "Android",
    "iOS": "iOS",
}
_LANGUAGES = frozenset(
    {
        "Bash",
        "C",
        "C#",
        "C++",
        "CWL",
        "Fortran",
        "Go",
        "Java",
        "JavaScript",
        "Julia",
        "Kotlin",
        "MATLAB",
        "Perl",
        "PHP",
        "Python",
        "R",
        "Ruby",
        "Rust",
        "Shell",
        "SQL",
        "Swift",
        "TypeScript",
    }
)
_PUBLICATION_TYPES = {
    "benchmarking study": "Benchmarking study",
    "method": "Method",
    "usage": "Usage",
    "review": "Review",
    "other": "Other",
}
_ROLE_MAP = {
    "Original author": "Developer",
    "Co-author": "Developer",
    "Maintainer": "Maintainer",
    "Principal investigator": "Provider",
    "Successor": "Contributor",
}


class BiotoolsModel(_BiotoolsRSM):
    """Published RSM fields needed to render ``biotools.json``."""

    template_name = "biotools.json.j2"
    output_name = "biotools.json"
    schema_url = BIOTOOLS_SCHEMA_URL
    media_type = "json"

    @staticmethod
    def _name(value: str, fallback: str) -> str:
        """Return a name accepted by the bio.tools character constraints."""
        cleaned = re.sub(r"[^ ()+\-./0-9:;A-Z_a-z]", "-", value.strip())
        cleaned = re.sub(r"-{2,}", "-", cleaned).strip("- ")
        fallback = re.sub(r"[^ ()+\-./0-9:;A-Z_a-z]", "-", fallback.strip())
        fallback = re.sub(r"-{2,}", "-", fallback).strip("- ")
        return (cleaned or fallback or "project")[:100]

    def _description(self) -> str:
        """Return a description within the schema's length bounds."""
        value = str(
            self.project_long_description
            or self.project_short_description
            or "Research software project."
        ).strip()
        if len(value) < 10:
            value = f"{value} software".strip()
        return value[:1000]

    @staticmethod
    def _edam(value: Any, namespace: str) -> dict[str, str] | None:
        """Map one RSM EDAM term to the URI form required by bio.tools."""
        result: dict[str, str] = {}
        if term := str(getattr(value, "term", None) or "").strip():
            result["term"] = term
        uri = str(getattr(value, "uri", None) or "").strip()
        match = re.fullmatch(rf"https?://edamontology\.org/{namespace}_([0-9]{{4}})", uri)
        if match:
            result["uri"] = f"http://edamontology.org/{namespace}_{match.group(1)}"
        return result or None

    def _biotools_id(self) -> str:
        """Read an existing bio.tools identifier from the registry metadata."""
        for registry in self.registries.entries:
            registry_name = re.sub(r"[^a-z]", "", registry.name.lower())
            if registry_name != "biotools" or not registry.url_or_id:
                continue
            value = str(registry.url_or_id).strip().rstrip("/")
            value = re.sub(r"^https?://bio\.tools/", "", value, flags=re.IGNORECASE)
            value = re.sub(r"^biotools:", "", value, flags=re.IGNORECASE)
            if re.fullmatch(r"[-.0-9A-Z_a-z]+", value):
                return value
        return ""

    def _other_ids(self) -> list[dict[str, str]]:
        """Map persistent identifiers supported by the bio.tools schema."""
        result: list[dict[str, str]] = []
        for identifier in self.persistent_identifiers.entries:
            identifier_type = str(identifier.type)
            value = str(identifier.identifier).strip()
            if identifier_type == "doi":
                value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
                if re.fullmatch(r"10\.[0-9]{4,9}/\S+", value, flags=re.IGNORECASE):
                    record = {"type": "doi", "value": value}
                    if identifier.associated_version:
                        record["version"] = str(identifier.associated_version)[:100]
                    result.append(record)
        return result

    def _topics(self) -> list[dict[str, str]]:
        """Map project-level EDAM topics."""
        return [topic for value in self.topics.entries if (topic := self._edam(value, "topic"))]

    def _license(self) -> str:
        """Return a bio.tools license identifier or its custom-license marker."""
        value = str(self.licensing.license or "").strip()
        if not value:
            return ""
        if "\n" in value or value.startswith(("http://", "https://")):
            return "Other"
        if " " in value and value not in {"Not licensed"}:
            return "Other"
        return value

    def _functions(self) -> list[dict[str, Any]]:
        """Map RSM software functions to bio.tools function records."""
        result: list[dict[str, Any]] = []
        for function in self.software_functions.entries:
            operations = [
                operation
                for value in function.operations or []
                if (operation := self._edam(value, "operation"))
            ]
            if not operations:
                continue
            record: dict[str, Any] = {"operation": operations}
            for source_name, target_name in (("inputs", "input"), ("outputs", "output")):
                entries: list[dict[str, Any]] = []
                for item in getattr(function, source_name) or []:
                    data = self._edam(item.data, "data") if item.data else None
                    if not data:
                        continue
                    entry: dict[str, Any] = {"data": data}
                    formats = [
                        data_format
                        for value in item.format or []
                        if (data_format := self._edam(value, "format"))
                    ]
                    if formats:
                        entry["format"] = formats
                    entries.append(entry)
                if entries:
                    record[target_name] = entries
            note = str(function.note or "").strip()
            if len(note) >= 10:
                record["note"] = note[:1000]
            if command := str(function.cmd or "").strip():
                record["cmd"] = command[:1000]
            result.append(record)
        return result

    @staticmethod
    def _credit(contributor: Contributor) -> dict[str, Any]:
        """Map one RSM contributor to a bio.tools credit."""
        record: dict[str, Any] = {
            "name": person_name(contributor)[:100],
            "typeEntity": "Person",
        }
        if contributor.email:
            record["email"] = contributor.email
        if contributor.url:
            record["url"] = contributor.url
        if contributor.orcid:
            record["orcidid"] = f"https://orcid.org/{normalize_orcid(contributor.orcid)}"
        roles = list(
            dict.fromkeys(
                _ROLE_MAP[str(role)] for role in contributor.roles if str(role) in _ROLE_MAP
            )
        )
        if roles:
            record["typeRole"] = roles
        return record

    def _credits(self) -> list[dict[str, Any]]:
        """Build contributor and funding-agency credits."""
        result = [self._credit(person) for person in self.contributors.entries]
        seen_funders: set[str] = set()
        for funding in self.funding.entries:
            name = str(funding.funder or "").strip()
            if not name or name.casefold() in seen_funders:
                continue
            record: dict[str, Any] = {
                "name": name[:100],
                "typeEntity": "Funding agency",
                "typeRole": ["Provider"],
            }
            identifier = str(funding.funder_identifier or "").strip()
            identifier_type = str(funding.funder_identifier_type or "")
            if identifier_type == "ror" and identifier:
                record["rorid"] = identifier.removeprefix("https://ror.org/")
            elif identifier_type == "crossref-funder-id" and identifier:
                record["fundrefid"] = identifier
            if funding.funder_url:
                record["url"] = funding.funder_url
            result.append(record)
            seen_funders.add(name.casefold())
        return result

    def _publications(self) -> list[dict[str, Any]]:
        """Map DOI, PMID, and PMCID publication identifiers."""
        result: list[dict[str, Any]] = []
        for publication in self.publications.entries:
            record: dict[str, Any] = {}
            if publication.doi:
                doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", publication.doi)
                if re.fullmatch(r"10\.[0-9]{4,9}/\S+", doi, flags=re.IGNORECASE):
                    record["doi"] = doi
            if publication.pmid:
                pmid = re.sub(r"^PMID:", "", publication.pmid, flags=re.IGNORECASE)
                if re.fullmatch(r"[1-9][0-9]{0,8}", pmid):
                    record["pmid"] = pmid
            if publication.pmcid:
                pmcid = publication.pmcid.upper()
                pmcid = pmcid if pmcid.startswith("PMC") else f"PMC{pmcid}"
                if re.fullmatch(r"PMC[1-9][0-9]{0,8}", pmcid):
                    record["pmcid"] = pmcid
            publication_type = _PUBLICATION_TYPES.get(str(publication.type or "").lower())
            types = ["Primary"] if publication.preferred else []
            if publication_type and publication_type not in types:
                types.append(publication_type)
            if types:
                record["type"] = types
            note = str(publication.note or publication.citation or "").strip()
            if len(note) >= 10:
                record["note"] = note[:1000]
            if self.versioning.version:
                record["version"] = str(self.versioning.version)[:100]
            if record:
                result.append(record)
        return result

    def _links(self) -> list[dict[str, Any]]:
        """Map repository and support links."""
        result: list[dict[str, Any]] = []
        if self.urls.repository:
            result.append({"url": self.urls.repository, "type": ["Repository"]})
        for route in self.support_routes.entries:
            if not route.url:
                continue
            system = str(route.system or "").lower()
            if "issue" in system:
                link_type = "Issue tracker"
            elif "mail" in system:
                link_type = "Mailing list"
            elif "discussion" in system or "forum" in system:
                link_type = "Discussion forum"
            elif "help" in system or "support" in system:
                link_type = "Helpdesk"
            else:
                link_type = "Other"
            result.append({"url": route.url, "type": [link_type]})
        return result

    def template_data(self) -> dict[str, Any]:
        """Build the single tool record stored in the top-level array."""
        homepage = self.urls.homepage or self.urls.documentation or self.urls.repository or ""
        tool: dict[str, Any] = {
            "name": self._name(self.project_name or self.project_slug, self.project_slug),
            "description": self._description(),
            "homepage": homepage,
        }
        optional_values: tuple[tuple[str, Any], ...] = (
            ("biotoolsID", self._biotools_id()),
            ("version", [str(self.versioning.version)[:100]] if self.versioning.version else []),
            ("otherID", self._other_ids()),
            ("toolType", list(dict.fromkeys(str(x.type) for x in self.interfaces.entries))),
            ("topic", self._topics()),
            (
                "operatingSystem",
                list(
                    dict.fromkeys(
                        _OPERATING_SYSTEM[str(item.name)]
                        for item in self.operating_systems.entries
                        if str(item.name) in _OPERATING_SYSTEM
                    )
                ),
            ),
            (
                "language",
                list(
                    dict.fromkeys(
                        language.name if language.name in _LANGUAGES else "Other"
                        for language in self.programming_languages.entries
                    )
                ),
            ),
            ("license", self._license()),
            ("maturity", _MATURITY.get(str(self.development_status or ""))),
            ("cost", _COST.get(str(self.access.type or ""))),
            (
                "accessibility",
                "Open access"
                if str(self.access.type or "") == "free"
                else (
                    "Restricted access"
                    if str(self.access.type or "") in {"free-with-restrictions", "commercial"}
                    else None
                ),
            ),
            ("function", self._functions()),
            ("link", self._links()),
            (
                "documentation",
                [{"url": self.urls.documentation, "type": ["General"]}]
                if self.urls.documentation
                else [],
            ),
            ("publication", self._publications()),
            ("credit", self._credits()),
        )
        tool.update({key: value for key, value in optional_values if value})
        return {"tools": [tool]}
