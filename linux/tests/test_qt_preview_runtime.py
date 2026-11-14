"""Disposable Qt 6.12 Linux smoke for the optional Contacts read-only UI."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

from PySide6.QtCore import QUrl, qVersion
from PySide6.QtGui import QGuiApplication, QWindow
from PySide6.QtQml import QQmlApplicationEngine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from goreecloud_contacts.core import ContactStore, new_contact
from goreecloud_contacts.qt_preview import ContactsBridge, load_preview_records


class QtContactsPreviewSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if qVersion() != "6.12.0":
            raise AssertionError("Expected Qt 6.12.0, got " + qVersion())
        cls.app = QGuiApplication.instance() or QGuiApplication(["goreecloud-contacts-preview-smoke"])

    def test_demo_does_not_need_private_database(self):
        records = load_preview_records()
        self.assertEqual(len(records), 2)
        self.assertTrue(all(c["name"].startswith("Example Contact ") for c in records))

    def test_private_load_is_readonly_and_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private" / "contacts.sqlite3"
            store = ContactStore(path)
            try:
                contact = new_contact("Synthetic Local Contact")
                store.save(contact, is_new=True)
            finally:
                store.close()
            before = (path.stat().st_size, path.stat().st_mtime_ns)
            records = load_preview_records(private=True, db=str(path))
            after = (path.stat().st_size, path.stat().st_mtime_ns)
            self.assertEqual(before, after, "Preview must not modify existing SQLite")
            self.assertEqual(records, [contact])

    def test_qml_loads_windowed_without_network(self):
        bridge = ContactsBridge(load_preview_records(), "Fictional example contacts • demo")
        engine = QQmlApplicationEngine()
        warnings = []
        engine.warnings.connect(lambda errors: warnings.extend(e.toString() for e in errors))
        engine.rootContext().setContextProperty("contactsBackend", bridge)
        qml = Path(__file__).resolve().parents[1] / "goreecloud_contacts" / "ContactsPreview.qml"
        engine.load(QUrl.fromLocalFile(str(qml)))
        self.assertFalse(warnings, "QML warning/error: " + " | ".join(warnings))
        self.assertEqual(len(engine.rootObjects()), 1)
        window = engine.rootObjects()[0]
        self.assertTrue(window.isVisible())
        self.assertEqual(window.visibility(), QWindow.Visibility.Windowed)
        bridge.applyFilter("example contact a", False)
        self.assertEqual(len(bridge.rows), 1)
        bridge.applyFilter("", True)
        self.assertEqual(len(bridge.rows), 1)
        window.close()


if __name__ == "__main__":
    unittest.main()
