# GoreeCloud Contacts — native Linux application

An original GTK4/libadwaita Linux desktop Contacts app, not a web wrapper. It uses its own private SQLite database, never Android Contacts Provider data, browser IndexedDB or CardDAV servers.

Runtime: GTK4, libadwaita 1, GObject Introspection (python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1 on compatible Debian/Ubuntu), Python >= 3.11. Run from repository root:
  PYTHONPATH=linux /usr/bin/python3 -m goreecloud_contacts.app

Optional guarded per-user installation (explicit execution, no root, no personal contact transfer):
  python3 linux/install_user.py

It creates a launcher in ~/.local/bin, a desktop entry in ~/.local/share/applications and application code in ~/.local/share/goreecloud/contacts-linux, honoring XDG overrides. Refuses existing installation paths; private launcher/desktop entries use exclusive creation, file-sync before success, and incomplete-write cleanup on failure. Installer rollback touches only newly created application files, not personal Contacts SQLite; no automatic replacement/updater is provided. Private contact data lives separately under ~/.local/share/goreecloud/contacts (0700 dir, 0600 SQLite). Exports are exclusive create-only 0600 files; there is no encryption at rest.

Implemented in source: native list/search/favorites, editor, user-confirmed delete, explicit JSON and limited vCard import, private JSON backup and limited vCard export. Rich vCard properties are rejected; favorites cannot be restored from vCards, OS file chooser and native toast feedback, using verified GC UI semantic colors. Neither CardDAV sync nor a deployed backend is included.

Tests: PYTHONPATH=linux /usr/bin/python3 -m unittest discover -s linux/tests -p test_*.py; PYTHONPATH=linux xvfb-run -a /usr/bin/python3 linux/tests/gtk_smoke.py.

Physical Linux installation/removal/upgrade acceptance, accessibility tests, signing and Stable release gate remain open. See docs/PLATFORMS.md in the parent repository.
