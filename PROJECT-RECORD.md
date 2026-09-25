# GoreeCloud Contacts — Project Record

**Repository:** `GoreeCloud/contacts`  
**Lifecycle:** Development  
**Record purpose:** Significant project history, architecture/governance transitions, candidate evidence, licensing history, and project-specification migration provenance  
**Migration baseline:** `85be95c07179224933548e3605b1d727cb3f4d5b`  
**Canonical authority:** This file is the repository-local project record once accepted on the default branch.

## Accepted Development foundation

Authoritative `main` already contains repository-native `IMPLEMENTED-FEATURES.md`, `PLANNED-FEATURES.md`, and `CHANGELOGS.md`.

Those records establish accepted Development capabilities and preserve the boundary between merged state and extensive unmerged Draft work. The mapped legacy Contacts Drive feature roadmap has already been retired and independently verified absent after the separate feature/changelog migration.

## Licensing boundary at migration

The Drive project specification records a planned/prospective transition to AGPL-3.0-only and explicitly notes continuity for previously distributed MIT copies.

At this project-specification migration baseline, live GitHub still reports MIT and authoritative `main` contains the MIT license. Therefore:
- MIT is the current verified default-branch license state;
- prospective AGPL language remains planned/candidate history until accepted repository evidence changes the license; and
- this documentation migration does not itself perform a license change.

## Unmerged Development candidates

Live GitHub contains extensive open Draft/candidate work, including the Android Contacts stack, Glaze migrations, Platform Contract migrations, browser/security hardening, public-profile/group work, and other production-readiness changes.

Those pull requests remain candidate evidence only until accepted, merged, and verified on the authoritative default branch.

## 2026-09-22 — Repository-native feature/changelog authority

PR #42 established repository-native feature/changelog records. Subsequent main-branch documentation records verified the mapped Contacts Drive feature-roadmap retirement. That migration is separate from this project specification/project record migration and is not reversed here.

## 2026-09-24 — Project specification/project record migration candidate

This migration:
- creates root `PROJECT-SPECIFICATIONS.md`;
- creates root `PROJECT-RECORD.md`;
- reconciles the active Drive project specification with current repository state;
- preserves the full former Drive source below as source-era history/candidate evidence;
- links the canonical project records from README; and
- leaves the already-established repository-native feature/changelog records intact.

**Drive source:** Project Specification — Contacts.docx  
**Drive file ID:** `1LSuIFz3-bEyfDaTa-Mt2RNqUU7pesy7C`  
**Drive deletion status:** Blocked until accepted/default-branch readback and all migration verification gates pass.

# Imported Drive Source Record

The complete Drive project specification is retained below for traceability and content preservation. Historical or candidate status claims inside this imported section do not override current verified repository state.

---

