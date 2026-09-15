# GoreeCloud Contacts Android Client

This directory is the dedicated native Android application line for GoreeCloud Contacts.

## Architecture authority

Radicale/CardDAV remains the sole authoritative contact store. The Android client must not create a competing application-only authoritative contact database. Any future local persistence is a bounded offline/cache representation with explicit synchronization and conflict handling.

Android's Contacts Provider is an optional device-integration bridge, not the GoreeCloud source of truth. Provider read/write access must be separately permissioned, purpose-bound, user-controlled, and independently accepted before it is enabled.

## Current Development foundation

The current shell provides:

- Kotlin/Jetpack Compose application module targeting SDK 36 with minimum SDK 29 and Java 17.
- A launchable native Contacts surface.
- Repository-local GLAZE UI V1.4.1 / `1.4.1` adoption boundary pinned to Stable authority `4fab9da0fad2e5c974e0e66ec88632c61745751c`, with V1.4.0 retained as the immediate rollback baseline and downstream conformance still `ADOPTION_IN_PROGRESS`.
- Explicit runtime capability state for GoreeCloud Identity, CardDAV read/write, offline cache, background synchronization, and the Android Contacts Provider bridge.
- A pure Kotlin read-contract model for the existing session-bound `/api/carddav/address-books`, `/api/carddav/contacts`, and `/api/carddav/contact` endpoints.
- Fail-closed CardDAV href construction: only bounded, canonical server-relative hrefs are accepted before query encoding; absolute/scheme-relative authorities and control-bearing values are rejected.
- A source-ready, transport-neutral **CardDAV response acceptance** contract for the current backend `AddressBook`, `ContactSummary`, and `ContactDetail` shapes.
- Exact response field allowlists for address-book, summary, detail, structured-name, and postal-address records so a future decoder can reject unknown authority/credential fields instead of silently trusting them.
- Response validation that preserves opaque server-relative href identity, rejects duplicate resource hrefs, requires contact detail to match the requested href, bounds collection/text sizes, and rejects malformed/control-bearing presentation values.
- Native Identity/session exchange and network transport remain blocked. The manifest still requests neither `INTERNET` nor Contacts Provider permissions.
- Android backup disabled.
- Unit coverage proving unavailable runtime capability is not advertised as accepted and source-ready request/response contracts cannot broaden origin/identity authority.
- Gradle caching, parallel execution, and incremental Kotlin compilation.

A source-ready endpoint or response contract is not a live CardDAV connection. The Android client has **no network authority** in this tranche: it does not copy browser cookies, embed reusable service credentials, invent bearer tokens, contact Radicale directly, or parse remote JSON.

Shared GLAZE UI V1.4.1 qualification is not Contacts-local acceptance. Repository-local optical behavior, accessibility, representative-device behavior, performance, Human Visual Excellence, rollback, and release evidence remain separate fail-closed gates.

## CardDAV response acceptance boundary

`CardDavResponseContract` models the backend's current read-only response shapes without importing transport or authentication behavior.

The accepted address-book record contains only:

- `href`; and
- `display_name`.

The accepted contact summary fields are:

- `href`, `etag`, and `uid`;
- `formatted_name`;
- `emails` and `phones`;
- `organization` and `title`;
- `categories`;
- `favorite`; and
- `has_photo`.

Contact detail adds only the current backend fields:

- `structured_name`;
- `addresses`;
- `birthday`;
- `websites`;
- `note`; and
- `photo`.

The policy rejects absolute or scheme-relative hrefs, trim-dependent/control-bearing hrefs, duplicate address-book/contact identities, contact-detail href mismatch, oversized collections, malformed text, and unknown fields identified by the exact allowlists. It does not normalize a different host into an accepted resource identity.

This acceptance layer intentionally does **not** verify an Identity session, authenticate CardDAV, establish transport security, cache contacts, write contacts, access Android Contacts Provider, or synchronize anything. A successful decision means only that already-decoded Development data conforms to the current minimized consumer shape.

## GoreeCloud Identity boundary

The source-ready native Identity proof contract remains separate from runtime authority. Exact principal/audience/lifetime metadata can be evaluated locally, but a deployed native Identity application registration, credential exchange, protected session runtime, and accepted CardDAV transport do not yet exist.

Neither `CardDavReadContractState.SOURCE_READY` nor a successful `CardDavResponseDecision.Accepted` result grants authentication or contact authorization.

## Next milestones

Advance each capability independently and preserve truthful state:

1. Define and accept first-party GoreeCloud Identity/session exchange for native Contacts without reusable application-wide credentials.
2. Add an exact-field decoder for the accepted address-book/summary/detail response shapes; reject unknown fields before `CardDavResponseContract` evaluation.
3. Add a bounded same-origin authenticated transport adapter and exercise read-only address-book discovery/contact listing against non-production Development data.
4. Add authorized contact detail retrieval with data-minimized error handling and feed only accepted responses into UI state.
5. Add ETag/precondition-aware create/edit/delete with explicit conflict surfaces.
6. Add protected bounded offline cache and deterministic reconciliation.
7. Add WorkManager/background synchronization with power/network constraints.
8. Add the optional Android Contacts Provider bridge with explicit permission and user controls.
9. Complete repository-local GLAZE UI V1.4.1 rendered, accessibility, form-factor, representative-device, performance, Human Visual Excellence, and rollback acceptance.
10. Complete independent Privacy Shield, Wardveil Security, Everkeep, Manager, Mesh, Identity, and Sync acceptance where applicable.
11. Complete APK/AAB signing, SBOM/provenance, rollback/recovery evidence, Release Candidate, production, and Stable gates.

No source-local safeguard or successful CI run grants production, platform-system, or Stable acceptance by itself.
