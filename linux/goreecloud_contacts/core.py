"""GoreeCloud Contacts Linux: small, offline-only private contact domain.

No account, network, sync endpoint, telemetry or Android system contacts access.
The portable v1 JSON format is intentionally limited to six fields.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import unicodedata
from uuid import UUID, uuid4

FORMAT = "goreecloud.contacts.v1"
MAX_CONTACTS = 5000
MAX_BUNDLE_BYTES = 2 * 1024 * 1024
LIMITS = {"name": 160, "phone": 80, "email": 254, "organization": 160}
KEYS = frozenset(("id", "name", "phone", "email", "organization", "favorite"))
UUID4 = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
UNSAFE = re.compile(r"[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u2028\u2029\u202a-\u202e\u2066-\u2069]")
SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  organization TEXT NOT NULL,
  favorite INTEGER NOT NULL CHECK(favorite IN (0,1))
);
"""

class ContactError(ValueError):
    """A failed validation or refused local operation, without private content."""


def _field(key: str, value: object) -> str:
    if not isinstance(value, str):
        raise ContactError(f"Invalid {key} type")
    text = unicodedata.normalize("NFC", value.strip())
    try:
        length_bytes = len(text.encode("utf-8", errors="strict"))
    except UnicodeError as error:
        raise ContactError(f"Invalid {key} content") from error
    if len(text) > LIMITS[key] or length_bytes > 4 * LIMITS[key] or UNSAFE.search(text):
        raise ContactError(f"Invalid {key} content")
    if key == "name" and not text:
        raise ContactError("Name is required")
    return text


def validate(contact: object) -> dict:
    if not isinstance(contact, dict) or set(contact) != KEYS:
        raise ContactError("Unexpected or missing contact fields")
    ident = contact["id"]
    if not isinstance(ident, str) or not UUID4.fullmatch(ident):
        raise ContactError("Invalid contact ID")
    if type(contact["favorite"]) is not bool:
        raise ContactError("Invalid favorite flag")
    return {
        "id": ident, "name": _field("name", contact["name"]),
        "phone": _field("phone", contact["phone"]),
        "email": _field("email", contact["email"]),
        "organization": _field("organization", contact["organization"]),
        "favorite": contact["favorite"],
    }


def validate_collection(data: object) -> list[dict]:
    if not isinstance(data, list) or len(data) > MAX_CONTACTS:
        raise ContactError("Too many contacts")
    contacts = [validate(c) for c in data]
    if len({c["id"] for c in contacts}) != len(contacts):
        raise ContactError("Duplicate contact IDs")
    return contacts


def new_contact(name: str, phone="", email="", organization="", favorite=False) -> dict:
    return validate({
        "id": str(uuid4()), "name": name, "phone": phone,
        "email": email, "organization": organization, "favorite": favorite,
    })


def parse_backup(text: str) -> list[dict]:
    if not isinstance(text, str):
        raise ContactError("Expected UTF-8 JSON text")
    try:
        if len(text.encode("utf-8")) > MAX_BUNDLE_BYTES:
            raise ContactError("Backup exceeds size limit")
        bundle = json.loads(text)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ContactError("Invalid backup JSON") from error
    if not isinstance(bundle, dict) or set(bundle) != {"format", "contacts"}:
        raise ContactError("Unexpected backup fields")
    if bundle["format"] != FORMAT:
        raise ContactError("Unsupported backup format")
    return validate_collection(bundle["contacts"])


def make_backup(records: list[dict]) -> str:
    contacts = sorted(validate_collection(records), key=lambda c: c["id"])
    text = json.dumps({"format": FORMAT, "contacts": contacts},
                      ensure_ascii=False, indent=2) + "\n"
    if len(text.encode("utf-8")) > MAX_BUNDLE_BYTES:
        raise ContactError("Backup exceeds size limit")
    return text


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def _fold(line: str) -> str:
    chunk = ""
    size = 0
    output = []
    for glyph in line:
        byte_count = len(glyph.encode("utf-8"))
        if size + byte_count > 75:
            output.append(chunk)
            chunk = " "
            size = 1
        chunk += glyph
        size += byte_count
    output.append(chunk)
    return "\r\n".join(output)


def make_vcards(records: list[dict]) -> str:
    lines = []
    for c in validate_collection(records):
        lines.extend(("BEGIN:VCARD", "VERSION:3.0",
                      "N:" + _escape(c["name"]) + ";;;;",
                      "FN:" + _escape(c["name"])))
        if c["phone"]:
            lines.append("TEL:" + _escape(c["phone"]))
        if c["email"]:
            lines.append("EMAIL:" + _escape(c["email"]))
        if c["organization"]:
            lines.append("ORG:" + _escape(c["organization"]))
        lines.append("END:VCARD")
    output = "\r\n".join(map(_fold, lines)) + ("\r\n" if lines else "")
    if len(output.encode("utf-8")) > MAX_BUNDLE_BYTES:
        raise ContactError("vCard export exceeds size limit")
    return output


def _private_path(path: str | Path | None) -> Path:
    if path is None:
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
        path = base / "goreecloud" / "contacts" / "contacts.sqlite3"
    location = Path(os.path.abspath(os.fspath(path)))
    folder = location.parent
    if folder.is_symlink():
        raise ContactError("Refusing symlinked private data directory")
    try:
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        info = folder.stat(follow_symlinks=False)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ContactError("Private data directory must be owned by you and mode 0700")
        if location.is_symlink():
            raise ContactError("Refusing symlinked database")
    except OSError as error:
        raise ContactError("Cannot prepare private data directory") from error
    return location


