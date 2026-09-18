# Pressure Resistance Protocol

The verification substrate (`enforcement/gates.py`,
`enforcement/negative_tests/`, `conformance/`) will come under adoption
pressure: a gate blocks a release, an integrator asks for "just this once"
relief, a deadline makes a BLOCKED look like a PASS. This document specifies
how such requests are handled. It is governed by `GOVERNANCE.md` like
everything else in this repo.

## 1. Gate-relaxation requests are full spec amendments

There is no lightweight path. Any request that would weaken a gate —
removing a required check, accepting a weaker verdict, narrowing coverage,
retyping UNKNOWN/BLOCKED — is a **gate-change amendment** under
`GOVERNANCE.md` and must carry:

- the 30-day comment window (measured in wall-clock days; no early merge);
- at least one reviewer who did not author the change;
- mutation-verified evidence that no weakening occurs
  (`GOVERNANCE.md` "Mutation verification");
- an `enforcement/GATE-AUDIT-LOG.md` entry with rationale and evidence links.

Within a major version the only permissible outcomes are `tightened` or
`replaced_by_stronger`. A request for loosening is therefore expected to be
rejected; the burden of proof sits entirely on the proposer, and the proof
standard (strict subsumption of failure sets) is defined in
`GOVERNANCE.md` "Gates only tighten".

## 2. No temporary relaxations

There is no such thing as a temporary gate relaxation. Specifically:

- **No waivers.** A release either passes the gate set at its exact head or
  it is not qualified. "Waiver with follow-up" is a loosening with extra
  steps and is not permitted.
- **No feature flags / config escapes.** The evaluator in
  `enforcement/gates.py` has no override mechanism; adding one is itself a
  gate-loosening amendment and will be flagged by the integrity report
  (the gate definition hash changes).
- **No verdict retyping.** UNKNOWN/BLOCKED is never recorded as PASS
  (`GOVERNANCE.md` procedural rule 3; `specs/ATTESTATION-VERSIONING.md`
  AT-5). The universal negative tests in
  `enforcement/negative_tests/test_gate_negatives.py` fail any evaluator
  change that permits this.
- **No expiry.** Gates do not lapse. A stale attestation is evidence about
  an old head, not a weakening of the gate.

## 3. Historical-precedent documentation requirement

Every gate-relaxation request — accepted or rejected — is documented so that
precedent is visible and cannot be quietly set:

1. The request and its disposition are recorded in the amendment PR, which
   carries exact base/head SHA attestation and a SHA-256 blob manifest
   (`GOVERNANCE.md` procedural rule 5).
2. Accepted changes (only `tightened`/`replaced_by_stronger`) are appended
   to `enforcement/GATE-AUDIT-LOG.md`, hash-chained, and admitted to the CAS
   ledger per `specs/ATTESTATION-VERSIONING.md` §4.
3. Rejected requests are recorded by closing the amendment PR unmerged with
   the objection resolution stated; the PR remains the public precedent.
4. First-attempt failures are retained (`GOVERNANCE.md` procedural rule 4).
   A gate that blocked a release and was later satisfied is a success story
   of the process, not an argument against the gate.

## 4. How drift surfaces in CI

`enforcement/gate_integrity_report.py` is the automated tripwire. It
recomputes every gate hash from `enforcement/gates.py`, replays the audit
log's hash chain, and FAILs (exit 1) when:

- any gate's live definition differs from its last logged state (DRIFT —
  an unlogged gate change, i.e. a change that bypassed governance);
- any log entry has an invalid `change_class` (`loosened`/`removed`);
- the log's hash chain is broken or an entry hash does not recompute;
- a tightening/replacement entry lacks evidence links or a non-author
  reviewer signature.

The CI workflow that runs this on every push and PR is provided verbatim in
the pull request that introduces this directory (the pushing token lacks
`workflow` scope, so the YAML cannot be committed to `.github/workflows/`
by automation; a maintainer with workflow scope installs it unchanged).
Until that workflow lands, the required local gate is:

```
python3 enforcement/gate_integrity_report.py          # must exit 0
cd enforcement/negative_tests && python3 -m unittest  # must be OK
cd conformance && python3 -m unittest test_conformance_positive test_conformance_negative
```

## 5. What this protocol does not claim

- It does not prevent a maintainer with write access from rewriting history;
  it makes any such act detectable by any outsider via the hash chain, the
  blob manifests, and the CAS ledger binding (`GOVERNANCE.md` rule 6: no
  single maintainer is a point of trust).
- The negative tests and evaluator currently run against the spec-layer
  reference definitions, not the live `residual-agent-harness`
  implementation; binding is a fixture change per
  `conformance/reference_harness.py`.