GoreeCloud — Project Specification — Contacts
Document Metadata
Document Owner: LaDamian Goree
Version: v0.11
Status: Draft
Created: Aug 13, 2026
Classification: Internal
Document Type: Software Project Specification and Implementation Blueprint
Project Name: GoreeCloud Contacts
Project Status: Active Development — the current stacked line extends through Draft PR #34. PR #31 reconciled the required GLAZE UI target to current Stable V1.3 / 1.3.0 while preserving the implemented Contacts runtime/source mapping at V1.1 / 1.1.0 and `applicable-migration-required`. Draft PR #34 stages a bounded, non-activating V1.3 foundation at exact Glaze integration anchor `fc7cc91d2eace8da2371371c2855c24cbcb326a1`; runtime/source staging head `17369a83a586b71783c43b809550800f369ffbe8` passed Platform Contract run `34542118740` and Continuous Integration run `34542118164`. Repository feature-roadmap reconciliation later advanced the final Draft PR #34 head to `2c62ac7ba149060ef2e34b74bd014850ca9338b7`, which passed Platform Contract run `34547018199` and Continuous Integration run `34547017894`. The live browser root remains V1.1 and the V1.3 foundation remains non-activating. Representative-device/browser, deliberate V1.3 root migration and whole-application acceptance, Integral Platform System integration, recovery/rollback, signing/provenance, Release Candidate, Stable, production deployment, production-family data use, Android APK, and Debian-native package gates remain pending or unapproved.
Repository: GoreeCloud/goreecloud-contacts
Development Model: Original GoreeCloud-owned software development
Approved License: GNU Affero General Public License v3.0 only (AGPL-3.0-only) for current and future GoreeCloud-owned source, to be applied prospectively through synchronized main and active release-candidate licensing integrations.
Third-Party Licensing: Radicale, dependencies, and separately licensed services/components retain their applicable licenses.
Prior-License Continuity: Copies previously distributed or obtained under the MIT License retain those MIT permissions; the prospective AGPL-3.0-only integrations do not revoke, narrow, or retroactively alter those grants.
Current Development Model: Local frontend and backend on personal-laptop-ideapad3-01 with isolated Radicale/CardDAV test identities and synthetic data
Current CardDAV Service: Radicale 3.7.3
Historical Development CardDAV Address: https://calendar.goreecloud.com
Definitive CardDAV/CalDAV Service Address: https://dav.goreecloud.com
Current Verified CardDAV Runtime Address: https://dav.goreecloud.com
Intended Product Address Referenced by Development Records: https://contacts.goreecloud.com — not deployed or published
Long-Term Production Placement: Not yet approved
Authoritative Contact Store: Radicale/CardDAV
Authoritative Record: Yes
Related Records
GoreeCloud — Change Log — Contacts
GoreeCloud — Change Log — Radicale
GoreeCloud — Architecture — Contacts, Calendar, and DAV
GoreeCloud — Plan — Native Applications
GoreeCloud — Strategy — Native Software Development and Original Applications
GoreeCloud — Standard — Application Branding and User Interface Design
GoreeCloud — Standard — Glaze UI Design Language
GoreeCloud — Standard — Privacy by Default
GoreeCloud — Standard — Sensitive Information Separation
GoreeCloud — Requirement — Open-Source Software
GoreeCloud — Requirement — Role and Purpose Documentation
GoreeCloud — Policy — Backup, Restore, and Recovery
GoreeCloud — Standard — Code Structure and Documentation
1. Project Definition
I am developing GoreeCloud Contacts as a GoreeCloud-native, privacy-first, self-hosted contact-management application and Google Contacts alternative.
GoreeCloud Contacts provides a browser-based GoreeCloud interface while preserving Radicale/CardDAV as the authoritative contact store. I will not create a second authoritative contacts database merely to support the application interface.
This specification controls project-specific scope. Change logs remain the chronological history of completed work, Radicale records control the current CardDAV service state, and current repository/runtime inspection controls details that may have changed after this document was last updated.
2. Role
Role: Private Multi-User Contact-Management Interface over Standards-Based CardDAV
I will use GoreeCloud Contacts to let authorized users discover, search, view, create, update, and delete contacts through a GoreeCloud-controlled interface while maintaining compatibility with standards-based CardDAV clients such as DAVx5.
3. Purpose
My objectives are to provide a contact experience that remains:
Private by default.
Self-hosted.
Multi-user.
Individually attributable.
Standards-based.
Portable.
Recoverable.
Protected against stale-write conflicts.
Usable from desktop and mobile browsers.
Independent from a proprietary contact provider.
Compatible with direct CardDAV synchronization where appropriate.
4. Authoritative Data Model
Radicale/CardDAV remains the authoritative store for contact data.
The application does not maintain a separate PostgreSQL or other second authoritative contact database. The browser communicates with the GoreeCloud Contacts backend, and the backend performs CardDAV operations server-side against Radicale through the canonical DAV service at https://dav.goreecloud.com.
DAVx5 and other approved CardDAV clients may continue to communicate directly with Radicale through https://dav.goreecloud.com. GoreeCloud Contacts must coexist with those clients rather than requiring migration into a proprietary application-only data format.
5. Current Application Architecture
The validated development architecture is:
Browser
→ React / TypeScript / Vite frontend
→ FastAPI backend
→ server-side HTTPX CardDAV adapter
→ https://dav.goreecloud.com
→ Radicale
CardDAV protocol work remains server-side so reusable credentials are not exposed to browser JavaScript, CORS complexity is reduced, ETag behavior is centralized, and protocol behavior remains testable.
This diagram describes the validated development architecture. It does not by itself approve a future production host, container topology, reverse-proxy route, session store, secret mount, DNS record, or network policy.
6. Authentication and Multi-User Isolation
Milestone 3 replaced the earlier single application-wide CardDAV identity with per-user Radicale authentication and session-bound CardDAV access.
Current development behavior includes:
POST /api/auth/login for Radicale-backed sign-in.
GET /api/auth/session for session state.
POST /api/auth/logout for explicit logout.
Opaque cryptographically random server-side session tokens.
HttpOnly session cookies.
SameSite=Strict cookies.
Per-session CardDAV clients created from the authenticated user's credentials.
Application-level authorization that restricts a user to address books discovered for that authenticated identity.
Path normalization and same-origin CardDAV target enforcement before protected resource access.
Live validation proved that a second isolated Radicale identity could authenticate independently, could not discover the primary test identity's address book, and received HTTP 403 when explicitly attempting to select the other user's collection.
7. Current Session Model and Production Validation Boundary
Milestone 3 originally used a process-local in-memory session store. The current consolidated release-candidate source has advanced beyond that historical model and supports encrypted shared SQLite-backed sessions for the production-shaped multi-worker runtime.
The production-shaped runtime supplies session encryption key material separately from the image, keeps the session database in the explicitly writable application-data path, and runs multiple backend workers against the shared session store. CI validates this source/runtime contract, but target-environment backup, restore, key rotation, rollback, and worker-behavior evidence remain required before production approval.
The normal development session lifetime remains separately configurable. Session persistence and encryption are now implemented at the release-candidate source level; production deployment must still validate the selected runtime's actual storage persistence, permissions, recovery, encryption-key lifecycle, and failure behavior.
8. Contact Read and Search Behavior
The application currently supports CardDAV principal discovery, address-book-home discovery, address-book discovery, multiget contact retrieval, vCard parsing, ETag capture, contact listing, and browser search.
Protected CardDAV address-book and contact routes require an authenticated application session under the Milestone 3 model.
9. Conditional Write Model
GoreeCloud Contacts uses conditional CardDAV operations to prevent stale browser state from silently overwriting newer data.
Create operations use If-None-Match: *.
Update operations require the current ETag and use If-Match.
Delete operations require the current ETag and use If-Match.
CardDAV HTTP 412 precondition failures are surfaced by the application as HTTP 409 conflicts rather than being retried or forced.
Live isolated validation proved create, update, stale-ETag rejection, and delete behavior while preserving the contact UID across an update.
10. Write Safety Gate
CARDDAV_WRITE_ENABLED remains an explicit application-side safety gate and defaults to false.
After write validation, the protected local development environment was restored to CARDDAV_WRITE_ENABLED=false. Ordinary development and authentication-isolation testing therefore return to read-only safety mode unless writes are deliberately enabled for an approved isolated test.
I will not use this safety gate as a substitute for authorization. A production-capable write path must require both the correct authenticated user permissions and the approved application write configuration.
11. Current Contact Field Coverage
The validated Milestone 4 contact model retains the original Milestone 2 fields and now supports a substantially broader structured contact model, including:
UID.
Formatted name.
Multiple email addresses.
Multiple phone numbers.
Phase 4A additionally implements structured names, organization and title, postal addresses, birthday, websites, notes, categories, favorites, HTTP(S) photo-reference awareness, full contact-detail retrieval, broader search, and expanded browser create/view/edit/favorite workflows. Phase 4B adds raw single-contact and full-address-book VCF export plus vCard 3.0/4.0 preview/import so portability-sensitive source properties can be preserved without rebuilding every record through only the understood structured fields. Embedded data-image PHOTO content is not claimed as lossless in the current Radicale/vobject path; current photo writes are limited to HTTP(S) references.
12. Development and Test Data Boundary
All live Milestone 1 through Milestone 4 Phase 4B validation used isolated non-production Radicale identities and synthetic contact data.
The primary test identity is goreecloud-contacts-test. The negative authorization identity is goreecloud-contacts-isolation-test. The retained synthetic fixture in the primary test address book is Jordan Example.
Production family contacts remain unused and are not yet approved for application testing. Test identities and synthetic fixtures must not be presented as production family accounts or data.
Reusable test passwords remain outside ordinary documentation and source control.
13. Current Repository and Validation State
The public source repository is GoreeCloud/goreecloud-contacts.
Milestone 3 authentication and multi-user isolation were squash-merged to main at 062b8677259c4ae29d87e7e8af6011ed267a57b6. Milestone 4 Phase 4A was later squash-merged as 1e2675390e06e9485bf664b53b0552c2e4575cd4, and Phase 4B was squash-merged as eead31afb86894fcf5ed44c32ba7cbd8c5fa30a0.
Exact-final-head and post-merge GitHub Actions validation passed for Milestone 3. Phase 4A also passed exact-final-head CI before merge. Phase 4B passed 27 local backend tests, frontend lint and production build, implementation-head CI, isolated live read/write acceptance, and final exact-head GitHub Actions run #38 on 9bc0bd25db25cc7bbe8cd093e9f5b8b522aab69e before merge. The validated pipeline covers backend tests plus frontend dependency installation, lint, and production build.
Current validation evidence does not mean the application is production deployed.
14. Completed Milestones — Historical Implementation Record
Milestone 1 — Read Path — Completed
Established repository foundation, React/TypeScript/Vite frontend, FastAPI backend, server-side CardDAV integration, discovery, contact listing, ETag capture, browser search, dependency locking, and CI validation.
Milestone 2 — Conditional CardDAV Writes — Completed
Added gated create, update, and delete support using conditional CardDAV headers; validated stale-ETag conflict protection; completed browser write acceptance with synthetic data; restored write-disabled safety state afterward.
Milestone 3 — Authentication and Multi-User Isolation — Completed
Added per-user Radicale sign-in, opaque server-side sessions, logout and expiration handling, protected routes, per-user address-book authorization, live two-user negative isolation testing, browser acceptance, and CI validation.
Milestone 4 Phase 4A — Expanded Contact Model — Completed
Expanded the structured contact model, detail API, categories/favorites, browser workflows, and HTTP(S) photo-reference support while preserving per-user CardDAV authorization, UID handling, and ETag conflict protection. Isolated synthetic API/browser acceptance and exact-head CI passed; PR #6 was squash-merged as 1e2675390e06e9485bf664b53b0552c2e4575cd4.
Milestone 4 Phase 4B — VCF Import and Export — Completed
Added raw single-contact and full-address-book VCF export, vCard 3.0/4.0 preview/import, explicit destination and record selection, missing-UID generation, raw unknown-property preservation where possible, and conflict-safe If-None-Match: * creates. Live validation proved the tested source UID and X-GOREECLOUD-TEST extension survived the Radicale round trip; cleanup restored the address book to Jordan Example only and the write gate to false. PR #7 was squash-merged as eead31afb86894fcf5ed44c32ba7cbd8c5fa30a0.
These historical milestones are retained because they explain how the current application state was reached. They must not be rewritten as if they were all implemented at project creation.
15. Next Development Direction
Milestone 4 Phase 4A and Phase 4B are merged historical milestones. Phase 4C duplicate detection/user-reviewed merge and Phase 4D Glaze UI/readiness source are present in the consolidated active development stack, but required live, representative-device, current-Glaze, platform-system, and production acceptance remain incomplete.
Current development direction is to preserve the CardDAV single-source-of-truth design, per-user isolation, conditional-write protections, raw portability behavior, and DAVx5 interoperability while completing the current Platform Contract v0.2 and GLAZE UI V1.3 / 1.3.0 migration. The active browser runtime/source mapping remains V1.1 / 1.1.0 until a deliberate exact-revision V1.3 root switch and fresh application-specific acceptance are completed. Staged source presence must not be mistaken for completed application acceptance or production approval.
The exact Phase 4C/4D and later implementation state must be taken from the current repository and newer change records before work is performed. Duplicate detection/merge must remain user-reviewed and conflict-safe; examples in this specification are not an authorization to mutate production contact data.
16. Production Readiness Gates
GoreeCloud Contacts is not approved for production deployment or production-family contact use yet.
Before production approval, I must validate at least the following areas as applicable to the selected deployment architecture:
Production session-storage behavior and worker compatibility.
SESSION_COOKIE_SECURE under HTTPS.
Final CSRF protection decision and validation, including token or Origin/Referer enforcement as appropriate.
Final multi-user authentication and authorization behavior against production-representative identities.
Backup and restore of the application configuration and the authoritative Radicale contact data.
Recovery and rollback procedures.
Private DNS, Caddy, NetBird, and firewall/publication boundaries if contacts.goreecloud.com is deployed.
Monitoring and health visibility.
Secret and credential storage, permissions, rotation, and recovery.
Upgrade and rollback validation.
Production-representative browser acceptance.
DAVx5 and other approved client coexistence, including conflict behavior where applicable.
Data export and portability validation.
17. DNS and Service Identity Boundary
Historical GoreeCloud Contacts development validation used https://calendar.goreecloud.com as the Radicale/CardDAV endpoint. That remains historical implementation evidence, not the definitive service identity.
The definitive architecture assigns Radicale CardDAV/CalDAV to https://dav.goreecloud.com and reserves https://calendar.goreecloud.com for the user-facing GoreeCloud Calendar application. The runtime migration is now operationally verified: private DNS resolves dav.goreecloud.com through the GoreeCloud NetBird path, Caddy serves Radicale through dav.goreecloud.com with a valid TLS certificate, authenticated PROPFIND returns HTTP 207, the local GoreeCloud Contacts runtime uses CARDDAV_BASE_URL=https://dav.goreecloud.com and successfully authenticates through Radicale, and Uptime Kuma monitor ID 20 now monitors https://dav.goreecloud.com/. Historical calendar.goreecloud.com references remain evidence of the earlier development state and must not be interpreted as the current DAV endpoint.
The definitive GoreeCloud Contacts application hostname is https://contacts.goreecloud.com. Its runtime deployment and publication state must be verified independently from current operational records; the architecture decision does not by itself prove production publication.
18. Privacy and Sensitive Information
I will not store reusable CardDAV passwords, session tokens, private keys, API tokens, or other credentials in ordinary project documentation or source control.
The application must minimize exposure of contact data and credentials in logs, errors, browser state, exported diagnostics, and monitoring output.
Passwords must not be returned in authentication responses or preserved in ordinary object representations.
19. Backup, Recovery, and Portability
A successful GoreeCloud Contacts deployment must preserve the ability to recover contacts independently of the application interface.
Because Radicale/CardDAV is authoritative, recovery planning must protect the Radicale contact collections and configuration required to restore standards-based access. GoreeCloud Contacts configuration and any production session or application state must be protected separately according to its actual recovery importance.
The application must not create a lock-in condition where a contact can be used only through GoreeCloud Contacts.
20. User Interface Direction
GoreeCloud Contacts must migrate to and be accepted against current Stable GLAZE UI V1.3 / 1.3.0 for its browser/installable client. The active browser runtime/source mapping remains V1.1 / 1.1.0 while a bounded V1.3 foundation is staged for controlled migration; neither that staging nor the earlier Glaze UI 1.4 form-factor implementation and PR #25 acceptance establish current whole-application conformance. The visual direction remains Google Contacts-inspired while remaining a distinct GoreeCloud application.
The interface must use purpose-built Mobile, Tablet, Desktop, and Wide Desktop compositions rather than scaling one generic layout across device classes. Mobile/Compact is touch- and reachability-first with stacked task flow, safe-area-aware lower actions, horizontal address-book selection, and contact cards instead of a compressed desktop table. Tablet/Medium uses persistent touch navigation and a pane-aware expanded contact-card canvas. Desktop/Expanded restores a persistent productivity sidebar and denser contact list. Wide Desktop expands navigation and spacing while bounding content width. The historical Glaze UI 1.4 representative profiles were 390 × 844, 820 × 1180, 1280 × 900, and 1600 × 1000; the V1.3 migration and acceptance must revalidate the supported responsive compositions, density, material, motion, state, accessibility, resilience, and applicable adaptive behavior against the current Stable contract. TV is not a supported Contacts surface in this increment. Android APK and Debian-native packaging remain future milestones; these source changes apply to the current browser/installable client and do not claim native packages exist.
21. Inspect-First Implementation Rule
Examples, diagrams, endpoint lists, paths, environment variables, repository layouts, Docker definitions, migration sequences, and deployment sketches in this specification may describe validated historical state or illustrative future direction.
Before using any such item as an operational instruction, I will inspect:
The current GoreeCloud Contacts repository and branch.
The latest Contacts and Radicale change records.
The target host and runtime.
The current Radicale endpoint and account model.
The current DNS, Caddy, NetBird, and firewall state.
The applicable GoreeCloud policies, standards, and requirements.
The current backup and recovery evidence.
Any newer project specification revision.
Current verified state overrides stale examples. Historical evidence remains preserved but must not be executed merely because it appears in this document.
22. Final Current State
GoreeCloud Contacts is an active native GoreeCloud development project with a working React/TypeScript/Vite frontend, FastAPI backend, server-side CardDAV adapter, conditional ETag-protected writes, Radicale-backed per-user authentication, opaque sessions, validated two-user address-book isolation, the Phase 4A expanded contact model, and Phase 4B raw VCF import/export workflows.
Radicale remains the authoritative contact store. Production family data remains unused. contacts.goreecloud.com is not production published. The current release-candidate source includes encrypted shared sessions, CSRF Origin/Referer enforcement, privacy headers, dependency auditing, hardened Docker runtime controls, canonical application identity enforcement, and production browser-security headers, but the remaining target-environment production-readiness gates still prevent production approval.
Phase 4C duplicate detection/user-reviewed merge and Phase 4D Glaze UI/readiness work are already present in the consolidated release-candidate source. The active development stack now concentrates on release hardening: PR #21 introduced privacy-minimal sign-in abuse controls, PR #22 established canonical cross-platform identity, PR #23 added production browser-security policy, and PR #24 extends sign-in throttling across the production multi-worker runtime by sharing the attempt budget through the protected SQLite state path. Production remains separately gated by isolated Phase 4C live acceptance, target-environment authentication/authorization and shared-worker throttle evidence, private publication, monitoring, backup/recovery and rollback, logging/request-limit validation, DAVx5 coexistence, browser/mobile acceptance, and controlled family onboarding.
23. August 20, 2026 Development Reconciliation
I reconciled this specification against the current GoreeCloud/goreecloud-contacts repository rather than relying on the older Milestone 4 planning state recorded above.
The current source state is materially ahead of the previous specification text. Release branch release/contacts-stable-private-publication is the current consolidated private-publication candidate. Its exact head 696f01d2a82cf50b9ad6d2413ae2ec3c5dd928f8 passed GitHub Actions Continuous Integration run 123. The candidate includes the Phase 4C source implementation, Phase 4D Glaze UI/readiness work, production HTTPS and CSRF requirements, encrypted shared SQLite sessions, liveness/readiness checks, API no-store privacy controls, bounded inputs, dependency auditing, access-log query minimization, browser-safe CardDAV error translation, and a production-shaped Docker runtime. These source controls do not constitute production approval.
I opened draft PR #21, Harden Contacts sign-in abuse controls, on branch agent/auth-abuse-hardening stacked on the release candidate. This increment adds a privacy-minimal, bounded login throttle keyed only by normalized username, HTTP 429 responses with Retry-After after the configured attempt budget is exhausted, successful-login reset behavior, positive configuration validation, documented environment settings, and focused regression tests. It does not retain passwords, session tokens, contact data, request bodies, or client addresses.
The current remaining production boundaries include Phase 4C isolated live acceptance and cleanup, target-environment authentication and authorization evidence, private publication validation, monitoring and alert delivery, backup/restore and rollback evidence, target-runtime logging and request-limit validation, DAVx5 coexistence, production browser/mobile acceptance, and controlled family onboarding. contacts.goreecloud.com remains unapproved for production-family use until those gates are closed.
24. Future Client Packaging Requirements
I will treat native client packaging as part of GoreeCloud Contacts' future delivery roadmap. In addition to the browser application, Contacts must eventually provide an Android APK and a Debian package for supported Linux systems.
The Android APK should provide a GoreeCloud-native mobile Contacts client experience while preserving the authoritative Radicale/CardDAV architecture, per-user isolation, portability, and coexistence with standards-based clients such as DAVx5 where appropriate.
The Debian package should provide an installable Linux desktop client for Debian-family systems. It must follow the same Glaze UI, Wardveil Security, privacy, authentication, packaging, upgrade, rollback, and release-validation requirements as the broader Contacts project.
Neither package is approved for implementation or production distribution yet. Their exact architecture, frameworks, signing model, update strategy, CI/CD pipelines, package metadata, desktop integration, Android permissions, and release channels must be designed and validated in dedicated future milestones against the current repository and platform standards.
25. Cross-Platform Application Icon Requirement
GoreeCloud Contacts must use one canonical application icon and visual identity across every supported client and distribution surface.
The canonical Contacts icon must be reused consistently for the web application, Android APK, Debian/Linux package, desktop launcher, application menus, installation metadata, release artifacts, repository artwork, documentation, and future supported platforms. Platform-specific files may be derived from the canonical artwork only when required by the operating system or packaging format, such as Android adaptive-icon layers or Linux PNG/SVG size variants.
The icon must follow the current GoreeCloud official application visual-identity and Glaze UI standards. Platform-specific packaging must not introduce unrelated artwork, alternate logos, unofficial colors, or client-specific identities that make Contacts appear to be different products.
The canonical source artwork should be maintained in source control as a reusable vector/master asset, with generated platform variants produced from that source through a documented build or asset pipeline. Future Android and Debian packaging work must consume those canonical assets rather than maintaining independent icon copies by hand.
26. Canonical Application Identity Source Implementation
I implemented the first source-controlled canonical GoreeCloud Contacts application identity on branch agent/canonical-app-identity, stacked on agent/auth-abuse-hardening.
The authoritative master artwork is artwork/contacts-icon.svg. The browser-consumable asset is frontend/public/contacts-icon.svg, and frontend/index.html references /contacts-icon.svg for SVG favicon and application touch-icon metadata. Draft PR #22, Establish canonical Contacts application artwork, records this increment.
The canonical icon uses a text-free Glaze UI address-book tile with a person silhouette so the same identity can scale across web, Android, Debian/Linux, repository, release, and documentation surfaces. Android adaptive icons, Linux raster derivatives, package metadata assets, and other platform-specific outputs remain future derivatives and must be generated from the canonical master rather than independently redesigned.
I extended the existing frontend Glaze UI validation gate to enforce the application identity contract. The validator now verifies the canonical SVG identity metadata and 512-square vector contract, requires frontend/public/contacts-icon.svg to remain byte-for-byte identical to artwork/contacts-icon.svg, and requires browser metadata to continue referencing the canonical asset. This makes icon consistency a CI-enforced source requirement rather than documentation-only guidance.
Continuous Integration run #128 / workflow run 32431223686 completed on exact head c9aef6c844b9b426d5501bf061deccf2203a36dd. Backend tests on Python 3.10 and Python 3.13 passed, and the Frontend lint and build job passed including the 20-check identity validator. The Production image smoke test failed during docker build because the strict validator correctly required /build/artwork/contacts-icon.svg while the Docker frontend-build stage copied only frontend/. I corrected docker/Dockerfile to copy artwork/ into /build/artwork/ before validation, preserving the fail-closed master/derivative comparison. The fix is commit e6c9095ef2fd3119366fef6b7ab90eb7babbdd71. Continuous Integration run #129 / workflow run 32448930265 completed successfully on exact head e6c9095ef2fd3119366fef6b7ab90eb7babbdd71. Frontend dependency audit, the 20-check Glaze UI and identity validator, frontend lint, and production build passed. Backend tests passed on Python 3.10 and Python 3.13, with the Python 3.13 dependency-audit gates also passing. The Production image smoke test passed production Compose validation, image construction, image-contract verification, hardened production-shaped container startup, same-origin production-surface smoke testing, and runtime-log collection. This exact-head result closes the source-level CI regression introduced by the stricter canonical-artwork contract without weakening that contract.
I extended the browser identity contract with frontend/public/manifest.webmanifest. The manifest identifies GoreeCloud Contacts, uses same-origin start URL and scope, standalone display mode, and derives its install icon from /contacts-icon.svg with SVG any/maskable metadata. frontend/index.html now references the manifest, and the validator now verifies manifest linkage, product identity, launch contract, and canonical icon linkage in addition to the existing artwork checks. This does not add a service worker or claim offline/PWA functionality. Continuous Integration run #132 / workflow run 32449326939 completed successfully on manifest-enforcement head 45fe0eee10fdbb684bff478aa986e71bb07a4101. I then extended the production runtime smoke test so the built image must serve the manifest and canonical SVG and the delivered HTML must reference the manifest. The exact current PR #22 head is 1002204660e79b983524fec31ed22ba560778181. Continuous Integration run #133 / workflow run 32449411621 completed successfully on that exact head. Frontend dependency audit, the 23-check Glaze UI/canonical-artwork/web-manifest validator, frontend lint and build, backend tests on Python 3.10 and Python 3.13, Python 3.13 dependency audits, production Compose validation, production image construction and contract verification, hardened container startup, and same-origin runtime smoke testing all passed. The runtime smoke test also proved that the built image serves the manifest and canonical SVG and that the delivered HTML references the manifest.
Android APK and Debian package implementation remain future milestones. This identity work does not claim those native packages are implemented or approved for distribution.
27. Production Browser Security Header Hardening
I opened draft PR #23, Harden production browser security headers, on branch agent/browser-security-headers stacked on the exact green PR #22 identity head. The production application now wraps API, HTML, manifest, and static-asset responses with a single browser-security policy.
The policy includes a strict same-origin Content-Security-Policy covering default, base, connect, font, form, frame, image, manifest, object, script, style, and worker behavior. It rejects framing, object execution, workers, unsafe-inline, unsafe-eval, and external HTTP(S) source allowances. It also adds X-Frame-Options DENY, Cross-Origin-Opener-Policy same-origin, Cross-Origin-Resource-Policy same-origin, Referrer-Policy no-referrer, X-Content-Type-Options nosniff, and a restrictive Permissions-Policy disabling camera, geolocation, microphone, payment, and USB access.
Application-level HSTS is intentionally not added. HTTPS and HSTS remain responsibilities of the validated Caddy/private-publication layer so local HTTP development and internal health checks are not altered by the application middleware.
Exact current PR #23 head 9c9b23b48b6fe4c9b9fe9b981d160b7c806d169f passed Continuous Integration run #138 / workflow run 32450262273. Frontend dependency audit, the 23-check Glaze UI/canonical-identity validator, frontend lint/build, backend tests on Python 3.10 and Python 3.13, Python 3.13 dependency audits, production Compose validation, production image construction and contract verification, hardened production-shaped container startup, and same-origin production-surface smoke testing all passed. The browser-security regression tests passed on both supported Python versions, and the production smoke test verified the required security policy on actual delivered HTML and API responses. Run #136 had failed only because the first runtime CSP assertion compared the entire policy as one order-sensitive string; the policy was present. The assertion was corrected to validate each required CSP directive independently while explicitly rejecting unsafe-inline and unsafe-eval. Implementation head f95aec7c52822e2d79409e97c579cd9447359ca7 then passed run #137, and
The documentation-reconciled current head passed again in run #138.
PR #23 remains open and draft because it is stacked on draft PR #22. This source-level hardening does not approve production deployment, Android APK distribution, Debian package distribution, or production-family contact use.
28. Shared Multi-Worker Sign-In Throttle Hardening
I opened draft PR #24, Share sign-in throttling across production workers, on branch agent/shared-login-throttle stacked on the exact green PR #23 head. This increment closes the source-level mismatch between PR #21's process-local throttle and the production candidate's two-worker Uvicorn runtime.
The existing process-local LoginThrottle remains the development and isolated-test implementation when SESSION_STORE_BACKEND=memory. When SESSION_STORE_BACKEND=sqlite, the application now creates a shared SQLite-backed throttle in the existing protected SESSION_DB_PATH so independent backend workers enforce one configured attempt budget.
The shared throttle stores only a SHA-256 digest of the normalized username and attempt timestamps in a dedicated login_throttle_attempts table. It does not persist passwords, session tokens, contact data, request bodies, or client addresses. Check-and-record decisions use SQLite BEGIN IMMEDIATE transactions so concurrent workers cannot independently consume separate per-process attempt budgets. Successful CardDAV authentication resets the shared identity window, and expired attempt records are pruned.
Regression coverage now includes cross-instance shared-budget enforcement, a spawned-OS-process proof that distinct processes share one configured attempt budget, cross-instance reset behavior, expiry pruning, plaintext-username non-persistence, backend-selection behavior, and the original process-local threshold/expiry/reset behavior. The production-image smoke test also configures a two-attempt budget and executes three separate Python processes inside the hardened production-shaped container through the application-wired login_throttle; the first two attempts are accepted and the third is required to observe the shared SQLite state and block. .env.example, docs/security.md, and CI runtime validation are reconciled with the shared-worker model.
Implementation/runtime-validation head f1d88f66b423dc4e2e3b58e9f62591f5f6026c09 passed Continuous Integration run #141 / workflow run 32692530681, including backend tests on Python 3.10 and Python 3.13, dependency audits, frontend/Glaze UI validation, and the production-image application-wired cross-process shared-throttle assertion. The security-document reconciliation then moved PR #24 to exact current head 4a9498ec80b05f76b7d4a2bce54d3aa6cfcda69c. Continuous Integration run #142 / workflow run 32692714010 completed successfully on that exact final head and repeated the full source and hardened production-image validation, including the cross-process throttle assertion. PR #24 is therefore exact-head source-and-production-shaped-runtime CI validated, while target-environment acceptance remains separately required. Production deployment, production-family contact use, Phase 4C isolated live acceptance, target-environment authentication/authorization and throttle behavior, private publication, monitoring, backup/restore and rollback, DAVx5 coexistence, and browser/mobile acceptance remain separate pending gates.
29. Glaze UI 1.4 Form-Factor Layout Adoption
I opened draft PR #25, Adopt Glaze UI 1.4 purpose-built Contacts layouts, on branch agent/glaze-ui-1.4-form-factor-layout stacked on the exact-green PR #24 head. The current Stable GoreeCloud/glaze-ui main branch reports version 1.4.0, whose form-factor contract treats Mobile, Tablet, Desktop, and Wide Desktop as purpose-built interaction environments rather than one layout scaled by width.
The Contacts browser/installable client now uses purpose-built form-factor compositions. Compact windows through 719 px use a touch-first stacked workspace with a true safe-area-aware lower Contacts/Favorites navigation zone, floating lower create action, horizontal address-book selection, labeled contact cards, and full-width touch actions. Compact configuration, safety, and error notices use tighter readable spacing with long configuration tokens allowed to wrap; loading, sign-in-required, and no-results states use a full-width Glaze empty-state card. Authentication/account presentation follows the same contract: the Compact sign-in card is full-width with 48 px controls, account identity is bounded with ellipsis protection, sign-out remains reachable, and backend status uses a Glaze-token state surface. Contact detail and editor surfaces use Glaze-token material styling, stacked Compact actions with 46 px touch targets, and full-width destructive-action separation. Narrow Tablet windows from 720–839 px retain a persistent touch navigation pane while using single-column contact cards, a full-width sign-in workflow, and single-column detail/editor forms. Roomier Tablet windows from 840–1023 px use the persistent pane with two-column contact cards and intentionally expanded two-column detail/editor grids; loading and empty states span the entire two-column contact canvas instead of occupying one column. Desktop/Expanded uses a persistent productivity sidebar and dense four-column contact list. Wide Desktop expands navigation and spacing while bounding content width.
The VCF import/export and duplicate-detection/review workflows now participate in the same Glaze UI 1.4 system rather than retaining legacy presentation rules. Their surfaces use Glaze tokens for borders, material surfaces, muted text, semantic success/warning/danger states, and shadows; their Compact layouts stack workflow tasks and comparison cards with touch-sized controls; Narrow Tablet avoids cramped side-by-side tool and duplicate-comparison panels. Reduced-transparency and forced-colors fallbacks apply to these workflow surfaces as well.
frontend/scripts/validate-form-factors.mjs is connected to npm run validate:ui and now fails CI if the Mobile, Narrow Tablet, Roomier Tablet, Desktop, or Wide composition rules regress; if loading/empty/no-results states stop spanning the active contact canvas or Compact notices lose their readable wrapping/spacing contract; if Compact authentication stops using the full-width touch-sized sign-in contract; if account/backend state stops being bounded and touch-friendly; if contact detail/editor surfaces stop using the current Glaze material and touch/form-factor contracts; if keyboard users lose the visible skip path, group-level focus orientation, sticky-chrome/Compact-navigation scroll clearance, forced-colors focus fallback, or reduced-motion behavior; if the VCF or duplicate-review workflows stop using their Glaze token/form-factor contracts; if the legacy hard-coded light palette reappears in those workflow tools; or if third-party presentation dependencies are introduced.
Exact PR #25 head aeb8f65cc74a5555b036f99ba6afd7f824258a75 passed Continuous Integration run #159 / workflow run 32730836161. The successful run included frontend dependency audit, the Glaze UI/canonical-identity checks, the strengthened shell/feedback/authentication/account/detail/editor/workflow and keyboard-focus conformance validator, frontend lint/build, Python 3.10 and Python 3.13 backend tests, Python 3.13 dependency audits, production Compose validation, production image construction and contract checks, hardened-container startup, and same-origin production-surface smoke testing.
This acceptance proves the exact source and production-shaped packaged runtime, but it does not replace representative real-device/browser visual and interaction acceptance at Mobile 390 × 844, Tablet 820 × 1180, Desktop 1280 × 900, and Wide Desktop 1600 × 1000. Native Android APK and Debian/Linux desktop packages remain future milestones and are not claimed as implemented by PR #25. Production deployment and production-family contact use remain unapproved.
Superseding Native-Build and Platform Integration Mandate
This specification is governed by the platform-wide requirement that this application be built natively from the ground up as original GoreeCloud-owned software. Earlier maintained-fork or upstream-product implementation language is transitional only. Narrow critical foundations may be retained only when independently replacing them would materially increase security, cryptographic, protocol, standards, codec, rendering, operating-system, runtime, or interoperability risk; WireGuard and mature cryptographic or encryption primitives are canonical examples. Such exceptions must remain limited to the minimum technical foundation and must not preserve upstream product architecture, UI, branding, workflows, or general application logic.
This application must remain current with the latest applicable Stable Glaze UI contract and the latest approved Wardveil Security, Privacy Shield, and Everkeep contracts. All four are mandatory. Missing, incomplete, superseded, outdated, unverified, or unaccepted integration with any required platform system blocks Stable qualification
30. Public Profile Development Candidate — September 3, 2026
Development status: Draft PR #28 (`agent/contact-public-profiles`) is stacked on draft PR #27 and is not merged to `main`, production-approved, or approved for production-family contact data. Exact head `838bec9c2187643f2bee151977b87b26f93d2b74` passed GitHub Actions Continuous Integration run #167 (`33806659810`), including frontend lint/build and Glaze requirement validation, backend tests on Python 3.10 and 3.13, and the production-image smoke test. This establishes development-head source/runtime-CI validation only; no live Radicale public-profile mutation, representative-device acceptance, production deployment, or application-wide Glaze UI V1.1 conformance is claimed.
The candidate adds repeatable public-profile records to the structured contact model. Each record contains a normalized platform slug and an explicit HTTP(S) public-profile URL. Public profiles remain ordinary user-controlled contact data; the application does not discover, scrape, infer, verify, or continuously monitor external accounts.
Radicale/CardDAV remains authoritative. The candidate stores each public profile as a standard vCard URL property with a GoreeCloud platform parameter, for example `URL;TYPE=profile;X-GOREECLOUD-PLATFORM=github:https://github.com/example`. Generic vCard consumers can continue to read the URL, while GoreeCloud-aware clients can recover the platform association. Invalid GoreeCloud profile metadata falls back to an ordinary website rather than hiding the URL.
The candidate preserves existing signed-in-user address-book authorization and ETag-protected CardDAV mutation paths. Public-profile URLs are limited to HTTP and HTTPS. Duplicate-merge logic unions and deduplicates profile entries while preserving the existing survivor/ETag safety model. VCF portability remains the mechanism by which these fields participate in export and recovery; this entry does not claim new Everkeep recovery evidence.
The browser candidate adds a repeatable Public profiles editor and contact-detail presentation with locally encoded identifying marks for selected known platforms plus a generic link presentation for custom platforms. It does not introduce remote icon, font, CSS, script, or profile-fetch dependencies. Platform marks are identification aids only and do not establish affiliation, sponsorship, verification, or GoreeCloud Identity relationships.
Current design target reconciliation: the authoritative Glaze UI standard and current canonical Glaze UI release identify GLAZE UI V1.1 / 1.1.0 as the current Stable design-system release after the platform reset. Earlier Contacts specification passages referring to Glaze UI 1.5.0 or historical 1.4 acceptance are retained as historical records but do not define the current consumer target. PR #28 applies current V1.1 interaction principles to this feature only and does not claim application-wide V1.1 conformance or production acceptance.
.
31. Platform Contract v0.2 Development Candidate — September 3, 2026
Development status: Draft PR #29 (`agent/platform-contract-v0.2`) is stacked on draft PR #28 and remains unmerged. The candidate adds the repository-root `goreecloud.platform.yaml` required by the current central Platform Contract v0.2 and replaces the older local four-system `docs/platform-systems.json` mechanism with the canonical seven-system contract model. The superseded local manifest and its bespoke backend regression test are removed on this branch so they do not compete with the central source of truth.
The v0.2 manifest records GoreeCloud Contacts as a Development-stage web application with application/API source version 0.5.0, liveness `/api/health/live`, readiness `/api/health/ready`, Radicale/CardDAV as the required authoritative external dependency, and explicit backup, restore, VCF export, and standards-based portability requirements. GoreeCloud Manager, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, and GoreeCloud Identity are truthfully declared `applicable-blocked`; Glaze UI is `applicable-migration-required` from the historical 1.4 source state to current Stable GLAZE UI V1.1 / 1.1.0. Overall conformance is deliberately declared nonconformant while those gates remain open.
Exact-head Platform Contract evidence: branch head `86b10beeb1fb283cf5f30a4e045e08389cc77d3f` passed Platform Contract push run #2 (`33817119126`) using central validator revision `8779763fb6c0ee51ff26669205e04fbd7c8b3db2`. The generated artifact `goreecloud-platform-conformance-86b10beeb1fb283cf5f30a4e045e08389cc77d3f` records `evaluated_revision` exactly equal to the branch head. Its computed result is `nonconformant` with `stable_eligible: false`, which is the intended fail-closed result while platform-system integrations, Stable acceptance categories, and release evidence remain incomplete. The compatibility check confirms the declared Glaze UI target is current Stable 1.1.0.
Supplemental pull-request Platform Contract run #3 (`33817121185`) also passed. Inspection of the central reusable workflow showed that pull-request events currently evaluate GitHub's synthetic pull-request merge SHA through `GITHUB_SHA` rather than the branch head. Contacts therefore runs the Platform Contract workflow on branch pushes as well, providing exact-head evidence without claiming the central attribution issue is fixed. The platform-wide remediation is tracked in GoreeCloud/Tasks Management.
General Contacts Continuous Integration run #169 (`33817120790`) completed successfully on exact head `86b10beeb1fb283cf5f30a4e045e08389cc77d3f`. Frontend dependency installation/audit, Glaze UI requirement validation, lint, and production build passed. Backend tests passed on Python 3.10 and Python 3.13, including the Python 3.13 project and locked-production dependency audits. The production-image smoke test passed production Compose validation, image build/contract verification, hardened production-shaped container startup, same-origin production-surface smoke testing, and runtime-log collection. This establishes exact-head source/runtime-CI validation for the PR #29 development branch without changing its intentionally nonconformant, non-Stable platform status.
Boundary: PR #29 changes repository conformance declaration/validation only. It does not deploy Contacts, change Radicale or CardDAV data, alter DNS/Caddy/NetBird/firewall state, use production-family contacts, or establish Stable qualification. Production and production-family use remain unapproved.
32. GLAZE UI V1.1 Development Candidate — September 4, 2026
Development status: Draft PR #30 (`agent/glaze-v1.1-source-migration`) is stacked on draft PR #29 and remains unmerged. Exact head `6cb5a7357f87c8de0e4647a13f130e4d2b6fcd25` passed Platform Contract #20 and Continuous Integration #174. This establishes exact-head Development source/runtime-CI evidence only; it does not establish rendered, accessibility, representative-device/browser, Integral Platform System, Release Candidate, Stable, production, or production-family acceptance.
The candidate corrects a V1.1 appearance-precedence defect: the system `prefers-color-scheme: dark` fallback now applies only when no explicit `data-glz-appearance` is selected. Explicit Deep Dark therefore remains authoritative instead of being overwritten by the later system-dark rule. `frontend/scripts/validate-glaze-ui.mjs` now fails closed if that precedence regresses.
The branch remains pinned for Development evidence to immutable GLAZE UI V1.1 / 1.1.0 revision `15cc76d2bcd4065552dc31c77145b63f34d9e7b2`, but that Stable release now has a known import-closure defect in its published web source graph. Corrective GLAZE UI 1.1.1 remains an unmerged Release Candidate and is not a Stable authority that Contacts may silently adopt. `goreecloud.platform.yaml` therefore remains `applicable-migration-required` and overall `nonconformant`; Contacts must explicitly re-pin to a corrected immutable Stable release and repeat applicable exact-revision source, rendered, accessibility, representative-device/browser, and production acceptance.
Radicale/CardDAV remains the sole authoritative contact store. PR #30 does not change CardDAV data, production-family data, DNS/Caddy/NetBird/firewall state, deployment state, or production runtime authority. Manager, Privacy Shield, Wardveil Security, Everkeep, GoreeCloud Mesh, GoreeCloud Identity, recovery/rollback, production-runtime, and release gates remain open. Android APK and Debian-native Contacts packaging remain separately governed future milestones and are not implemented or approved by this candidate.
33. September 9, 2026 Development Reconciliation — Reduced Motion and GLAZE UI V1.3 Target
Draft PR #30 (`agent/glaze-v1.1-source-migration`) advanced to exact head `113585d5da9b72a4625eb14e2387fdd979f24a7c`. The final Reduced Motion correction preserves the source-level `transition: none` fallback required by the Contacts form-factor validator while also enforcing `transition: none !important`, zero transition duration, and zero transition delay for the skip link and the existing keyboard-focus workflow surfaces. This prevents later migration-layer transitions from reintroducing measurable motion when `prefers-reduced-motion: reduce` is active. Exact-head Platform Contract run `34324494195` and Continuous Integration run `34324493774` both passed, including rendered browser acceptance. This is Development source/runtime acceptance only; representative-device/browser, current-Glaze application acceptance, Integral Platform System, release, production, and native-package gates remain open.
A separate stacked Draft PR #31 (`agent/contacts-glaze-v1.3-target-reconciliation`) reconciles the machine-readable current Glaze requirement without relabeling the implemented Contacts source. Current GoreeCloud Glaze release authority identifies GLAZE UI V1.3 / `1.3.0` as the current Official/Stable/consumer-eligible shared target. Contacts therefore keeps `platform_systems.glaze_ui.version: 1.1.0`, `applicable-migration-required`, and overall `nonconformant`, while `compatibility.glaze_ui_required` and the required dependency now target `1.3.0`. The Contacts Platform Contract workflow was also advanced from the superseded evaluator pin `8779763fb6c0ee51ff26669205e04fbd7c8b3db2` to current central Platform Contract revision `235e519fe342d7e7075c8239fbf0f3a19dc4c6c8`, which carries the approved V1.3 consumer baseline.
Exact PR #31 head `3f4a3b878d76855e40d8e4f63bbdcdb6aa38a790` passed Platform Contract run `34325637381` and Continuous Integration run `34325636746`. This confirms the declaration and existing Contacts source/runtime checks agree at that exact Development revision. It does not mean Contacts has completed a V1.3 source migration or application acceptance. Radicale/CardDAV remains authoritative. Manager, Privacy Shield, Wardveil Security, Everkeep, Mesh, Identity, representative-device/browser, recovery/rollback, signing/provenance, Release Candidate, Stable, production deployment, production-family data use, Android APK, and Debian-native package gates remain incomplete or unapproved as applicable
34. September 10, 2026 — Bounded GLAZE UI V1.3 Foundation Staging
Draft PR #34 (`feature/contacts-glaze-v1.3-foundation`) is stacked directly on Draft PR #33 (`docs/contacts-profile-development-state-control`) exact head `ae80400607dfd27433e59bd0dd141755330b3246`. The exact PR #34 head is `17369a83a586b71783c43b809550800f369ffbe8`.
This tranche introduces `frontend/src/glaze-v1.3-foundation.css`, anchored to exact GLAZE UI V1.3 / 1.3.0 Stable implementation revision `fc7cc91d2eace8da2371371c2855c24cbcb326a1`. It stages the inherited V1.2/V1.3 neutral/frosted material foundation and Contacts-owned compatibility variables while explicitly preserving protected success, warning, critical, and focus roles. The staged layer does not grant wallpaper/environment sampling, remote dynamic color, contextual intelligence, Personalization persistence, System Shell authority, or product-truth authority.
The foundation is deliberately non-activating in this checkpoint. `frontend/src/main.tsx` loads it after the active V1.1 layer, but the stylesheet is isolated behind `data-glaze-target-version="1.3"`; the live document remains `data-glaze-version="1.1"` and does not set the target marker. `frontend/scripts/validate-glaze-v1.3-foundation.mjs` is wired into `npm run validate:ui` and fails closed if this tranche silently activates a V1.3 root/target, loses its exact authority anchor or resilience boundaries, introduces remote presentation dependencies, or stops preserving the current V1.1 runtime boundary.
The machine-readable Platform Contract remains truthful: implemented Glaze version `1.1.0`, result `applicable-migration-required`, required compatibility target `1.3.0`, lifecycle Development, and overall `nonconformant`. Exact-head Platform Contract run `34542118740` / #60 and Continuous Integration run `34542118164` / #192 both completed successfully on `17369a83a586b71783c43b809550800f369ffbe8`. The CI result validates this bounded source/build/production-shaped-runtime checkpoint without converting staged V1.3 source into V1.3 application acceptance.
PR #34 changes presentation staging, source validation, and conformance evidence only. It does not change CardDAV or Radicale data, contact mutation behavior, authentication, authorization, sessions, duplicate review/merge, VCF portability, DNS, Caddy, NetBird, firewall state, deployment, production-family data use, Android packaging, or Debian packaging. The next V1.3 tranche must deliberately switch the active root/source contract on one exact revision and repeat applicable rendered, interaction, accessibility, responsive/form-factor, representative-device/browser, performance, rollback, Integral Platform System, release, and production acceptance. Until those gates pass, Contacts remains Development and nonconformant to the current shared Glaze target
35. September 10, 2026 — Feature Roadmap Control Reconciliation
The current Draft PR #34 branch previously lacked the repository-side `FEATURE-ROADMAP.md` counterpart required by the canonical Drive roadmap control. The missing root roadmap has now been added and reconciled against this authoritative specification, the current PR #34 source state, and `goreecloud.platform.yaml` without changing Contacts runtime behavior.
The reconciled roadmap preserves Radicale/CardDAV as the sole authoritative contact store and records current obligations for per-user authentication and isolation, ETag-protected conditional writes, the structured contact model and CardDAV-backed groups/public profiles, user-reviewed duplicate merging, raw VCF portability, deliberate GLAZE UI V1.3 migration and application acceptance, responsive/accessibility form factors, canonical identity, privacy/security hardening, Integral Platform System acceptance, continuity/recovery, production publication, future Android and Debian-native packages, and exact-revision release gates. Planned work remains Planned and source-local safeguards are not represented as accepted platform authority.
Roadmap reconciliation advanced the final Draft PR #34 head from the V1.3 staging source head `17369a83a586b71783c43b809550800f369ffbe8` to `2c62ac7ba149060ef2e34b74bd014850ca9338b7`. That exact final head passed Platform Contract run `34547018199` / #62 and Continuous Integration run `34547017894` / #193. The earlier V1.3 staging head remains valid source/runtime evidence and passed Platform Contract `34542118740` / #60 plus Continuous Integration `34542118164` / #192.
The canonical `GoreeCloud/Feature Roadmap/GoreeCloud Contacts/FEATURE-ROADMAP.docx` was synchronized in place under its existing Drive file ID and governed Contacts roadmap folder. The final three-page document was rendered and visually inspected page by page, re-fetched from Drive after replacement, and verified byte-for-byte at SHA-256 `0d3b88ad9178e7cdd615314faba91fdbf0dc95035b5fab519308774997345bd9`.
This reconciliation is governance/documentation work only. The live Contacts browser root remains GLAZE UI V1.1 / `1.1.0`; the V1.3 / `1.3.0` foundation remains staged but non-activating, and Contacts remains web Development / overall `nonconformant`. Deliberate V1.3 root migration, whole-application rendered/accessibility/responsive/representative-browser acceptance, Manager/Privacy Shield/Wardveil Security/Everkeep/Mesh/Identity acceptance, recovery/rollback, production publication and family-data approval, Android APK, Debian-native package, signing/provenance, Release Candidate, production, and Stable qualification remain open..
.

---

## Ongoing maintenance

Update this record for significant architecture, governance, repository, licensing, security/privacy, data-authority, packaging, production/recovery, lifecycle, migration, split/merge/rename, deprecation, or retirement events. Routine feature/fix chronology remains in `CHANGELOGS.md`.
