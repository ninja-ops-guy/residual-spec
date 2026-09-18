# Adapter Conformance Suite (ADAPTERS-CONFORMANCE 1.0.0)

Shared suite that every RESIDUAL adapter MUST pass. Versioned independently
of the core conformance suite (see `VERSION`).

Run the self-verification (stdlib-only):

```
cd conformance/adapters
python3 -m unittest adapter_conformance_suite -v
```

## Binding your adapter

Subclass `AdapterConformanceTests`, implement `make_handle()` returning an
`AdapterHandle` that drives your adapter at the RESIDUAL event level, and run
the same class. The suite file is designed to be vendored verbatim into
adapter repos — record the SHA-256 of the vendored copy.

## What it gates

- **A-ORD-1** event ordering (`run.started` < `module.called` < `run.completed` < `attestation.issued`)
- **A-TOK-1** attestation token format (fields, content address, hash formats, verdict vocabulary)
- **A-VER-1** verdicts verbatim; UNKNOWN/BLOCKED never coerced to PASS
- **A-ERR-1** core unreachable → fail closed, zero events
- **A-ERR-2** ledger write failure → fail closed, no attestation
- **A-GATE-1** gate firing propagates to caller
- **A-LED-1** hash-chain integrity (genesis `'0'*64`)
- **A-LED-2** ledger append-only (mutation attempt rejected)
- **A-LED-3** exactly one terminal event per run
- **A-ATT-1** attestation admitted idempotently with `event_id = attestation_id`

## Mutation verification

The suite ships four deliberately non-compliant mutants
(`MUTANTS`): verdict coercion, fail-open core, swallowed gate fire, mutable
ledger. `TestMutantsRejected` proves each is detected by the suite, with
anti-vacuity guards (the compliant self-test handle must pass all gates).

## NOT yet verified

This suite verifies adapter contract semantics, not production deployments:
it does not prove durability across host crashes, multi-process contention,
or anything about non-Python adapters. Framework-event coverage for specific
frameworks lives in each adapter repo's own integration tests.
