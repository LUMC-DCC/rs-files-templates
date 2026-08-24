"""Model and normalization logic for ``codemeta.json``."""

from __future__ import annotations

from typing import Any

from rsm_schema.generated import ExternalDependency, Person

from .base import rsm_template_base
from .utils import normalize_orcid, organization_data, person_name, publication_link, registry_url

CODEMETA_SCHEMA_URL = (
    "https://lumc-dcc.github.io/rs-metadata/schema/1.0.0/codemeta-lumc.schema.json"
)

_CodeMetaRSM = rsm_template_base(
    "_CodeMetaRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "development_status",
    "keywords",
    "authors",
    "maintainers",
    "principal_investigators",
    "funding",
    "motivation",
    "related_software",
    "urls",
    "registries",
    "persistent_identifiers",
    "publications",
    "licensing",
    "include_metadata",
    "documentation_types",
    "community_files",
    "support_routes",
    "programming_languages",
    "software_functions",
    "interfaces",
    "operating_systems",
    "external_dependencies",
    "test_types",
    "quality_tools",
    "versioning",
    "distribution_channels",
    "containerization",
)


class CodeMetaModel(_CodeMetaRSM):
    """Published RSM fields needed to render ``codemeta.json``."""

    template_name = "codemeta.json.j2"
    output_name = "codemeta.json"
    schema_url = CODEMETA_SCHEMA_URL
    media_type = "json"

    @staticmethod
    def _person(person: Person) -> dict[str, Any]:
        result: dict[str, Any] = {"@type": "Person", "name": person_name(person)}
        if person.orcid:
            result["@id"] = f"https://orcid.org/{normalize_orcid(person.orcid)}"
        elif person.url:
            result["@id"] = person.url
        if person.given_names:
            result["givenName"] = person.given_names
        if person.family_names:
            result["familyName"] = person.family_names
        if person.email:
            result["email"] = person.email
        if person.affiliation:
            result["affiliation"] = organization_data(person.affiliation)
        if person.url:
            result["url"] = person.url
        return result

    @staticmethod
    def _dependency(dependency: ExternalDependency) -> dict[str, Any]:
        result: dict[str, Any] = {"@type": "SoftwareSourceCode", "name": dependency.name}
        if dependency.url:
            result.update({"@id": dependency.url, "url": dependency.url})
        if dependency.version_constraint:
            result["version"] = dependency.version_constraint
        if dependency.license:
            result["license"] = (
                dependency.license
                if dependency.license.startswith(("http://", "https://"))
                else f"https://spdx.org/licenses/{dependency.license}"
            )
        if dependency.purpose:
            result["description"] = dependency.purpose
        return result

    def _registry_links(self) -> list[str]:
        links: list[str] = []
        for registry in self.registries.entries:
            link = registry_url(registry)
            if link and link not in links:
                links.append(link)
        return links

    def _features(self) -> list[str]:
        features: list[str] = []
        for function in self.software_functions.entries:
            for operation in function.operation or []:
                feature = operation.uri or operation.term
                if feature and feature not in features:
                    features.append(feature)
            if function.summary and not function.operation and function.summary not in features:
                features.append(function.summary)
        return features or [
            self.motivation.purpose
            or self.project_short_description
            or "REPLACE_WITH_SOFTWARE_FUNCTION"
        ]

    def _identifiers(self) -> list[Any]:
        identifiers: list[Any] = []
        for identifier in self.persistent_identifiers.entries:
            identifier_type = str(identifier.type)
            if identifier_type == "doi":
                identifiers.append(
                    identifier.identifier
                    if identifier.identifier.startswith(("http://", "https://"))
                    else f"https://doi.org/{identifier.identifier}"
                )
            elif identifier.identifier.startswith(("http://", "https://")):
                identifiers.append(identifier.identifier)
            else:
                item: dict[str, Any] = {
                    "@type": "PropertyValue",
                    "propertyID": identifier_type,
                    "value": identifier.identifier,
                }
                if identifier.associated_version:
                    item["description"] = (
                        f"Persistent identifier for version {identifier.associated_version}"
                    )
                identifiers.append(item)
        return identifiers or [
            {
                "@type": "PropertyValue",
                "propertyID": "placeholder",
                "value": "REPLACE_WITH_PERSISTENT_IDENTIFIER",
            }
        ]

    def _license(self) -> Any:
        value = self.licensing.license or ""
        if not value:
            return {
                "@type": "CreativeWork",
                "name": "REPLACE_WITH_PROJECT_LICENSE",
                "url": "https://example.org/REPLACE_WITH_LICENSE",
            }
        if value.startswith(("http://", "https://")):
            return value
        if "\n" not in value and len(value) < 100:
            return f"https://spdx.org/licenses/{value}"
        return {
            "@type": "CreativeWork",
            "name": "Custom project license",
            "url": "https://example.org/REPLACE_WITH_CUSTOM_LICENSE_URL",
        }

    def _supporting_data(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        seen: set[str] = set()
        for function in self.software_functions.entries:
            for direction, values in (
                ("input", function.input or []),
                ("output", function.output or []),
            ):
                for function_io in values:
                    for data_format in function_io.format or []:
                        if not data_format.sample_url or data_format.sample_url in seen:
                            continue
                        result.append(
                            {
                                "@type": "DataFeed",
                                "@id": data_format.sample_url,
                                "name": data_format.term or f"Example {direction} data",
                                "url": data_format.sample_url,
                            }
                        )
                        seen.add(data_format.sample_url)
        return result

    def _has_generated_ci(self) -> bool:
        quality = self.quality_tools
        has_quality_ci = bool(quality.formatter or quality.linter or quality.type_checker)
        return bool(
            self.include_metadata
            or "CHANGELOG.md" in self.community_files.entries
            or self.documentation_types.entries
            or self.test_types.entries
            or has_quality_ci
            or self.containerization.entries
            or self.distribution_channels.entries
            or (
                self.licensing.license
                and str(self.licensing.compatibility_check) == "Yes - automated tooling"
            )
        )

    def template_data(self) -> dict[str, Any]:
        registry_links = self._registry_links()
        interfaces = list(dict.fromkeys(str(item.type) for item in self.interfaces.entries))
        runtime_platforms: list[str] = []
        languages: list[Any] = []
        for language in self.programming_languages.entries:
            label = language.name + (
                f" {language.version_constraint}" if language.version_constraint else ""
            )
            if label not in runtime_platforms:
                runtime_platforms.append(label)
            item = {"@type": "ComputerLanguage", "name": language.name}
            if language.version_constraint:
                item["version"] = language.version_constraint
            languages.append(item)
        if not languages:
            languages = ["REPLACE_WITH_PROGRAMMING_LANGUAGE"]
        for container in self.containerization.entries:
            container_type = str(container.type)
            if container_type not in runtime_platforms:
                runtime_platforms.append(container_type)
        operating_systems = [
            str(item.name) + (f" {item.specification}" if item.specification else "")
            for item in self.operating_systems.entries
            if not item.status or str(item.status) in {"Officially supported", "Expected to work"}
        ]
        funders = list(dict.fromkeys(x.funder for x in self.funding.entries if x.funder))
        funding_values = [
            x.award_number or x.project_code or x.award_title or x.funder
            for x in self.funding.entries
        ]
        publications = [
            {"@type": "ScholarlyArticle", "@id": link, **({"name": pub.title} if pub.title else {})}
            for pub in self.publications.entries
            if (link := publication_link(pub))
        ]
        repository = self.urls.repository or ""
        return {
            "project_name": self.project_name or self.project_slug,
            "description": self.project_long_description
            or self.project_short_description
            or "REPLACE_WITH_DESCRIPTION",
            "version": self.versioning.version or "0.1.0",
            "development_status": str(self.development_status or "REPLACE_WITH_DEVELOPMENT_STATUS"),
            "application_category": interfaces[0]
            if len(interfaces) == 1
            else (interfaces or "REPLACE_WITH_APPLICATION_CATEGORY"),
            "application_subcategory": [str(x) for x in self.motivation.categories.entries]
            if self.motivation.categories
            else [],
            "feature_list": self._features(),
            "programming_languages": languages,
            "authors": [self._person(x) for x in self.authors.entries]
            or [{"@type": "Organization", "name": "Project team"}],
            "identifiers": self._identifiers(),
            "maintainers": [self._person(x) for x in self.maintainers.entries],
            "principal_investigators": [
                self._person(x) for x in self.principal_investigators.entries
            ],
            "keywords": [x.root for x in self.keywords.entries],
            "code_repository": repository or "https://example.org/REPLACE_WITH_REPOSITORY",
            "continuous_integration": f"{repository.rstrip('/')}/actions"
            if repository.startswith("https://github.com/") and self._has_generated_ci()
            else None,
            "license": self._license(),
            "url": self.urls.homepage or self.urls.documentation,
            "software_help": self.urls.documentation,
            "issue_tracker": next((x.url for x in self.support_routes.entries if x.url), None),
            "release_notes": f"{repository.rstrip('/')}/blob/HEAD/CHANGELOG.md"
            if "CHANGELOG.md" in self.community_files.entries and repository
            else None,
            "runtime_platforms": runtime_platforms,
            "operating_systems": operating_systems,
            "software_requirements": [
                self._dependency(x) for x in self.external_dependencies.entries
            ],
            "supporting_data": self._supporting_data(),
            "funders": funders,
            "funding_values": [x for x in funding_values if x],
            "related_links": list(
                dict.fromkeys(x.url_or_doi for x in self.related_software.entries if x.url_or_doi)
            ),
            "same_as": registry_links,
            "reference_publications": publications,
        }
