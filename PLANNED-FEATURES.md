# GoreeCloud Contacts — Planned Features

**Record type:** Repository planned/open feature inventory  
**Repository:** `GoreeCloud/goreecloud-contacts`  
**Lifecycle:** Development  
**Migration state:** Candidate on `migration/repository-feature-records-20260922`; authoritative only after accepted merge to `main`.  
**Evidence baseline:** authoritative `main` at `4e4cd3750c2ae03c769b7c30b0253b273887a7bc`; later Draft PRs remain candidate-only.  
**Governing standard:** Standard — Repository Feature Tracking and Changelog Governance v1.0.

## Purpose and migration sources

This file carries forward open, partial, blocked, deferred, acceptance-gated, and future obligations from:
- the legacy root `FEATURE-ROADMAP.md`;
- the Drive roadmap `GoreeCloud/Feature Roadmap/GoreeCloud Contacts/FEATURE-ROADMAP.docx` (file ID `1iEju1z-62uoRMQc6GXX8kr5DazpdiZuk`);
- authoritative `main` documentation and implementation evidence.

Open Draft PRs #34–#41 are preserved as candidate evidence only. Their code or documentation must not be represented as accepted implementation until merged and verified on authoritative `main`.

## Legacy roadmap disposition

| Legacy ID | Current repository-native disposition |
| --- | --- |
| FR-001 | Superseded as an active roadmap-control row by the maintenance rules in the three repository-native records; continuous reconciliation remains required. |
| FR-002 | Continues under GoreeCloud Tasks Management when work remains actionable; it is governance, not a product feature. |
| FR-003 | Evidence-backed lifecycle control remains; repository/Drive synchronization is superseded by repository-native authority. |
| FR-010 | Partial Development foundation implemented. Preserve Radicale/CardDAV as sole authoritative contact store and standards-based portability. Production acceptance remains open. |
| FR-011 | Partial Development foundation implemented. Per-user authentication/isolation and session controls exist; target-environment Identity/session/worker/recovery acceptance remains open. |
| FR-012 | Partial Development foundation implemented. ETag/precondition write safety exists; production write acceptance remains open. |
| FR-013 | Partial Development foundation implemented. Continue first-party contact-model, groups/public-profile, search, detail/edit, and broader product/device acceptance. |
| FR-014 | Open. Duplicate detection and merge must remain user-reviewed, conflict-safe, ETag-aware, and preservation-oriented. |
| FR-015 | Partial Development foundation implemented. VCF export/import exists; broader production portability/recovery acceptance remains open. |
| FR-016 | Open. Complete deliberate current-Stable GLAZE UI migration and application-specific rendered/interaction/accessibility/responsive/device/performance/rollback/Human Visual Excellence acceptance. Draft PRs do not satisfy this gate. |
| FR-017 | Open. Preserve Mobile/Tablet/Desktop/Wide Desktop compositions, keyboard focus, touch/reachability, Reduced Motion/Transparency, Increased Contrast, forced-colors resilience, and appropriate density through migration. |
| FR-018 | Partial. Maintain canonical Contacts identity and generate browser/native/package/release/documentation derivatives from one approved master; native package derivatives remain open. |
| FR-019 | Partial Development hardening exists. Complete privacy/security/abuse/logging/credential/multi-worker controls without treating source-local safeguards as Privacy Shield or Wardveil acceptance. |
| FR-020 | Blocked/incomplete. Independently integrate and validate Manager, Privacy Shield, Wardveil Security, Everkeep, Mesh, and Identity while preserving CardDAV authority and least privilege. |
| FR-021 | Blocked/incomplete. Complete governed backup, clean-target restore, key/secret recovery, rollback, and Everkeep acceptance for authoritative Radicale data plus required Contacts state. |
| FR-022 | Planned production gate. Validate private publication architecture, TLS/cookies/CSRF, multi-worker behavior, monitoring, limits, secret/key rotation, DAVx5 coexistence, and controlled onboarding before production approval. |
| FR-023 | Planned future package. Build and accept a native Android Contacts application only through dedicated architecture, permission, CardDAV, Identity, GLAZE UI, signing/update, accessibility, and release gates. Current Draft Android work is not accepted `main` state. |
| FR-024 | Planned future package. Build and accept a Debian-native Linux Contacts package through dedicated desktop, CardDAV, GLAZE UI, packaging/signing/update/rollback, integration, accessibility, and release gates. |
| FR-025 | Open release gate. Complete representative browser/mobile acceptance, dependency and production-image validation, backup/restore/rollback evidence, signing/provenance, Release Candidate qualification, production approval, and Stable qualification on the exact accepted revision. |

## Priority open obligations

### P0 — Authority, privacy, security, and recovery
- Preserve Radicale/CardDAV as sole contact authority.
- Keep all contact mutations user-authorized, conflict-safe, and ETag/precondition protected.
- Complete Privacy Shield, Wardveil Security, Everkeep, Identity, Mesh, and Manager acceptance independently.
- Complete backup/restore, rollback, key/secret recovery, and continuity validation before production-family use.

### P0 — GLAZE UI and accessibility acceptance
- Migrate the accepted application source to the current approved GLAZE UI target without relabeling staged Draft work as accepted.
- Complete Contacts-specific rendered, keyboard, accessibility, large-text/reflow, reduced-effects, forced-colors, responsive/form-factor, representative-browser/device, performance, and visual-finish acceptance.

### P0 — Production and release
- Validate production publication at the approved service boundary.
- Validate session storage, CSRF/TLS/cookie behavior, monitoring, multi-worker operation, dependency and container/image state, rollback, and recovery.
- Complete exact-revision signing/provenance, Release Candidate, production approval, and Stable qualification.

### P1 — Product capabilities
- Complete duplicate detection and user-reviewed merge.
- Continue contact groups/public profiles and broader first-party contact workflows where authoritative requirements support them.
- Complete native Android and Debian-native package milestones only through separate acceptance gates.

## Repository-governance obligations

- Do not recreate `FEATURE-ROADMAP.md` after verified migration retirement.
- Do not recreate, synchronize, mirror, or retain a Contacts roadmap or changelog in Google Drive after the applicable source has been successfully migrated and retired.
- Keep `IMPLEMENTED-FEATURES.md`, this file, and `CHANGELOGS.md` synchronized with accepted `main` lifecycle truth.
- Preserve Draft/candidate evidence without promoting it into implemented state.

## Maintenance rule

A capability remains here until its defined implementation and acceptance scope is complete. When accepted on authoritative `main`, update `IMPLEMENTED-FEATURES.md`, reconcile the corresponding obligation here, and record the meaningful event in `CHANGELOGS.md`.