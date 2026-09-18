# enforcement/ — gates-only-tighten enforcement layer

Makes qualification-gate weakening expensive, visible, and reviewable.

| Path | Purpose |
|---|---|
| `gates.py` | Canonical machine-checkable gate definitions G0–G7 + fail-closed evaluator. Hash source for `gate_hash`/`gate_set_hash` (see `specs/ATTESTATION-VERSIONING.md` §2–3). Every edit is a gate-change amendment (`GOVERNANCE.md`). |
| `negative_tests/test_gate_negatives.py` | One non-vacuous MUST-FAIL configuration per gate G0–G7, plus universal-rule tests (UNKNOWN/BLOCKED never PASS; exact-head binding; no prose-only claims) and positive controls. |
| `negative_tests/LOOSENING-DEMO-OUTPUT.txt` | Captured demonstration that loosening a gate in a scratch copy breaks the corresponding negative test and trips the integrity report. |
| `GATE-AUDIT-LOG.md` | Append-only, hash-chained public log of every gate change; seeded with the v1.0.0 `added` entries for G0–G7. Entries bind to the CAS ledger per `specs/ATTESTATION-VERSIONING.md` §4. |
| `gate_integrity_report.py` | Replays the audit log, recomputes live gate hashes, flags DRIFT for any unlogged gate change; exit 1 on failure. |
| `integrity-report-v1.0.0.json` | Committed output artifact of the report at the v1.0.0 seed state (verdict PASS). |
| `PRESSURE-RESISTANCE.md` | Protocol for gate-relaxation requests: full amendment process, no temporary relaxations, precedent documentation, CI drift surfacing. |

Quick check:

```
cd enforcement/negative_tests && python3 -m unittest        # 13 tests, OK
python3 enforcement/gate_integrity_report.py                # exit 0
```

Relationship to `conformance/`: the conformance suite's negative tests
enforce the harness-level invariants (MS-00/MS-08 mutants); this directory
enforces the qualification-gate layer (G0–G7 evidence predicates). Neither
modifies the other; both are governed by `GOVERNANCE.md`.
