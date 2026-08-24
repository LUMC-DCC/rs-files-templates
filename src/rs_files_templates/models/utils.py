"""Small normalization helpers shared by file models."""

from __future__ import annotations

from collections.abc import Iterable

from rsm_schema.generated import Contributor, Organization, Person, Publication, Registry

AUTHOR_ROLES = frozenset({"Original author", "Co-author"})
MAINTAINER_ROLES = frozenset({"Maintainer"})
PRINCIPAL_INVESTIGATOR_ROLES = frozenset({"Principal investigator"})


def normalize_orcid(value: str | None) -> str:
    """Return an ORCID without its resolver URL prefix."""
    value = str(value or "").strip()
    for prefix in ("https://orcid.org/", "http://orcid.org/"):
        if value.lower().startswith(prefix):
            return value[len(prefix) :]
    return value


def person_name(person: Person) -> str:
    """Return a display name from either flat or structured person fields."""
    if person.name:
        return person.name.strip()
    return (
        " ".join(
            part.strip()
            for part in (person.given_names or "", person.family_names or "")
            if part and part.strip()
        )
        or "Project member"
    )


def person_label(person: Person) -> str:
    """Return a human-readable role label."""
    return person_name(person)


def contributors_with_roles(
    contributors: Iterable[Contributor],
    roles: frozenset[str],
) -> list[Contributor]:
    """Return contributors declaring at least one requested role."""
    return [
        contributor
        for contributor in contributors
        if roles.intersection(str(role) for role in contributor.roles)
    ]


def primary_affiliation(person: Person) -> Organization | None:
    """Return the person's most relevant affiliation, when supplied."""
    return person.affiliations[0] if person.affiliations else None


def organization_data(organization: Organization) -> dict[str, object]:
    """Return a CodeMeta organization object."""
    result: dict[str, object] = {"@type": "Organization", "name": organization.name}
    if organization.identifier:
        result["@id"] = organization.identifier
    for field in ("email", "url", "address"):
        value = getattr(organization, field)
        if value:
            result[field] = value
    return result


def registry_url(registry: Registry) -> str:
    """Resolve common registry identifiers to public URLs."""
    value = registry.url_or_id or ""
    if value.startswith(("http://", "https://")):
        return value
    normalized = (registry.name or "").lower().replace(".", "").replace("-", "").replace(" ", "")
    if normalized == "biotools":
        return f"https://bio.tools/{value.removeprefix('biotools:')}"
    if normalized == "pypi":
        return f"https://pypi.org/project/{value}/"
    if normalized == "cran":
        return f"https://cran.r-project.org/package={value}"
    return value


def publication_link(publication: Publication) -> str:
    """Resolve a publication model to its most useful public URL."""
    doi = getattr(publication, "doi", None)
    if doi:
        return doi if doi.startswith(("http://", "https://")) else f"https://doi.org/{doi}"
    if getattr(publication, "url", None):
        return publication.url
    if getattr(publication, "pmcid", None):
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{publication.pmcid}/"
    if getattr(publication, "pmid", None):
        return f"https://pubmed.ncbi.nlm.nih.gov/{publication.pmid}/"
    return ""
