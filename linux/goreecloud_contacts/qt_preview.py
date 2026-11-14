"""Optional Qt Quick 6.12.0 read-only Contacts desktop migration preview.

No launcher, installer, GTK code, SQLite schema or user's local contacts data
is changed. Default invocation shows fictional data. Explicit --private
loads an existing Contacts SQLite file read-only using the established domain.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .core import ContactError, ContactStore, data_location, new_contact, validate_collection
from .qt_preview_model import filter_contacts


class ContactsBridge(QObject):
    rowsChanged = Signal()

    def __init__(self, records: list[dict], source_label: str):
        super().__init__()
        self._all = validate_collection(records)
        self._rows = filter_contacts(self._all)
        self._source_label = source_label

    @Property("QVariantList", notify=rowsChanged)
    def rows(self):
        return self._rows

    @Property(str, constant=True)
    def sourceLabel(self):
        return self._source_label

    @Slot(str, bool)
    def applyFilter(self, query: str, favorites_only: bool):
        next_rows = filter_contacts(self._all, query, favorites_only)
        if next_rows != self._rows:
            self._rows = next_rows
            self.rowsChanged.emit()


def load_preview_records(*, private: bool = False, db: str | None = None) -> list[dict]:
    """No access to existing user data unless explicitly requested."""
    if not private:
        if db:
            raise ContactError("--db requires explicit --private")
        return [
            new_contact("Example Contact A", "+1 555 010 0100", "example-a@invalid.example", "GoreeCloud", True),
            new_contact("Example Contact B", "+1 555 010 0200", "example-b@invalid.example", "Sample", False),
        ]
    path = data_location(db)
    # Prevent ContactStore preflight from creating the default data directory
    # when the user has never created a database. A symlink is refused by store.
    if not path.is_file():
        raise ContactError("Private Contacts database does not exist")
    store = ContactStore(path, readonly=True)
    try:
        return store.list()
    finally:
        store.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="GoreeCloud Contacts optional Qt Quick read-only preview")
    parser.add_argument("--private", action="store_true", help="Read existing local Contacts database (never modify)")
    parser.add_argument("--db", help="Existing private SQLite file; requires --private")
    args = parser.parse_args(argv)

    if qVersion() != "6.12.0":
        print("Qt 6.12.0 is required for the Contacts preview.", file=sys.stderr)
        return 2
    try:
        records = load_preview_records(private=args.private, db=args.db)
    except (ContactError, OSError):
        print("Cannot safely open the requested Contacts database.", file=sys.stderr)
        return 3

    app = QGuiApplication([sys.argv[0]])
    app.setOrganizationName("GoreeCloud")
    app.setApplicationName("GoreeCloud Contacts — Qt Preview")
    bridge = ContactsBridge(records, "Existing private SQLite • read-only" if args.private
                            else "Fictional example contacts • demo")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("contactsBackend", bridge)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name("ContactsPreview.qml"))))
    if not engine.rootObjects():
        return 4
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
