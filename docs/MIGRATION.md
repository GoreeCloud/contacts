# GoreeCloud Contacts standalone repository migration

**Status (November 11, 2026):** Standalone Android Contacts source migrated and merged into public `GoreeCloud/contacts` `main` at commit `51d5dd58517a3f544545c573b797eaf0c3cf2ae8`. Its source build and emulator CI passed both before and after merge. The application remains a **0.1.0 development preview**, not a signed release, deployed service, default Contacts-handler replacement or real-device certification.

## Verified source and history

- Original repository: https://github.com/GoreeCloud/android-defaults
- Source tree: `contacts/` (an independently built Android Kotlin project).
- Exact source monorepo main commit at extraction: `c7f65cdd55e7fa742743853244a8959e0d814ac4` (November 10, 2026).
- Source subtree-filtered Git tip: `3f160f287ccfa4fac01890270bac0fa1842a263e`, comprising **33 Contacts-specific commits**, reachable from the standalone migration merge.
- Destination repository: https://github.com/GoreeCloud/contacts; prior placeholder main commit `c52f95561f840ef77070674ff6a4cd99a025c3d4` is preserved in the merge ancestry.
- Retained original license: MIT, copyright 2026 GoreeCloud, with no change to Kotlin app package `com.goreecloud.contacts`, min SDK 26, target/compile SDK 35, or version `0.1.0-dev`.

## Verified development migration acceptance

- [Migration PR #1](https://github.com/GoreeCloud/contacts/pull/1) merged using the **merge** strategy, preserving the original repository's 33 Contacts-specific commits (subtree history tip `3f160f287ccfa4fac01890270bac0fa1842a263e`) plus the prior destination placeholder-main ancestry.
- [Exact-head migration CI](https://github.com/GoreeCloud/contacts/actions/runs/43057383247) succeeded across four jobs: Android Contacts source privacy, JVM tests, lint and APK assembly plus isolated Android API26/35/36 emulator UI/instrumentation checks.
- Independent [post-merge main CI](https://github.com/GoreeCloud/contacts/actions/runs/43058845016) also succeeded across all four jobs at merge commit `51d5dd58517a3f544545c573b797eaf0c3cf2ae8`.
- Compared immutable Git blob IDs for the original 46 Contacts tracked files against migrated target main content: **43 files byte-identical**; the three adaptations are `README.md`, `ci/capture-emulator.sh`, `ci/test-fresh-hierarchy.sh` for standalone paths and ownership. Six root support files were added (workflow, license, ignore rules, safe emulator helper/tests and this record).
- Verified GitHub public owner and default branch, unchanged `com.goreecloud.contacts` application ID, `READ_CONTACTS`-only manifest permission, local offline ADB emulator guard tests and MIT license readback. Source `android-defaults` remains unchanged at original extraction commit for rollback.

## Source-only adaptations

The standalone repository lifts the former `contacts/` Gradle tree to the root and migrates its Contacts-only CI workflow. The monorepo's two shared **synthetic-only ADB emulator safety scripts** are retained in `ci/`, with Dialer-specific test cases removed. Screenshot checks remain fail-closed: explicit emulator serial, qemu identity and exact API checks must succeed before any ADB install/clear or screenshot operation. The CI workflow must run on every relevant branch and PR revision, not rely on the old monorepo path filter.

## Release and security boundaries

The source directory contains no INTERNET or WRITE_CONTACTS permission. It uses Android permission-gated on-device Contacts Provider reads, user-controlled share/export/document-picker flows and private app-local favorites. Existing unit and emulator tests passed independently after path extraction as documented above; product release and physical-device acceptance remain separate. No migration of device contact data, Android preferences, encryption keys, account state, release signing, customer data or production endpoints is performed here. The original app ID is retained intentionally to protect future upgrade continuity, but that does **not** prove install/upgrade behavior; signed APK compatibility and device migration need independent validation.

**Remaining acceptance:** TalkBack and accessibility testing, OEM READ_CONTACTS revocation/cancellation behavior, independent screenshot/privacy review, real physical Android devices, original source consumer reconciliation and release signing/install/upgrade/rollback. Canonical Drive repository index reconciliation is tracked in [Contacts issue #2](https://github.com/GoreeCloud/contacts/issues/2). Any future CardDAV integration requires explicit Identity authorization, GoreeShield consent and Wardveil enforcement. The standalone app does not silently enable DAV, Mesh or network sync.

**Rollback and source cutover:** Keep original `android-defaults/contacts` intact while compatibility and release gates remain open; do not force-push rewritten history or remove legacy CI without a consumer audit. A code rollback of the migrated public `main` now requires a separately reviewed Git revert or forward-fix, not merely closing a branch. The documentation-only [android-defaults ownership PR #64](https://github.com/GoreeCloud/android-defaults/pull/64) labels the prior module as a compatibility snapshot and awaits its own CI acceptance. Neither Git migration nor this document transfers a user's Android contact data.
