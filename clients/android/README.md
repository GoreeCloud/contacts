# GoreeCloud Contacts Android Client

This directory is the dedicated native Android application line for GoreeCloud Contacts.

## Architecture authority

Radicale/CardDAV remains the sole authoritative contact store. The Android client must not create a competing application-only authoritative contact database. Any future local persistence is a bounded offline/cache representation with explicit synchronization and conflict handling.

Android's Contacts Provider is an optional device-integration bridge, not the GoreeCloud source of truth. Provider read/write access must be separately permissioned, purpose-bound, user-controlled, and independently accepted before it is enabled.

## Current Development foundation

The current shell provides:

- Kotlin/Jetpack Compose application module targeting SDK 36 with minimum SDK 29 and Java 17.
- A launchable native Contacts surface.
- Repository-local GLAZE UI V1.4 / `1.4.0` adoption boundary pinned to the current Stable source authority while downstream conformance remains `ADOPTION_IN_PROGRESS`.
- Explicit runtime capability state for GoreeCloud Identity, CardDAV read/write, offline cache, background synchronization, and the Android Contacts Provider bridge.
- A pure Kotlin read-contract model for the existing session-bound `/api/carddav/address-books`, `/api/carddav/contacts`, and `/api/carddav/contact` endpoints.
- Fail-closed CardDAV href construction: only bounded, canonical server-relative hrefs are accepted before query encoding; absolute/scheme-relative authorities and control-bearing values are rejected.
- Native Identity/session exchange and network transport remain blocked. The manifest still requests neither `INTERNET` nor Contacts Provider permissions.
- Android backup disabled.
- Unit coverage proving unavailable runtime capability is not advertised as accepted and the source-ready read contract cannot broaden origin/identity authority.
- Gradle caching, parallel execution, and incremental Kotlin compilation.

A source-ready endpoint contract is not a live CardDAV connection. The Android client does not copy browser cookies, embed reusable service credentials, invent bearer tokens, or contact Radicale directly.

## Next milestones

Advance each capability independently and preserve truthful state:

1. Define and accept first-party GoreeCloud Identity/session exchange for native Contacts without reusable application-wide credentials.
2. Add a bounded same-origin transport adapter and exercise read-only address-book discovery/contact listing against non-production Development data.
3. Add authorized contact detail retrieval with data-minimized error handling.
4. Add ETag/precondition-aware create/edit/delete with explicit conflict surfaces.
5. Add protected bounded offline cache and deterministic reconciliation.
6. Add WorkManager/background synchronization with power/network constraints.
7. Add the optional Android Contacts Provider bridge with explicit permission and user controls.
8. Complete repository-local GLAZE UI V1.4 application acceptance, accessibility, form-factor, and representative-device gates; human/manual V1.4.1 checks remain separate.
9. Complete independent Privacy Shield, Wardveil Security, Everkeep, Manager, Mesh, and Identity acceptance where applicable.
10. Complete APK/AAB signing, SBOM/provenance, rollback/recovery evidence, Release Candidate, production, and Stable gates.

No source-local safeguard or successful CI run grants production, platform-system, or Stable acceptance by itself.
