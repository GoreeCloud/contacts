# GoreeCloud Contacts — Project Specifications

**Repository:** `GoreeCloud/contacts`  
**Project type:** First-party self-hosted contact-management application  
**Lifecycle:** Development  
**Repository visibility:** Public  
**Default branch:** `main`  
**Migration baseline:** `85be95c07179224933548e3605b1d727cb3f4d5b`  
**Current default-branch license:** MIT  
**Authoritative contact service:** Radicale / CardDAV  
**Canonical authority:** This file is the authoritative project specification once accepted on the default branch.

## Authority and migration boundary

This specification reconciles Google Drive **Project Specification — Contacts** with authoritative repository state.

The Drive source contains substantial historical and unmerged Development-candidate detail. It also describes a prospective AGPL-3.0-only licensing transition. At the migration baseline, live GitHub reports the repository license as MIT and authoritative `main` still contains the MIT license. Therefore the prospective AGPL language is preserved in `PROJECT-RECORD.md` as planned/candidate history and is **not** represented here as an already-completed license change.

Authoritative implementation state is maintained by:
- `IMPLEMENTED-FEATURES.md`;
- `PLANNED-FEATURES.md`;
- `CHANGELOGS.md`; and
- accepted source, tests, CI, pull requests, commits, and releases on the repository.

Open Draft pull requests remain candidate evidence until merged and verified on `main`.

## Role and purpose

GoreeCloud Contacts is the private, self-hosted personal and family contact-management application for GoreeCloud. It provides a GoreeCloud-owned user experience over standards-based contact data while preserving portability and interoperability.

## Authoritative data model

Radicale/CardDAV remains authoritative for ordinary contact data. Contacts must not silently create a competing authoritative ordinary-contact database.

Application-local indexes, caches, session state, projections, derived search state, configuration, and other bounded application state may exist where technically justified, but they must not change the authoritative CardDAV ownership model.

## Architecture

The accepted web application architecture uses:
- React + TypeScript + Vite for the browser client;
- Python + FastAPI for the backend;
- CardDAV as the contact protocol;
- vCard as the portable contact format;
- Radicale as the authoritative contact service;
- opaque server-side application sessions; and
- per-user CardDAV access through the authenticated application boundary.

Technology choices remain subject to security, privacy, maintainability, interoperability, and production-readiness review.

## Authentication and multi-user isolation

Contacts must:
- authenticate users through an approved identity/CardDAV boundary;
- keep reusable CardDAV credentials out of browser-readable storage;
- use bounded, protected application sessions;
- constrain address-book access to collections authorized for the signed-in user;
- constrain contact-resource access to authorized resources within those collections;
- revalidate authorization on mutations;
- provide logout and session-expiration behavior;
- prevent cross-user address-book/contact access; and
- fail closed when identity or authorization cannot be established.

Future GoreeCloud Identity integration must preserve these authority boundaries rather than manufacturing access from application-local state.

## Contact read, search, and detail behavior

Contacts should support:
- address-book discovery;
- contact listing and detail retrieval;
- local search and filtering;
- structured names;
- organizations and titles;
- multiple email addresses and phone numbers;
- postal addresses;
- birthdays;
- websites and public-profile links;
- notes;
- categories/groups;
- favorites;
- photo references where safely supported; and
- transparent handling of unsupported or preserved vCard properties.

Search, sorting, and derived presentation must not alter authoritative CardDAV records without an explicit user-authorized mutation.

## Conditional write model

Mutations must preserve CardDAV concurrency and safety.

Expected controls include:
- create with `If-None-Match: *` where applicable;
- update/delete with ETag-backed `If-Match`;
- conflict presentation instead of silent overwrite;
- UID preservation;
- explicit user authorization;
- bounded input validation; and
- a controlled write-safety gate for development/test workflows.

## Portability

Contacts must preserve standards-based portability through vCard/VCF and applicable export/import workflows.

Import must:
- validate before mutation;
- make the destination explicit;
- let the user review/select imported records where applicable;
- preserve source properties where practical;
- avoid unnecessary UID replacement; and
- fail safely on malformed or unsupported data.

Export/import claims require round-trip evidence for the supported scope.

## Duplicate detection and merge

Duplicate detection and merge must remain user-reviewed and preservation-oriented.

Merge logic must not silently destroy distinct contact data. It must respect authorization, ETags/concurrency, surviving resource identity, vCard preservation, and recoverability.

## Public-profile and external-link data

Public-profile links are user-controlled contact data. Contacts must not infer, scrape, continuously monitor, or claim verification of third-party accounts merely because a profile URL is stored.