class ContactStore:
    def __init__(self, path: str | Path | None = None):
        self.path = _private_path(path)
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        try:
            fd = os.open(self.path, flags, 0o600)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or info.st_mode & 0o077:
                raise ContactError("Unsafe database file permissions or type")
        except OSError as error:
            raise ContactError("Cannot safely open private database") from error
        finally:
            if "fd" in locals():
                os.close(fd)
        self.db = sqlite3.connect(str(self.path), timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA secure_delete=ON")
        self.db.execute("PRAGMA trusted_schema=OFF")
        self.db.executescript(SQL_SCHEMA)

    def close(self):
        self.db.close()

    def list(self) -> list[dict]:
        items = [
            dict(id=r["id"], name=r["name"], phone=r["phone"], email=r["email"],
                 organization=r["organization"], favorite=bool(r["favorite"]))
            for r in self.db.execute("SELECT id,name,phone,email,organization,favorite FROM contacts")
        ]
        return validate_collection(items)

    def filtered(self, query: str = "", favorites_only: bool = False) -> list[dict]:
        def fold(value: str) -> str:
            return "".join(ch for ch in unicodedata.normalize("NFKD", value)
                           if not unicodedata.combining(ch)).casefold()
        needle = fold(query.strip())
        contacts = self.list()
        matched = [c for c in contacts if (not favorites_only or c["favorite"]) and
                   (not needle or any(needle in fold(c[key]) for key in
                                     ("name", "phone", "email", "organization")))]
        return sorted(matched, key=lambda c: (not c["favorite"], fold(c["name"]), c["id"]))

    def _current(self, ident: str) -> dict | None:
        row=self.db.execute(
            "SELECT id,name,phone,email,organization,favorite FROM contacts WHERE id=?",
            (ident,)).fetchone()
        if row is None:
            return None
        return dict(id=row["id"],name=row["name"],phone=row["phone"],
                    email=row["email"],organization=row["organization"],
                    favorite=bool(row["favorite"]))

    def save(self, raw: dict, *, is_new: bool, expected: dict | None = None):
        c=validate(raw)
        prior=None
        if not is_new:
            if expected is None:
                raise ContactError("A previous contact version is required")
            prior=validate(expected)
            if prior["id"] != c["id"]:
                raise ContactError("Contact identity changed")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if is_new:
                if self.db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0] >= MAX_CONTACTS:
                    raise ContactError("Contact limit reached")
                try:
                    self.db.execute("INSERT INTO contacts VALUES (?,?,?,?,?,?)",
                                    (c["id"],c["name"],c["phone"],c["email"],
                                     c["organization"],int(c["favorite"])))
                except sqlite3.IntegrityError as error:
                    raise ContactError("Contact already exists") from error
            else:
                if self._current(c["id"]) != prior:
                    raise ContactError("Contact changed; reload before saving")
                self.db.execute(
                    "UPDATE contacts SET name=?,phone=?,email=?,organization=?,favorite=? WHERE id=?",
                    (c["name"],c["phone"],c["email"],c["organization"],
                     int(c["favorite"]),c["id"]))

    def delete(self, ident: str, *, expected: dict):
        if not isinstance(ident,str) or not UUID4.fullmatch(ident):
            raise ContactError("Invalid contact ID")
        prior=validate(expected)
        if prior["id"] != ident:
            raise ContactError("Contact identity changed")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self._current(ident) != prior:
                raise ContactError("Contact changed; reload before deleting")
            self.db.execute("DELETE FROM contacts WHERE id=?", (ident,))

    def import_new(self, incoming: list[dict], *, reject_visible_duplicates=False) -> int:
        contacts = validate_collection(incoming)
        try:
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                if self.db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0] + len(contacts) > MAX_CONTACTS:
                    raise ContactError("Contact limit reached")
                if reject_visible_duplicates:
                    from .vcard import visible_identity
                    known={visible_identity(c) for c in self.list()}
                    for c in contacts:
                        key=visible_identity(c)
                        if key in known:
                            raise ContactError("Import refused: contact details already exist")
                        known.add(key)
                self.db.executemany("INSERT INTO contacts VALUES (?,?,?,?,?,?)", [
                    (c["id"],c["name"],c["phone"],c["email"],c["organization"],int(c["favorite"]))
                    for c in contacts
                ])
        except sqlite3.IntegrityError as error:
            raise ContactError("Import was rolled back; duplicate contact ID") from error
        return len(contacts)


def read_backup_file(path: str | Path) -> list[dict]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as file:
            if not stat.S_ISREG(os.fstat(file.fileno()).st_mode) or os.fstat(file.fileno()).st_size > MAX_BUNDLE_BYTES:
                raise ContactError("Invalid backup file size or type")
            payload = file.read(MAX_BUNDLE_BYTES + 1)
        return parse_backup(payload.decode("utf-8", errors="strict"))
    except (OSError, UnicodeError) as error:
        raise ContactError("Cannot safely read backup file") from error


def write_new_file(path: str | Path, text: str):
    try:
        data = text.encode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ContactError("Invalid export data") from error
    if len(data) > MAX_BUNDLE_BYTES:
        raise ContactError("Export exceeds size limit")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    created = False
    try:
        fd = os.open(path, flags, 0o600)
        created = True
        with os.fdopen(fd, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
    except OSError as error:
        if created:
            try:
                os.unlink(path)
            except OSError:
                pass
        raise ContactError("Export refused; choose a new writable filename") from error
