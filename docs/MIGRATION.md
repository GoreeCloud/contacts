# GoreeCloud Contacts standalone repository migration

**Status:** Source and CI extraction under review; this document does not establish a released or deployed Contacts app.

## Verified source and history

- Original repository: https://github.com/GoreeCloud/android-defaults
- Source tree: `contacts/` (an independently built Android Kotlin project).
- Exact source monorepo main commit at extraction: `c7f65cdd55e7fa742743853244a8959e0d814ac4` (November 10, 2026).
- Source subtree-filtered Git tip: `3f160f287ccfa4fac01890270bac0fa1842a263e`, comprising **33 Contacts-specific commits**, reachable from the standalone migration merge.
- Destination repository: https://github.com/GoreeCloud/contacts; prior placeholder main commit `c52f95561f840ef77070674ff6a4cd99a025c3d4` is preserved in the merge ancestry.
- Retained original license: MIT, copyright 2026 GoreeCloud, with no change to Kotlin app package `com.goreecloud.contacts`, min SDK 26, target/compile SDK 35, or version `0.1.0-dev`.

## Source-only adaptations

The standalone repository lifts the former `contacts/` Gradle tree to the root and migrates its Contacts-only CI workflow. The monorepo's two shared **synthetic-only ADB emulator safety scripts** are retained in `ci/`, with Dialer-specific test cases removed. Screenshot checks remain fail-closed: explicit emulator serial, qemu identity and exact API checks must succeed before any ADB install/clear or screenshot operation. The CI workflow must run on every relevant branch and PR revision, not rely on the old monorepo path filter.

## Release and security boundaries

The source directory contains no INTERNET or WRITE_CONTACTS permission. It uses Android permission-gated on-device Contacts Provider reads, user-controlled share/export/document-picker flows and private app-local favorites. Existing unit and emulator tests must pass independently after path extraction. No migration of device contact data, Android preferences, encryption keys, account state, release signing, customer data or production endpoints is performed here. The original app ID is retained intentionally to protect future upgrade continuity, but that does **not** prove install/upgrade behavior; signed APK compatibility and device migration need independent validation.

**Remaining acceptance:** Hosted CI for JVM/Android lint and API26/35/36 emulator runs, TalkBack and accessibility testing, OEM READ_CONTACTS revocation/cancellation behavior, screenshot/privacy review, real physical Android devices, original source consumer reconciliation and release signing/rollback. Any future CardDAV integration requires explicit Identity authorization, GoreeShield consent and Wardveil enforcement. The standalone app does not silently enable DAV, Mesh or network sync.

**Rollback:** Do not delete original `android-defaults/contacts` while compatibility gates remain open. The destination feature branch can be closed without modifying the legacy source. Once a reviewed standalone main build is verified, follow a separately reviewed source-repository deprecation/redirect change and maintain a clear history link.
