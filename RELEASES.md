# Releases

Append-only release log. Entries are never edited or removed.

## v1.0.0 — initial extraction (2026-09-19)

- Initial standalone extraction of the RESIDUAL specification layer from
  `ninja-ops-guy/residual-agent-harness` @
  `3cff6bcd52e352a6ba048c958949a7bbb2a039eb` and open PR branches
  `docs/ms00-run-ledger-design` (#285), `swarm-e/g0-seam-graph` (#282),
  `swarm-g/ms08-writer-service-design` (#278),
  `test/ms01-provider-resolver-vectors` (#284),
  `docs/architecture-gap-audit-3cff6bc` (#280).
- Spec status: MS-00 COMPLETE (design-level), MS-08 COMPLETE (design-level),
  MS-01/MS-02 PARTIAL (recovered seam/contract material), MS-03…MS-07 PARTIAL
  (owner-directive labels only; no recoverable content).
- Qualification plan G0–G7: PARTIAL (G0/G1 detailed; G2–G7 scaffolded from the
  gap audit's gate-evidence requirements).
- Tag: the `v1.0.0` git tag SHOULD be placed on the merge commit of the
  initial `lane/3-governance` PR. If tag-object creation is unavailable to the
  extracting automation, this entry plus the PR's exact-head attestation
  constitutes the recorded tag intent, and the tag MUST be created by the first
  maintainer with push-tag capability, pointing at the exact head SHA recorded
  in the PR body.
