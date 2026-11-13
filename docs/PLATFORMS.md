# GoreeCloud Contacts — Three-platform architecture

**Status, November 11, 2026:** Source development previews for browser web, native GTK4/libadwaita Linux, and existing native Kotlin Android. No deployment, cross-device synchronization, signed release or physical-device acceptance is claimed.

| Capability | Browser web | Native Linux | Android |
| --- | --- | --- | --- |
| Source | web/ | linux/goreecloud_contacts/ | app/ (existing Gradle project, android/README.md) |
| Records | Browser-profile IndexedDB | User-private SQLite (0700 directory, 0600 database) | Permission-gated Android Contacts Provider |
| Add/edit | Local editor | Native editor | System-confirmed Android intents |
| Delete | Confirmation, browser record | Confirmation, SQLite record | Not implemented in Android preview |
| Search | Names, phones, emails, organizations | Same six-field local profile | Existing Android provider-backed directory |
| Favorites | Browser-local | SQLite-local | Existing app-local favorite markers |
| Import | JSON v1 or exact limited vCard 3.0 profile, confirmation, atomic no-clobber | JSON v1 or exact limited vCard 3.0 profile, confirmation, atomic no-clobber | Existing single vCard review and system insert |
| Export | Explicit JSON and limited vCard 3.0 | Explicit JSON and limited vCard 3.0 | Existing scoped vCard/CSV; no full backup |
| Local offline CLI | No | Available in linux/goreecloud_contacts/cli.py; private SQLite, validation, backup/restore, no network | No |
| Remote sync | None | None | None, no INTERNET permission |

**Important:** Three independent stores are NOT automatic sync. The browser and Linux clients can deliberately exchange portable versioned JSON, preserving exactly the six fields described in shared/CONTRACT.md. Android remains a different on-device Contacts Provider client. Limited vCards omit favorites, photos, relationships, addresses, notes, structured group membership and other rich fields. The new vCard importers accept only the exact FN/N/TEL/EMAIL/ORG vCard 3.0 profile emitted here, generate fresh local IDs, refuse unknown or parameterized properties and reject already-present visible contact details atomically. Third-party or rich Android vCards must not be described as supported if their content fails this strict parser. JSON imports deliberately reject unknown fields, duplicate IDs, oversized input and conflicting existing IDs instead of silently discarding or overwriting personal data.

## Privacy and security boundaries

- Web records are inside the current browser profile. This app does not encrypt IndexedDB; other users of the unlocked profile could access it, and clearing the profile may delete it. Existing-record updates and deletes check their previous snapshot and refuse stale writes; same-origin tabs in one browser profile receive a contact-free BroadcastChannel change marker and refresh on visibility/focus. Independent browser-profile and physical-browser concurrency acceptance remains open. The source includes no telemetry, CDN, remote font, service worker, backend fetch or network API. The development web server binds only 127.0.0.1, whitelists assets and uses CSP/security headers. HTTPS hosting, origin trust, access control and deployed browser security acceptance are NOT implemented.
- Linux records live under the user's XDG data location in a private SQLite database. The app refuses unsafe permissions and symlinked database paths, uses parameterized SQL and explicit exports (create-only, permission 0600); it does NOT encrypt at rest or sync in the background. An attacker with the logged-in user's filesystem permissions can potentially read the SQLite and exported backup files.
- Android reads system contacts only with explicit READ_CONTACTS permission and retains its original privacy/consent restrictions; no INTERNET or WRITE_CONTACTS permission was introduced by this feature.
- Exported JSON and vCards are plaintext. Sharing or exporting always requires a user action; destination storage is the user's responsibility. No real user data or credentials are committed in fixtures.
- No GoreeCloud Identity, GoreeShield consent exchange, Wardveil transport, Mesh adapter or DAV account integration is enabled. Such features require independent security, privacy, identity and conflict-management acceptance.

## Verified GoreeCloud UI provenance

Web uses exactly the GoreeCloud UI alpha semantic role tokens from GoreeCloud/gc-ui main commit 05dfc0d4de75723a819d611647d089e437251b6f, CSS SHA-256 94db1f214858bb05373058c92ab47cfb41c49a70f90bceb18b90854e75ef35ef. The original MIT license is copied. The GoreeCloud umbrella SVG is the verified founder-supplied umbrella identity derivative from GoreeCloud/brand-assets, Git blob c171733ccb86ba5349f27a5d64f5ff8db59a82f4, not a newly invented GC UI logo. Linux uses matching verified light/dark semantic token roles adapted to native Adwaita widgets. Android retains its existing preview colors/theme, so complete cross-platform GC UI acceptance is not yet established.

## Run, build and test

Browser web: python3 web/server.py --port 8765, then open http://127.0.0.1:8765/. Test with node --test web/tests/*.test.mjs and python3 -m unittest discover -s web/tests -p 'test_*.py'. The static server is for loopback preview only.

Linux: requires GTK4, libadwaita 1, Python 3.11+, python3-gi and GI typelibs. Run PYTHONPATH=linux /usr/bin/python3 -m goreecloud_contacts.app from repo root. Optional non-destructive per-user installer: python3 linux/install_user.py. It does not read personal contacts and refuses existing installation filenames. Test PYTHONPATH=linux /usr/bin/python3 -m unittest discover -s linux/tests -p 'test_*.py' and PYTHONPATH=linux xvfb-run -a /usr/bin/python3 linux/tests/gtk_smoke.py. A separate required CI installed-launcher smoke uses an isolated XDG HOME/profile to verify real per-user installer output, actual GTK startup, 0700/0600 SQLite permissions and synthetic restart persistence; it disables desktop-portal D-Bus only in the headless test environment.

Android: original root Gradle build, gradle :app:testDebugUnitTest :app:assembleDebug :app:lintDebug. The Android debug APK is not signed/accepted for release; delivered APKs must be verified, standalone files in the authorized GoreeCloud Google Drive Artifacts location.

## Remaining independent release gates

- [ ] Browser visual/mobile/keyboard/screen reader/contrast acceptance, secure HTTPS delivery and backup/restore.
- [ ] Linux install/upgrade/rollback on supported distributions, real accessibility, signed package and performance tests.
- [ ] Android OEM, real-device, TalkBack/RTL/tablet and release signing checks.
- [ ] Future explicit Identity, GoreeShield, Wardveil and Mesh consent gates before any DAV/CardDAV synchronization.
- [ ] Update canonical GoreeCloud Google Drive repository inventory in place when supported by connector; never claim the Markdown body was updated merely because a comment or issue was added.

See shared/CONTRACT.md and each platform's README. This is development source, not a deployed service.
