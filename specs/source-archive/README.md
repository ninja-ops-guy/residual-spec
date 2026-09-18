# Source Archive — Provenance Index

Extracted spec content in `../` derives from these source documents in
`ninja-ops-guy/residual-agent-harness`. Each entry records branch (open PR),
path, and git blob SHA so any outsider can re-fetch and diff without trusting
this repository's editors. Coordination base: `main@3cff6bcd52e352a6ba048c958949a7bbb2a039eb`.

| Extracted into | Source branch (PR) | Source path | Blob SHA |
|---|---|---|---|
| `specs/MS-00.md` | `docs/ms00-run-ledger-design` (#285) | `docs/architecture/MS-00-run-ledger.md` | `ac3a9a57373313bdf5483755618b5d94ced03e81` |
| `specs/MS-08.md` | `swarm-g/ms08-writer-service-design` (#278) | `docs/architecture/MS-08-writer-service.md` | `b656e0cc71425dc912606a0484bb7e6545783ae5` |
| `specs/MS-01.md`, `specs/MS-02.md`, `specs/qualification/G0-G7.md` | `swarm-e/g0-seam-graph` (#282) | `docs/architecture/SEAM-DAG.md` | `9dcc54425936112ee6d6ae9be3d123437da2c05b` |
| (gap/verdict material) | `swarm-e/g0-seam-graph` (#282) | `docs/architecture/SEAM-GAP-REPORT.md` | `70ae7eebf08d2162a61d2968593985305dec928c` |
| `specs/MS-01.md` (resolver contract, F-1..F-4) | `test/ms01-provider-resolver-vectors` (#284) | `docs/provider-resolver-migration.md` | `aa39f0de96ea2feb234234c1df9d8b7f83c11d4c` |
| `specs/MS-01.md` (executable vectors) | `test/ms01-provider-resolver-vectors` (#284) | `tests/modular/test_resolver_adversarial.py` | `f46cb30f58ef8563b358d0c22c9174150adeeea5` |
| `specs/qualification/G0-G7.md`, `SECOND-IMPLEMENTATION.md` | `docs/architecture-gap-audit-3cff6bc` (#280) | `docs/status/ARCHITECTURE-GAP-AUDIT.md` | `e53ca9bee5d813eae06e56fdf09d4b1dfd9021c4` |
| `specs/INTEGRATION-CONTRACTS.md` (verbatim §SPEC-GATEWAY) | `docs/ms00-run-ledger-design` (#285) | `docs/specs/SPEC-GATEWAY-CONTROL-PLANE-001.md` | `fe7f840f4dd973b226d92da44c4c8e109791547b` |
| (prior spec corpus, referenced not extracted) | `main` @ `3cff6bcd` | `harness_specs/` (incl. `M2_M3_M4_SPECS.md` blob `84bb2cc25b519a38e8d6388dc1032016b4119585`, `SPECS.md` blob `88fdc4f0924e7f82b681029fa777817021d1ced5`, `CONTROL_PLANE_SPECS.md` blob `2991545928401b07af886d3e525ab001bbeb15d3`) | see harness repo |

Notes:
- The MS-00 reference implementation and contract skeletons live at
  `docs/architecture/ms00/` on branch `docs/ms00-run-ledger-design`
  (`reference_ledger.py`, `tests/test_ms00_contract.py`); MS-08 reference and
  contract tests at `docs/architecture/ms08/` on branch
  `swarm-g/ms08-writer-service-design`. These are implementation-side
  artifacts and are not mirrored here; the conformance suite in
  `conformance/` supersedes them as the implementation-independent vehicle.
- The `harness_specs/` corpus (M2/M3/M4, mesh, resilience, studio, etc.)
  describes platform capabilities outside the MS-00…08 module seam structure;
  it is indexed above but not reorganized into `specs/`, to avoid fabricating
  a mapping that the source documents do not state.
