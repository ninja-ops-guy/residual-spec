# RESIDUAL Specification Layer (residual-spec)

The durable, implementation-independent specification artifact for RESIDUAL.
This repository contains:

- `specs/` — module specifications MS-00 … MS-08, the qualification plan
  `specs/qualification/G0-G7.md`, integration contracts, and storage-enforced
  invariants. Where a spec could not be fully recovered, the file carries an
  explicit `STATUS: PARTIAL` header listing exactly what is missing. Nothing
  here is fabricated.
- `specs/ATTESTATION-VERSIONING.md` — attestation token versioning design
  (spec version / gate version / implementation version, append-only gate
  history, CAS ledger schema change).
- `VERSIONING.md` — semantic versioning policy for specs
  (major = invariant change, minor = new gate, patch = editorial).
- `GOVERNANCE.md` — amendment classes, comment windows, reviewer and evidence
  requirements, and the gates-only-tighten rule.
- `conformance/` — Python conformance suite any RESIDUAL implementation must
  pass, plus a minimal reference harness stub. Negative tests genuinely
  exercise non-compliance paths; nothing passes vacuously.
- `SECOND-IMPLEMENTATION.md` — guide for an independent re-implementation,
  with per-module invariants, a feasibility ranking, and an MS-00 walkthrough.

## Provenance

Spec content was extracted from `ninja-ops-guy/residual-agent-harness` at
coordination base commit `3cff6bcd52e352a6ba048c958949a7bbb2a039eb` (main HEAD,
recorded 2026-09-19) and from these open-PR branches of that repository:

| Source branch / PR | Content recovered |
|---|---|
| `docs/ms00-run-ledger-design` (PR #285) | MS-00 run ledger design (G0/G1), crash matrix, CAS rules, migration plan |
| `swarm-e/g0-seam-graph` (PR #282) | MS-00…08 seam DAG (G0), seam contracts, seam gap report |
| `swarm-g/ms08-writer-service-design` (PR #278) | MS-08 writer service design (commit-before-ack, fencing, failure model) |
| `test/ms01-provider-resolver-vectors` (PR #284) | MS-01 provider-resolver migration map, adversarial vector contract |
| `docs/architecture-gap-audit-3cff6bc` (PR #280) | Gap audit vs MS-00…08 / G0…G7 (48-row verdict table) |
| `harness_specs/` on main | Prior spec corpus (M2/M3/M4, control plane, etc.) — see `specs/source-archive/README.md` |

Original source provenance (branches, paths, blob SHAs) is indexed under
`specs/source-archive/` so every extracted statement can be traced back without
trusting this repository's editors.

## Reading order

1. `specs/INTEGRATION-CONTRACTS.md` — cross-cutting invariants.
2. `specs/MS-00.md` → `specs/MS-08.md` → `specs/MS-01.md` → `specs/MS-02.md`
   (dependency order).
3. `specs/qualification/G0-G7.md` — gate plan.
4. `GOVERNANCE.md` + `VERSIONING.md` — how this artifact evolves.

## Longevity without trust

- Specs are versioned semantically and tagged; `v1.0.0` is the initial state
  (see `RELEASES.md`).
- Gate history is append-only; gates only tighten within a major version.
- The conformance suite runs against a public reference harness stub, so any
  outsider can execute it without access to any maintainer's infrastructure.
