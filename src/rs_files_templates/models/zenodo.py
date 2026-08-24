"""Input model and normalization helpers for Zenodo software metadata."""

from __future__ import annotations

import re
from typing import Any

from rsm_schema.generated import Person

from .base import rsm_template_base
from .utils import (
    AUTHOR_ROLES,
    MAINTAINER_ROLES,
    PRINCIPAL_INVESTIGATOR_ROLES,
    contributors_with_roles,
    primary_affiliation,
)

_ZenodoRSM = rsm_template_base(
    "_ZenodoRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "licensing",
    "keywords",
    "contributors",
    "funding",
    "publications",
)

ZENODO_SCHEMA_URL = (
    "https://raw.githubusercontent.com/zenodo/zenodo/master/zenodo/modules/deposit/"
    "jsonschemas/deposits/records/legacyrecord.json"
)


class ZenodoModel(_ZenodoRSM):
    """Input model for the GitHub integration's ``.zenodo.json`` file.

    Zenodo reads this file from the repository when it archives a GitHub release.
    The release itself supplies the version and files; this model supplies the
    deposit metadata that the repository author wants to override or enrich.
    """

    template_name = ".zenodo.json.j2"
    output_name = ".zenodo.json"
    schema_url = ZENODO_SCHEMA_URL
    media_type = "json"

    @staticmethod
    def _normalize_orcid(value: str | None) -> str:
        """Return a bare ORCID identifier."""
        return re.sub(r"^https?://orcid\.org/", "", str(value or "").strip(), flags=re.IGNORECASE)

    @staticmethod
    def _person_name(person: Person) -> str:
        """Format a person as ``family, given`` for Zenodo."""
        given = str(person.given_names or "").strip()
        family = str(person.family_names or "").strip()
        if family:
            return f"{family}, {given}" if given else family
        return str(person.name or "").strip() or "Project member"

    @classmethod
    def _person_identity(cls, person: Person) -> str:
        """Build a stable identity used when deduplicating contributors."""
        if person.orcid:
            return f"orcid:{cls._normalize_orcid(person.orcid).lower()}"
        if person.email:
            return f"email:{person.email.strip().lower()}"
        return f"name:{cls._person_name(person).lower()}"

    @classmethod
    def _zenodo_person(cls, person: Person, contributor_type: str = "") -> dict[str, str]:
        """Map one shared person value to a Zenodo record."""
        record = {"name": cls._person_name(person)}
        if affiliation := primary_affiliation(person):
            record["affiliation"] = affiliation.name
        if person.orcid:
            record["orcid"] = cls._normalize_orcid(person.orcid)
        if contributor_type:
            record["type"] = contributor_type
        return record

    def _contributors(self) -> list[dict[str, str]]:
        """Build deduplicated maintainer and investigator records."""
        contributors: list[dict[str, str]] = []
        authors = contributors_with_roles(self.contributors.entries, AUTHOR_ROLES)
        seen = {self._person_identity(author) for author in authors}
        for people, contributor_type in (
            (
                contributors_with_roles(self.contributors.entries, MAINTAINER_ROLES),
                "ContactPerson",
            ),
            (
                contributors_with_roles(self.contributors.entries, PRINCIPAL_INVESTIGATOR_ROLES),
                "ProjectLeader",
            ),
        ):
            for person in people:
                identity = self._person_identity(person)
                if identity not in seen:
                    contributors.append(self._zenodo_person(person, contributor_type))
                    seen.add(identity)
        return contributors

    def _related_identifiers(self) -> list[dict[str, str]]:
        """Map publication identifiers to Zenodo relationships."""
        related: list[dict[str, str]] = []
        seen: set[str] = set()
        for publication in self.publications.entries:
            doi = str(publication.doi or "").strip()
            url = str(publication.url or "").strip()
            identifier = doi or url
            if not identifier or identifier in seen:
                continue
            record = {
                "identifier": identifier,
                "relation": "isDocumentedBy",
                "scheme": "doi" if doi else "url",
            }
            if doi:
                record["resource_type"] = "publication-article"
            related.append(record)
            seen.add(identifier)
        return related

    def _grants(self) -> list[dict[str, str]]:
        """Keep only grant identifiers that Zenodo can resolve."""
        grant_ids: list[str] = []
        for funding in self.funding.entries:
            grant_id = str(funding.award_number or funding.project_code or "").strip()
            if re.fullmatch(r"\d+|10\.13039/[^\s:]+::\S+", grant_id) and grant_id not in grant_ids:
                grant_ids.append(grant_id)
        return [{"id": grant_id} for grant_id in grant_ids]

    def template_data(self) -> dict[str, Any]:
        """Prepare values consumed by the explicit ``.zenodo.json.j2`` layout."""
        creators = [
            self._zenodo_person(author)
            for author in contributors_with_roles(self.contributors.entries, AUTHOR_ROLES)
        ]
        return {
            "title": self.project_name or self.project_slug,
            "description": (
                self.project_long_description
                or self.project_short_description
                or "Research software project."
            ),
            "creators": creators or [{"name": "Project team"}],
            "license": self.licensing.license or "",
            "keywords": [str(keyword.root) for keyword in self.keywords.entries],
            "contributors": self._contributors(),
            "grants": self._grants(),
            "related_identifiers": self._related_identifiers(),
        }
