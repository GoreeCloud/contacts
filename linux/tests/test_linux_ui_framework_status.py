"""Guard actual Contacts Linux UI framework compliance; source-only, no user data."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LinuxUiFrameworkAuditTests(unittest.TestCase):
    def test_current_gtk_ui_is_truthfully_flagged_for_migration(self):
        s = json.loads((ROOT / "docs/linux-ui-framework-status.json").read_text(encoding="utf-8"))
        ui = (ROOT / "linux/goreecloud_contacts/app.py").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(s["platform"], "linux")
        self.assertEqual(s["currentPrimaryUi"], "gtk4-libadwaita")
        self.assertEqual(s["status"], "migration-required")
        self.assertFalse(s["grandfathered"])
        self.assertFalse(s["targetRuntimeVerified"])
        self.assertFalse(s["releasedCompliant"])
        self.assertNotIn(s["currentPrimaryUi"], s["approvedPrimaryUi"])
        self.assertIn('gi.require_version("Gtk", "4.0")', ui)
        self.assertIn("class ContactsWindow(Adw.ApplicationWindow)", ui)
        self.assertIn("Linux framework compliance: migration required", readme)
        self.assertEqual(s["independentClientsUnchanged"], ["web", "android"])

    def test_approved_target_is_not_prematurely_selected(self):
        s = json.loads((ROOT / "docs/linux-ui-framework-status.json").read_text(encoding="utf-8"))
        self.assertEqual(s["target"], "selection-pending")
        docs = (ROOT / "docs/LINUX_UI_MIGRATION.md").read_text(encoding="utf-8")
        self.assertIn("Qt Quick on Qt 6.12.0", docs)
        self.assertIn("private user-local SQLite", docs)


if __name__ == "__main__":
    unittest.main()
