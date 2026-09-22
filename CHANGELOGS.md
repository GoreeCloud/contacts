# GoreeCloud Contacts — Changelogs

**Record type:** Repository changelog and migration history  
**Repository:** `GoreeCloud/goreecloud-contacts`  
**Lifecycle:** Development  
**Migration state:** Candidate on `migration/repository-feature-records-20260922`; authoritative only after accepted merge to `main`.  
**Current accepted baseline:** `4e4cd3750c2ae03c769b7c30b0253b273887a7bc`.  
**Governing standard:** Standard — Repository Feature Tracking and Changelog Governance v1.0.

## Authority and interpretation

This file records meaningful repository changes established by accepted repository state and retained project evidence. No dedicated `Change Log — Contacts` Drive source was resolved during the bounded migration inventory; therefore no Drive changelog is claimed as migrated or eligible for retirement in this tranche.

Open Draft PRs #34–#41 remain candidate-only. Their source/build evidence may be historically relevant, but it is not accepted implementation authority until merged and verified on authoritative `main`.

## Current repository changelog

### September 22, 2026 — Repository-native feature/changelog migration candidate
- Added root `IMPLEMENTED-FEATURES.md`, `PLANNED-FEATURES.md`, and `CHANGELOGS.md` on an isolated migration branch.
- Reclassified the legacy roadmap into implemented Development foundations and open/partial/blocked obligations without promoting Draft work into accepted state.
- Preserved all material legacy roadmap identifiers FR-001 through FR-025 that exist in the verified Drive roadmap source.
- Identified Drive `FEATURE-ROADMAP.docx` file ID `1iEju1z-62uoRMQc6GXX8kr5DazpdiZuk` as the mapped roadmap migration source.
- No dedicated Contacts Drive changelog source was resolved; this migration does not delete or claim migration of an unidentified changelog.
- No contact data, CardDAV behavior, authentication/session behavior, permissions, network path, platform-system runtime authority, deployment, production, Release Candidate, or Stable state is changed by this governance migration.

### September 9, 2026 — Repository feature-roadmap control
- Accepted root `FEATURE-ROADMAP.md` as a repository-side roadmap control on `main` at `4e4cd3750c2ae03c769b7c30b0253b273887a7bc`.
- The legacy roadmap contained only the initial governance rows FR-001 through FR-003 and required synchronization with a Drive roadmap; that synchronization model is now superseded by repository-native governance.

### Milestone 4 Phase 4B — VCF import/export Development foundation
- Implemented single-contact and full-address-book raw VCF export.
- Implemented vCard 3.0/4.0 import preview and validation before mutation.
- Required explicit destination address-book selection and selected preview records.
- Preserved unknown source properties where possible and generated UIDs only when absent.
- Retained write gating and `If-None-Match: *` create safety for controlled imports.
- Isolated synthetic validation established raw VCF round-trip preservation for the tested custom property and UID.

### Milestone 4 Phase 4A — Expanded contact model and browser workflows
- Added structured names, organizations/titles, postal addresses, birthdays, websites, notes, categories, favorites, photo-reference awareness, and full authenticated contact detail retrieval.
- Expanded browser Contacts/Favorites/search/detail/edit workflows while preserving CardDAV authorization and ETag protections.
- Corrected structured validation-error rendering after browser validation exposed generic object text.
- Phase 4A was recorded as squash-merged to `main` as `1e2675390e06e9485bf664b53b0552c2e4575cd4`.

### Milestone 3 — Authentication and multi-user isolation
- Replaced a single application-wide CardDAV identity with per-user Radicale-backed sign-in.
- Added opaque HTTP-only server-side sessions and explicit logout/session expiration.
- Kept CardDAV passwords out of browser-readable storage and source control.
- Restricted address books and `.vcf` resources to collections authorized for the signed-in session.
- Validated negative two-user isolation and short-TTL expiration with isolated synthetic identities.

### Milestone 2 — Conditional CardDAV writes
- Added guarded creation using `If-None-Match: *`.
- Added ETag-protected update/delete using `If-Match`.
- Surfaced stale CardDAV preconditions as conflicts rather than blind overwrites.
- Preserved contact UIDs and guarded browser create/edit/delete controls.

### Milestone 1 — Read-only CardDAV proof of concept
- Established React/TypeScript frontend and FastAPI backend foundations.
- Implemented CardDAV principal/address-book discovery and synthetic contact retrieval.
- Preserved resource hrefs and ETags and parsed common vCard fields.
- Added responsive browser contact list/search, dependency locking, and CI.
- Validated the browser-to-Radicale read path without production-family contact data.

## Drive retirement gate

The mapped Drive roadmap must not be deleted until:
1. this migration is accepted through the repository workflow;
2. applicable exact-head checks pass;
3. the three root repository-native records are read back from authoritative `main`;
4. retired root `FEATURE-ROADMAP.md` is confirmed absent;
5. repository references to the retired roadmap model are reconciled; and
6. applicable post-merge validation passes on the accepted revision.

Only after those gates pass may the mapped Drive roadmap be permanently deleted:
- `GoreeCloud/Feature Roadmap/GoreeCloud Contacts/FEATURE-ROADMAP.docx` — file ID `1iEju1z-62uoRMQc6GXX8kr5DazpdiZuk`.

No Contacts Drive changelog deletion is authorized by this record because no dedicated source was resolved in the bounded inventory.

After any permitted Drive deletion, independently verify the source ID returns not found and record that retirement in a narrow follow-up repository change.

## Maintenance rule

Record meaningful implementation, architecture, privacy/security, accessibility, migration, compatibility, deployment, recovery, release, rollback, and correction events here with evidence-backed lifecycle state. Preserve historical facts; do not rewrite old evidence to match later architecture.