Credential-bearing or otherwise unsafe URLs must be rejected. Third-party marks are identification aids only and must not imply affiliation or verification.

## Privacy and sensitive information

Contacts handles personal and family information and must use strong minimization and disclosure controls.

Requirements include:
- no behavioral advertising or unnecessary tracking;
- data-minimized logs;
- no reusable credentials in source control or ordinary documentation;
- bounded error disclosure;
- production-family contact data prohibited from Development/test environments until explicitly approved;
- isolated synthetic identities/data for development validation where appropriate;
- privacy-safe observability; and
- Privacy Shield acceptance for applicable privacy behavior before Stable qualification.

## Security

Contacts must apply least privilege, secure sessions, CSRF/origin protections, input limits, abuse controls, safe security headers, protected secrets, dependency review, and fail-closed authorization behavior.

Wardveil Security governs applicable security authority and evidence. Application-local security checks do not independently establish Wardveil acceptance.

Multi-worker/runtime behavior must preserve shared abuse-control and session/security semantics where production topology requires it.

## Glaze UI, accessibility, and form factors

Contacts must migrate deliberately to the latest accepted Stable Glaze UI contract applicable at candidate acceptance time.

Historical and Draft references to specific Glaze versions are preserved in `PROJECT-RECORD.md`; they are not a permanent version pin.

Application-specific acceptance must include:
- purpose-built Mobile, Tablet, Desktop, and Wide Desktop behavior where applicable;
- keyboard navigation and visible focus;
- accessible names/roles/states;
- touch-friendly targets;
- scalable text and bounded long-content behavior;
- Reduced Motion and Reduced Transparency;
- Increased/forced contrast behavior;
- responsive detail/edit/import/duplicate-review workflows;
- representative browser/device validation; and
- Human Visual Excellence / rendered review where required.

## Canonical application identity

Contacts must use the approved GoreeCloud Contacts identity and canonical branding assets.

Platform/browser/package derivatives must come from the approved source artwork rather than independently diverging by client. Branding derivatives do not become independent sources of identity truth.

## Future client packaging

Native Android and Debian/Linux clients are separately acceptance-gated deliverables. Their existence must not be inferred from web-client maturity or Draft branches.

Each client requires its own architecture, permissions, protocol, packaging/signing, accessibility, update/rollback, Glaze UI, security/privacy, and release evidence.

## Backup, recovery, and continuity

Production approval requires governed backup, clean-target restore, rollback, key/secret recovery, and portability validation for authoritative Radicale data plus any necessary Contacts-owned state.

Everkeep acceptance must be established independently where applicable; ordinary export files are not a substitute for complete recovery evidence.

## Production readiness

Before production approval, Contacts must establish applicable evidence for:
- production identity/session behavior;
- secret lifecycle and rotation;
- CardDAV/Radicale interoperability;
- multi-worker correctness;
- private publication architecture;
- TLS/Caddy/network boundaries;
- monitoring and alerting;
- dependency and container/runtime validation;
- backup/restore/rollback;
- representative browser/mobile validation;
- accessibility;
- production-family data approval;
- security/privacy/platform-system acceptance;
- signing/provenance; and
- Release Candidate, production, and Stable gates.

Development source or CI alone does not establish production or Stable acceptance.

## Current accepted implementation boundary

The detailed accepted Development capability inventory is `IMPLEMENTED-FEATURES.md` at authoritative `main`.

At migration time it includes CardDAV discovery/list/detail/search, guarded ETag-backed writes, per-user Radicale-backed sign-in and isolation, expanded contact fields/workflows, VCF import/export foundations, and repository-native feature/changelog governance.

The same record explicitly excludes unmerged Android/Glaze candidate work, complete platform-system acceptance, production publication, production-family data approval, Debian packaging, controlled production signing/provenance, Release Candidate, and Stable qualification.

## Open obligations

`PLANNED-FEATURES.md` is the detailed authoritative open/partial/blocked feature inventory. This specification establishes project-level requirements and authority boundaries; it does not duplicate every work item or turn a planned row into implementation.

## Maintenance

Update this specification when project purpose, authoritative data ownership, licensing state, supported clients, authentication/security/privacy authority, portability model, Glaze requirements, deployment architecture, or acceptance gates materially change.

## Related repository documentation

- [README.md](README.md)
- [PROJECT-RECORD.md](PROJECT-RECORD.md)
- [IMPLEMENTED-FEATURES.md](IMPLEMENTED-FEATURES.md)
- [PLANNED-FEATURES.md](PLANNED-FEATURES.md)
- [CHANGELOGS.md](CHANGELOGS.md)
- [LICENSE](LICENSE)
- [BRANDING.md](BRANDING.md)
