# GoreeCloud Contacts

GoreeCloud Contacts is my private, self-hosted personal and family contact-management application. I am building it as a GoreeCloud-native contacts experience around CardDAV, with first-party web/server and native Android clients sharing Radicale as the authoritative contact service.

## Project Status

**Status:** Active development — Milestone 4 Phase 4B VCF import/export implementation and validation

Milestones 1 and 2 provide Radicale address-book discovery, contact listing and search, and guarded create, update, and delete operations with ETag-based conflict protection.

Milestone 3 adds per-user Radicale authentication, opaque server-side sessions, strict application-level address-book isolation, logout/session-expiration behavior, and live negative two-user authorization validation.

Milestone 4 Phase 4A expands the contact model with structured names, organization/title, addresses, birthdays, websites, notes, categories, favorites, HTTP(S) photo-reference awareness, full contact-detail retrieval, and expanded browser workflows. Automated validation, isolated live read/detail validation, the full synthetic create/detail/update/stale-ETag/delete sequence, and browser create/favorite/edit/unfavorite/delete validation have passed. The local write safety gate was restored to `CARDDAV_WRITE_ENABLED=false` after validation. A browser error-presentation defect discovered during validation was corrected so structured FastAPI validation details are rendered as readable messages instead of `[object Object]`. Development and validation continue to use isolated non-production identities and synthetic contact data; production family contact data is not yet approved for use.

## Role

I will use GoreeCloud Contacts to provide modern first-party web and native Android experiences for managing personal and family contacts while preserving CardDAV as the portable authoritative synchronization protocol.

## Architecture

The application model is:

```text
Approved web client                 GoreeCloud Contacts Android
        |                                      |
        | HTTPS / opaque session               | future accepted native Identity + bounded transport
        v                                      v
GoreeCloud Contacts web/server          GoreeCloud Contacts service contracts
        |                                      |
        +--------------- CardDAV --------------+
                               |
                               v
                            Radicale
                               |
                               | optional CardDAV compatibility
                               v
                    External CardDAV clients (for example DAVx5)
                               |
                               | optional device integration
                               v
                    Android Contacts Provider
```

Radicale remains the authoritative CardDAV service. GoreeCloud Contacts does not create a competing contact database for ordinary contact data.

The first-party native Android line is the planned GoreeCloud mobile client. It targets GoreeCloud-owned service contracts and does not treat DAVx5 or the Android Contacts Provider as its source of truth. Any future Contacts Provider bridge must remain optional, permission-bound, user-controlled, and independently accepted.

DAVx5 remains a compatible external CardDAV client for users who choose it; it is not the architecture or implementation dependency of the first-party GoreeCloud Contacts Android application.

Each web user currently authenticates with an approved Radicale/CardDAV identity. The backend performs CardDAV operations as that user and independently restricts requested address books and contact resources to collections discovered for the authenticated session. The native Android line separately defines a fail-closed GoreeCloud Identity/session acceptance prerequisite and does not reuse browser cookies or embed reusable CardDAV credentials.

## Technology Direction

- Web frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- Native Android: Kotlin + Jetpack Compose
- Contact protocol: CardDAV
- Contact format: vCard
- Authoritative contact service: Radicale
- First-party Android synchronization direction: GoreeCloud Contacts native client with bounded GoreeCloud Identity, CardDAV service-contract transport, offline reconciliation, and optional Android Contacts Provider integration
- External Android CardDAV compatibility: DAVx5 and other standards-compatible clients remain optional interoperability paths
- Current web authentication: Radicale-backed per-user sign-in
- Current web sessions: opaque server-side sessions
- Native Android authentication direction: first-party GoreeCloud Identity/session exchange, independently accepted before network transport activates
- Deployment: Docker and Docker Compose
- Reverse proxy: Caddy
- Development platform: GitHub

Technology selections remain subject to implementation and production-readiness validation.

## Repository Structure

```text
goreecloud-contacts/
├── frontend/
├── backend/
├── clients/
│   └── android/
├── docker/
├── tests/
├── docs/
│   ├── architecture.md
│   ├── carddav.md
│   ├── development.md
│   ├── security.md
│   ├── milestone-1-carddav-poc.md
│   ├── milestone-2-carddav-writes.md
│   ├── milestone-3-authentication-isolation.md
│   ├── milestone-4-expanded-contact-model.md
│   └── milestone-4-vcf-import-export.md
├── .github/workflows/ci.yml
├── .github/workflows/android-client.yml
├── .github/workflows/platform-contract.yml
├── goreecloud.platform.yaml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Development Milestones

### Milestone 1 — Read-Only CardDAV Proof of Concept — Complete

- Implemented the React/TypeScript frontend and FastAPI backend foundation.
- Authenticated to an isolated Radicale test account through protected local configuration.
- Discovered CardDAV principals, address-book homes, and address books.
- Retrieved synthetic contacts and preserved resource hrefs and ETags.
- Parsed common vCard fields.
- Rendered a responsive browser contact list with local search.
- Added dependency locking and GitHub Actions continuous integration.
- Validated the complete browser-to-Radicale read path without production family contact data.

### Milestone 2 — Conditional CardDAV Writes — Complete

- Added guarded create, update, and delete operations through the GoreeCloud Contacts backend.
- Preserved ETag-based conditional update/delete behavior to prevent silent overwrite of concurrent changes.
- Kept write operations disabled by default outside explicit isolated validation.

### Milestone 3 — Authentication and Address-Book Isolation — Complete Development Validation

- Added Radicale-backed per-user authentication and opaque server-side application sessions.
- Restricted address-book and contact access to collections discovered for the signed-in session.
- Added logout/session-expiration behavior and live two-user negative authorization validation.

### Milestone 4 — Expanded Contact Model and Portability — Active Development

- Phase 4A expanded structured contact fields, detail retrieval, favorites, and browser management workflows.
- Phase 4B is implementing and validating VCF import/export and broader portability behavior.

## Native Android Development Line

The dedicated `clients/android/` application is being developed independently from the current browser milestones. It already establishes the first-party Kotlin/Compose shell, current Stable GLAZE UI V1.4 source boundary, bounded CardDAV read-contract modeling, and a fail-closed GoreeCloud Identity acceptance-proof contract.

The native line still has no accepted Identity runtime, network transport, offline cache, background synchronization, contact mutation authority, or Android Contacts Provider bridge. Those capabilities must be implemented and validated independently before they are represented as available.

Successful source/build CI does not make the native client production-approved, Release Candidate, or Stable.
