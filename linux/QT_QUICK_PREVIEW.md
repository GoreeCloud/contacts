# GoreeCloud Contacts — Qt Quick 6.12.0 migration preview

**Status:** Draft, experimental, read-only and optional. This is not the supported default Linux client, a completed GTK migration, a Stable release, or a production installer.

My mandatory November 13, 2026 Linux UI standard requires all existing and future Linux graphical applications to use Qt Quick 6.12.0, Flutter Linux Desktop, or Slint as their primary UI, with no grandfathering. This separate preview is an initial source implementation on the way to that requirement; the established GTK interface and its installer remain unchanged until a migration is fully verified.

## Boundaries

- A Qt Quick 6.12.0 desktop window replaces **only the list/search/favorites presentation** in this proof of concept. Create/edit, delete, import/export, backups, installers, themes, accessibility and full feature parity remain pending.
- `qt_preview_model.py` reuses `core.validate_collection` to enforce the established portable local-contact shape; its search and sorting rules mirror the existing SQLite store. No network, accounts, telemetry or provider synchronization.
- `qt_preview.py` runs in **fictional demo mode by default**, without opening the user's database. Only explicit `--private` reads an existing private Contacts SQLite database using `ContactStore(readonly=True)` and closes it after taking a read-only snapshot. There is **no write path in the Qt preview**.
- The Linux application opens windowed, non-maximized and non-fullscreen by default, with candidate GC UI alpha Iris/light semantic values taken from the verified [GoreeCloud UI token source](https://github.com/GoreeCloud/gc-ui/blob/main/tokens/gc.tokens.json), not an independently invented design system.
- This preview does **not** introduce an updater, install/remove integration, or implicit rollout.

## Developer commands (not proof of runtime acceptance)

From repository root, in an **isolated Linux development environment** with Qt 6.12.0 and suitable GUI dependencies:

```sh
python3 -m venv .venv-contacts-qt
.venv-contacts-qt/bin/python -m pip install --only-binary=:all: -r linux/requirements-qt-preview.txt
PYTHONPATH=linux .venv-contacts-qt/bin/python -m goreecloud_contacts.qt_preview
# Optional, with explicit authorization to read the existing local personal database:
PYTHONPATH=linux .venv-contacts-qt/bin/python -m goreecloud_contacts.qt_preview --private
```

Run the isolated synthetic pure tests:

```sh
PYTHONPATH=linux python3 -m unittest discover -s linux/tests -p 'test_qt_preview_model.py' -v
```

A separate nonpublishing CI workflow checks the QML startup on headless Linux using **fictional data only**. It also tests a temporary synthetic local SQLite database using read-only access. No real contacts are required.

## Required work before default switch

Preserve the existing offline/private data store, secure file handling, explicit user consent, JSON/vCard compatibility, favorite sorting, contact editor, all current import/export/recovery protections, keyboard/focus/screen-reader behavior, theme states, native integrations, windowing and installation/rollback. Verify X11 and Wayland interaction, real desktop accessibility and founder visual acceptance. Then update the default launcher only after evidence, without prematurely removing the legacy rollback path.

**Tracking:** [migration issue #25](https://github.com/GoreeCloud/contacts/issues/25) and [mandatory framework standard](https://drive.google.com/file/d/1L-93POcFZE12F-vYxbSc9XquQ-KWOa6f/view). Individual application compliance is **not yet established**.
