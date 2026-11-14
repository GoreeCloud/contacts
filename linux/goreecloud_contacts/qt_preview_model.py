"""Qt Quick Contacts preview data filtering, without GUI or network dependencies.

Reuses the established Contacts validation contract and matches the legacy
search/favorites semantics without touching SQLite.
"""
from __future__ import annotations

import unicodedata

from .core import ContactError, validate_collection


def filter_contacts(records, query: str = "", favorites_only: bool = False) -> list[dict]:
    """Return validated, sorted, display-only rows.

    There are no mutations, file access, network requests, or logging here.
    """
    if not isinstance(query, str) or len(query) > 160:
        raise ContactError("Invalid search text")
    if type(favorites_only) is not bool:
        raise ContactError("Invalid favorites filter")

    def fold(text: str) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(c)
        ).casefold()

    needle = fold(query.strip())
    contacts = validate_collection(records)
    matched = [
        c for c in contacts
        if (not favorites_only or c["favorite"])
        and (not needle or any(
            needle in fold(c[k])
            for k in ("name", "phone", "email", "organization")
        ))
    ]
    return sorted(matched, key=lambda c: (not c["favorite"], fold(c["name"]), c["id"]))
