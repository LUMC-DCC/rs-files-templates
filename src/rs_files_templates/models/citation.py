"""Model for ``CITATION.cff``."""

from __future__ import annotations

from typing import Any

from rsm_schema.generated import Person, Publication

from .base import rsm_template_base
from .utils import normalize_orcid, person_name

_CitationRSM = rsm_template_base(
    "_CitationRSM",
    "project_name",
    "project_slug",
    "project_short_description",
    "project_long_description",
    "versioning",
    "urls",
    "authors",
    "maintainers",
    "keywords",
    "persistent_identifiers",
    "publications",
)

CFF_SCHEMA_URL = "https://citation-file-format.github.io/1.2.0/schema.json"


class CitationModel(_CitationRSM):
    """Input model for ``CITATION.cff``."""

    template_name = "CITATION.cff.j2"
    output_name = "CITATION.cff"
    schema_url = CFF_SCHEMA_URL
    media_type = "yaml"

    @staticmethod
    def _person(person: Person) -> dict[str, Any]:
        """Prepare one person for the CFF layout."""
        structured = bool(person.family_names or person.given_names)
        result: dict[str, Any] = {
            "family_names": person.family_names or (person_name(person) if structured else None),
            "given_names": person.given_names,
            "name": None if structured else person_name(person),
            "affiliation": person.affiliation.name if person.affiliation else None,
            "email": person.email,
            "orcid": f"https://orcid.org/{normalize_orcid(person.orcid)}" if person.orcid else None,
            "website": person.url,
        }
        return result

    @staticmethod
    def _publication_title(publication: Publication) -> str:
        """Choose the best available title for a CFF reference."""
        return (
            publication.title
            or publication.citation
            or (f"Publication {publication.doi}" if publication.doi else "")
            or (f"Publication {publication.url}" if publication.url else "")
            or (f"Publication PMID {publication.pmid}" if publication.pmid else "")
            or (f"Publication {publication.pmcid}" if publication.pmcid else "")
            or "Associated publication"
        )

    def _publication(self, publication: Publication) -> dict[str, Any]:
        """Prepare one publication reference for CFF."""
        requested = (publication.type or "article").lower().replace(" ", "-")
        cff_types = {
            "art",
            "article",
            "audiovisual",
            "bill",
            "blog",
            "book",
            "catalogue",
            "conference-paper",
            "conference",
            "data",
            "database",
            "dictionary",
            "edited-work",
            "encyclopedia",
            "film-broadcast",
            "generic",
            "government-document",
            "grant",
            "hearing",
            "historical-work",
            "legal-case",
            "legal-rule",
            "magazine-article",
            "manual",
            "map",
            "multimedia",
            "music",
            "newspaper-article",
            "pamphlet",
            "patent",
            "personal-communication",
            "proceedings",
            "report",
            "serial",
            "slides",
            "software-code",
            "software-container",
            "software-executable",
            "software-virtual-machine",
            "software",
            "sound-recording",
            "standard",
            "statute",
            "thesis",
            "unpublished",
            "video",
            "website",
        }
        result: dict[str, Any] = {
            "type": requested if requested in cff_types else "generic",
            "title": self._publication_title(publication),
            "authors": [self._person(author) for author in (publication.authors or [])],
            "doi": (publication.doi or "")
            .replace("https://doi.org/", "")
            .replace("http://dx.doi.org/", "")
            .replace("http://doi.org/", ""),
            "pmcid": publication.pmcid,
            "url": publication.url,
            "pmid": publication.pmid,
            "note": publication.note,
        }
        return result

    def template_data(self) -> dict[str, Any]:
        """Prepare identifiers and references for the readable CFF template."""
        identifiers = []
        for identifier in self.persistent_identifiers.entries:
            item: dict[str, Any] = {
                "type": identifier.type if identifier.type in {"doi", "url", "swh"} else "other",
                "value": identifier.identifier,
                "description": None,
            }
            if identifier.associated_version:
                item["description"] = (
                    f"Persistent identifier for version {identifier.associated_version}"
                )
            identifiers.append(item)
        publications = [
            self._publication(publication)
            for publication in self.publications.entries
            if publication.authors
        ]
        preferred = next(
            (
                self._publication(publication)
                for publication in self.publications.entries
                if publication.preferred and publication.authors
            ),
            None,
        )
        return {
            "project_name": self.project_name or self.project_slug,
            "version": self.versioning.version or "0.1.0",
            "abstract": self.project_long_description or self.project_short_description,
            "repository_url": self.urls.repository,
            "url": self.urls.homepage or self.urls.documentation,
            "authors": [self._person(author) for author in self.authors.entries],
            "maintainers": [self._person(person) for person in self.maintainers.entries],
            "keywords": [keyword.root for keyword in self.keywords.entries],
            "identifiers": identifiers,
            "preferred_citation": preferred,
            "references": publications,
        }
