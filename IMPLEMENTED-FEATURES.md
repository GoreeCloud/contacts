# GoreeCloud Contacts — Implemented Features

**Record type:** Repository implemented-feature inventory  
**Repository:** `GoreeCloud/goreecloud-contacts`  
**Lifecycle:** Development  
**Migration state:** Repository-native authority accepted on `main` through PR #42; mapped Contacts Drive roadmap retired and independently verified not found.  
**Product capability evidence baseline:** accepted application state at `4e4cd3750c2ae03c769b7c30b0253b273887a7bc`; governance migration accepted as `4fd378ab5aeec599192fe1b53fef2315a9d5a284`.  
**Governing standard:** Standard — Repository Feature Tracking and Changelog Governance v1.0.

## Interpretation

This record describes capabilities evidenced on authoritative `main`. Open Draft pull requests, including PRs #34–#41 and their stacked Android/GLAZE work, are candidate-only and are not promoted into implemented state here.

Contacts remains Development. Source, CI, synthetic-data, and isolated test evidence do not establish production-family data approval, Release Candidate qualification, production acceptance, or Stable qualification.

## Implemented Development capabilities on `main`

### CardDAV/Radicale foundation
- Radicale/CardDAV is the authoritative contact service; Contacts does not maintain a competing ordinary-contact database.
- Address-book discovery, contact listing, contact detail retrieval, local search, and resource href/ETag preservation are implemented.
- Common vCard fields are parsed and rendered through the browser application.

### Conditional write safety
- Contact creation uses `If-None-Match: *`.
- Contact update and delete use ETag-backed `If-Match` protection.
- Stale preconditions are surfaced as application conflicts instead of silent overwrites.
- The local write gate is intended to remain disabled outside controlled validation.

### Per-user authentication and isolation
- Per-user Radicale-backed sign-in is implemented.
- Opaque HTTP-only server-side sessions are used.
- CardDAV credentials remain backend-only after sign-in.
- Address-book and contact-resource access is constrained to collections authorized for the signed-in user.
- Logout and session-expiration behavior are implemented.
- Negative two-user isolation and short-TTL expiration behavior were validated with isolated synthetic test identities.

### Expanded contact model and browser workflows
- Structured names, organizations/titles, multiple email/phone/address values, birthdays, websites, notes, categories, favorites, HTTP(S) photo references, and full contact-detail retrieval are implemented Development foundations.
- Browser Contacts/Favorites views, broader search, read-only detail viewing, and guarded create/edit/delete/favorite workflows are present.
- Structured API validation errors are rendered as readable messages rather than generic object text.

### VCF portability foundation
- Single-contact and full-address-book raw VCF export are implemented.
- vCard 3.0/4.0 import preview and validation are implemented before mutation.
- Import requires explicit destination and selected preview records.
- Unknown source properties are preserved where possible; UID generation is limited to missing-UID cases.
- Controlled synthetic validation established round-trip preservation for tested unknown properties and UID values.

### Repository controls
- Root `IMPLEMENTED-FEATURES.md`, `PLANNED-FEATURES.md`, and `CHANGELOGS.md` are the repository-native feature/changelog authorities established by PR #42.
- Legacy root `FEATURE-ROADMAP.md` is retired and absent from authoritative `main`.
- The migrated Contacts Drive `FEATURE-ROADMAP.docx` source (file ID `1iEju1z-62uoRMQc6GXX8kr5DazpdiZuk`) was permanently deleted only after authoritative readback and post-merge validation; independent Drive readback returned 404 Not Found.
- Repository documentation records Development-only acceptance boundaries and synthetic/non-production validation rules.

## Implemented-but-incomplete capability families

The following have implemented Development foundations but retain open obligations in `PLANNED-FEATURES.md`:
- CardDAV authority, per-user isolation, and conditional writes;
- expanded contact-model and product workflows;
- VCF portability;
- accessibility/responsive/product refinement;
- security/privacy hardening;
- recovery and production-readiness preparation.

## Explicitly not implemented or not accepted on current `main`

Authoritative `main` does not establish:
- accepted GLAZE UI V1.3/V1.4/V1.4.1 application migration;
- the Draft native Android Contacts application stack from PRs #35–#41;
- native GoreeCloud Identity session/runtime binding for Android;
- accepted Manager, Privacy Shield, Wardveil Security, Everkeep, Mesh, or Identity runtime integration;
- approved production publication at `contacts.goreecloud.com`;
- production-family contact-data approval;
- Debian-native packaging;
- controlled production signing/provenance;
- Release Candidate or Stable qualification.

## Maintenance rule

When a capability becomes accepted on authoritative `main`, update this file, reconcile the corresponding open obligation in `PLANNED-FEATURES.md`, and record the meaningful event in `CHANGELOGS.md` in the same governed workflow.