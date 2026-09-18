# Adapter Interface — ResidualBackend

> **STATUS: DESIGN (normative for adapter implementations).** Authored by the
> spec layer (Lane 1); defines the contract every drop-in RESIDUAL adapter
> (SDK backends, framework callbacks/listeners) MUST satisfy.
> Sources: `specs/ATTESTATION-VERSIONING.md`, `specs/INTEGRATION-CONTRACTS.md`,
> `GOVERNANCE.md`. Conformance: `conformance/adapters/` (ADAPTERS-CONFORMANCE
> 1.0.0) — every adapter MUST pass it.

## 1. Purpose

A team adds RESIDUAL to an existing agent framework with `pip install` and a
wrapper, without reading the core specs. The adapter is the only integration
surface: framework lifecycle events in, attestation tokens out. This document
fixes that surface so adapters are interchangeable and independently
verifiable.

## 2. The `ResidualBackend` abstract class

```python
class ResidualBackend(ABC):
    @abstractmethod
    def on_run_start(self, run_id: str, spec_id: str,
                     metadata: dict | None = None) -> None: ...

    @abstractmethod
    def on_module_call(self, run_id: str, module: str, call_id: str,
                       inputs_digest: str) -> str: ...  # verdict

    @abstractmethod
    def on_run_complete(self, run_id: str, outcome: str) -> None: ...

    @abstractmethod
    def get_attestation(self, run_id: str) -> dict: ...
```

### 2.1 Lifecycle and ordering (normative)

1. `on_run_start(run_id, ...)` MUST precede any other call for that `run_id`.
2. `on_module_call` MAY occur zero or more times while the run is open. It
   returns the synchronous gate verdict for that call:
   `PASS | FAIL | UNKNOWN | BLOCKED`.
3. `on_run_complete(run_id, outcome)` is terminal and MUST occur exactly once
   per run (MS-00 I-1). `outcome ∈ {success, error, aborted}`.
4. Implementations MUST emit ledger events in the order
   `run.started` < `module.called`* < `gate.fired`* < `run.completed` <
   `attestation.issued`, and every event MUST be hash-chained
   (genesis `'0'*64`, MS-00 I-6) and admitted idempotently
   (`event_id UNIQUE`, MS-00 I-4).

### 2.2 Gate verdicts (normative)

- The verdict vocabulary is exactly `PASS | FAIL | UNKNOWN | BLOCKED`
  (ATTESTATION-VERSIONING §2 rule 2). UNKNOWN/BLOCKED is never coerced to
  PASS (INTEGRATION-CONTRACTS invariant 8); absence/timeout is evidence, not
  success.
- A non-PASS verdict from `on_module_call` MUST additionally emit a
  `gate.fired` event carrying `gate_id`, `module`, and the verbatim verdict,
  and the run MUST be aborted (fail-closed). The firing MUST be observable by
  the caller — either as the return value or as a raised `GateFiredError`;
  silently swallowing a gate fire is a conformance failure.
- Verdicts are stored verbatim in the attestation token; readers and writers
  never retype them (AT-5).

## 3. Attestation token format

`get_attestation(run_id)` returns a token conforming to
`specs/ATTESTATION-VERSIONING.md` §2 **verbatim**; this document restates the
adapter-facing requirements:

- Fields: `attestation_id`, `spec_version`, `spec_head_sha`, `gate_version`,
  `gate_set_hash`, `implementation{repo, commit_sha, tree_sha}`,
  `evidence_manifest_hash`, `verdicts`, `issued_ns`, `issuer`,
  `prev_attestation_hash`.
- `attestation_id` is content-addressed: sha256 of the canonical JSON
  (sorted keys, minimal separators, UTF-8) of the record minus
  `attestation_id`. Tokens are immutable; corrections are new tokens linked by
  `prev_attestation_hash` (genesis `'0'*64` per lineage, AT-4).
- The attestation is admitted into the ledger as an event
  `attestation.issued` with `event_id = attestation_id` (AT-3), making
  re-issuance idempotent and dedupe-visible.
- `spec_head_sha` MUST resolve to a committed spec state; adapters MUST NOT
  mint tokens against an untagged, uncommitted spec (§2 rule 1).
- Consumers verify offline by recomputing `attestation_id`, checking field
  formats, and validating the verdict vocabulary; lineage walking and
  gate-history replay require spec-repo access and are outside the adapter.

## 4. Error semantics (fail-closed, normative)

The spec's posture is fail-closed throughout (INTEGRATION-CONTRACTS failure
semantics; MS-00 I-6; AT migration rule). Adapters MUST implement:

| Failure | Adapter behavior |
|---|---|
| **Core unreachable** (ping/transport fails at run start) | Raise `CoreUnreachableError` (or adapter equivalent) from `on_run_start`. The workload MUST NOT proceed. No events are recorded; no attestation exists. |
| **Gate fires** (non-PASS verdict) | Emit `gate.fired` with the verbatim verdict, abort the run (`outcome="aborted"`), propagate to the caller (return value or `GateFiredError`), and still issue the attestation recording the non-PASS verdict verbatim. |
| **Ledger write fails** (any event/attestation append) | Raise `LedgerWriteError` (or adapter equivalent), roll back the partial transaction (MS-00 I-2), abort the run, and issue NO attestation. Evidence that is not durably recorded is treated as never having happened. |
| **Ledger corruption detected at open** | Fail closed: hash-chain verification aborts backend startup (MS-00 I-6). Never auto-repair, never skip. |
| **Duplicate admission** | Resolve idempotently to the original `(seq, hash)` (MS-00 I-4); never error, never double-record. |

No adapter may loosen, skip, or bypass any qualification gate
(GOVERNANCE.md: gates only tighten).

## 5. Adapter-side responsibilities

An adapter (e.g. `residual-langchain`, `residual-crewai`) MUST:

1. Map framework lifecycle events onto the `ResidualBackend` calls above,
   preserving ordering per run, including under concurrency (parallel
   chains/crews get independent `run_id`s).
2. Expose the resulting attestation token to the caller
   (`attestation_for(...)` or equivalent).
3. Propagate fail-closed errors even where the host framework swallows
   callback exceptions — at minimum by recording them in a caller-inspectable
   `failures` list AND configuring the host's error propagation
   (e.g. `raise_error = True` in LangChain) where available.
4. Pass `conformance/adapters/` (ADAPTERS-CONFORMANCE 1.0.0), including its
   mutation-verified negative tests.

## 6. Reference binding

`ninja-ops-guy/residual-sdk` provides the reference implementation
(`SQLiteResidualBackend`) and the first two adapters
(`residual-langchain`, `residual-crewai`) bind through it.

## 7. Out of scope

Multi-host attestation consensus; signature schemes; revocation;
framework-specific configuration of gate sets beyond the G0 defaults.
