# Mandatory Linux graphical UI migration — GoreeCloud Contacts

**Status: migration required.** This is a source-verified compliance finding, **not** a claim that a new UI has been implemented or tested.

The [founder Linux UI standard](https://drive.google.com/file/d/1L-93POcFZE12F-vYxbSc9XquQ-KWOa6f/view), reflected in [master Section 14.2B](https://drive.google.com/file/d/1W7eCxfSEw1_fpK7wSw8gfeHHCIJ8IrBE/view), requires every existing and future **graphical Linux application** to use **Qt Quick on Qt 6.12.0, Flutter Linux Desktop, or Slint** as its primary UI, without grandfathering.

## Verified starting point

- `linux/goreecloud_contacts/app.py` imports `gi.repository.Gtk` and `Adw`, declares `ContactsWindow(Adw.ApplicationWindow)`, and builds the contact editor with GTK widgets.
- `linux/pyproject.toml` declares the Linux GTK4/libadwaita preview. Consequently the current Linux UI is **not approved**, even though existing functionality can remain usable for maintenance.
- The independent **web** client and **Android** Contacts Provider client are not subject to this Linux-only UI selection change. No cross-device sync or encryption-at-rest is implied.

## Controlled migration gates

1. Select Qt Quick 6.12.0, Flutter Linux Desktop, or Slint using measured Python/SQLite integration, accessibility, 100–400% scaling, packaging, resource footprint, licensing and maintenance—not by importing a decorative UI module. The choice is **pending**.
2. Preserve `linux/goreecloud_contacts/core.py` storage and trust boundaries: private user-local SQLite, symlink/permission checks, versioned strict manual JSON/vCard import/export, no-clobber atomic backup and user-confirmed delete. No new telemetry or background upload.
3. Build a **genuine approved primary Linux UI** with local search, favorites, add/edit/delete confirmation, file import/export review, consent, keyboard shortcuts, focus, high contrast, error handling and normal-windowed startup.
4. Validate file picker/native integration without relaxing input strictness or granting filesystem/contacts permissions. Test real GNOME/KDE Wayland/X11 and assistive technologies.
5. Verify clean install, upgrade/rollback and data preservation, native source and packaging, and representative Linux runtime. Retire GTK primary UI only after parity and independent acceptance.

**Tracking:** [Contacts migration issue #25](https://github.com/GoreeCloud/contacts/issues/25). Update the source-backed [status record](linux-ui-framework-status.json) only after actual approved framework implementation, package and runtime evidence. This document does **not** declare compliance, a release or deployment.
