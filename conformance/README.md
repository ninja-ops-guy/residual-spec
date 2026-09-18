# Conformance Suite

Python (stdlib-only) conformance suite that any RESIDUAL implementation must
pass. Run:

```
cd conformance
python3 -m unittest test_conformance_positive test_conformance_negative -v
```

## Structure

- `reference_harness.py` — minimal in-memory reference stub implementing the
  MS-00/MS-08 normative contract surface, plus four **non-compliant mutants**
  each removing exactly one enforcement (ack-before-commit, no dedupe,
  double terminal, no chain verification).
- `test_conformance_positive.py` — positive tests: the compliant reference
  harness passes; encodes I-1, I-4, I-6, commit-before-ack, fencing, claim
  exclusion.
- `test_conformance_negative.py` — negative tests: each mutant is driven
  through its non-compliance path and the detector is proven to observe the
  violation (anti-vacuity guards assert the operation completed before
  asserting detection). These tests enforce gates-only-tighten: weakening a
  gate breaks detection and fails this suite.

## Binding a production implementation

Subclass `Harness`, override the primitives against the real store, and run
the same test modules. Binding is a one-fixture change by design.

## NOT yet verified

This suite has **not** been executed against the live implementation in
`ninja-ops-guy/residual-agent-harness`. It currently proves the contract
semantics against the reference stub only. Production binding, multi-process
contention (G0-impl writer-lease CAS), and the full KP-01..KP-18 crash matrix
remain unverified here.
