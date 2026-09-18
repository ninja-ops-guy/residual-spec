# Spec Versioning Policy

This repository versions the RESIDUAL specification layer with semantic
versioning. The version applies to the specification set as a whole; each
release tag snapshots every spec file.

## Version components

- **MAJOR** — incremented when a normative *invariant* changes: any change to a
  storage-enforced invariant (e.g. MS-00 I-1..I-6), a normative invariant in
  `specs/INTEGRATION-CONTRACTS.md`, a state machine's terminal semantics, or a
  hash/chain/dedupe rule. A major bump means existing implementations must be
  re-evaluated; attestations bound to the prior major version remain valid for
  that version and are never retroactively invalidated.
- **MINOR** — incremented when a new qualification *gate* is added (a new G-gate
  in `specs/qualification/G0-G7.md`, a new conformance test class, or a new
  normative requirement that an implementation could previously ignore). Gate
  tightening also requires a minor bump. Per `GOVERNANCE.md`, gates may never be
  loosened within a major version.
- **PATCH** — editorial changes only: wording, formatting, citations, added
  source references, STATUS header updates that add newly recovered material
  without changing any normative statement, and typo fixes. A patch release
  changes no conformance outcome.

## Rules

1. Every change to `specs/**` or `conformance/**` MUST include a version-bump
   note (`VERSION-BUMP: major|minor|patch — <reason>`) in the PR body, enforced
   by `.github/workflows/spec-version-check.yml`.
2. Version history is append-only: `RELEASES.md` entries are never edited or
   removed; corrections are new entries.
3. Tags are immutable. If a tag was cut in error, a new tag supersedes it; the
   erroneous tag's supersession is recorded in `RELEASES.md`.
4. Attestation tokens record the spec version they were issued under; see
   `specs/ATTESTATION-VERSIONING.md`.
5. Initial state is **v1.0.0**.

## Current version

`1.0.0` — initial extraction (see `RELEASES.md`).
