# Second Implementation Guide

How to independently re-implement RESIDUAL from this specification layer, and
how to prove the result without trusting the original maintainers.

## Per-module precise invariants

### MS-00 — Durable ledger core
- I-1 Exactly-one-terminal, storage-enforced: `terminal_state IS NULL` CAS in
  the same `BEGIN IMMEDIATE` transaction as the terminal event append; partial
  unique index `one_candidate_per_task`.
- I-2 Atomic state+event: one transaction per mutation; no ack before commit;
  no commit without event append.
- I-3 Projection reconstruction from `events` alone under
  argmax(fencing_token, writer, event_id); startup disagreement ⇒ abort.
- I-4 Idempotent admission via `event_id`; retry ⇒ `duplicate` with original
  `(seq, hash)`.
- I-5 Tri-state lease reads; `unknown` never retyped, never authorizes.
- I-6 Hash-chain verified at open; genesis `'0'*64`; corruption aborts startup.
- Storage discipline: SQLite WAL, `synchronous=FULL`, `BEGIN IMMEDIATE`,
  bounded busy budgets (writer ≤1.0s), 0o700/0o600 files.

### MS-08 — Admission & fencing
- Single writer holding a durable, strictly-monotonic fencing token (well-known
  row `('__control__','writer')`); renewal bumps the token; stale tokens
  rejected at the writer AND by storage CAS (defense in depth).
- Commit-before-ack; ambiguous COMMIT ⇒ discard connection, reconcile.
- Typed rejections only: `schema|ownership|stale_fencing|cas_conflict|
  illegal_transition|lease_lost|writer_unavailable`; never coerce to accepted.
- Takeover runs full reconciliation before accepting proposals; lease-table
  loss ⇒ `FENCING_UNAVAILABLE` epoch; single host only.

### MS-01 — Lifecycle orchestration / provider resolver
- Startup reconciliation per MS-00 §8 (interrupted ⇒ `FAILED`/
  `AUDIT_FAILED`, never manufactured success; jobs ⇒ `interrupted`, never
  auto-resumed).
- Resolver: single entry point; parse = dispatchable; kind↔host pinning;
  credential handles total (`clear` = absent from every source); exact
  loopback set; ≤5 distinct failover candidates; no mid-stream model switch;
  stable identity hashing; no implicit aliasing.

### MS-02 — Resolution & registry
- One receipt per attempt; fail-closed unknown provider; frozen module
  registry; manifest-hashed registry wired into the MS-01 event chain
  (manifest schema not yet specified — see MS-02.md STATUS).
- May not import MS-08; consumed by MS-01 only.

### MS-03 … MS-07
Not recoverable (see per-file STATUS headers). Do not guess; recover from the
spec owners first.

## Feasibility ranking for independent re-implementation

| Rank | Module | Feasibility | Why |
|---|---|---|---|
| 1 | MS-00 | HIGH | Complete design spec, full schema + CAS SQL + crash matrix + conformance stub here |
| 2 | MS-08 | HIGH | Complete API/failure model; depends on MS-00 |
| 3 | MS-01 | MEDIUM | Resolver contract complete; orchestration state-machine tables not recovered |
| 4 | MS-02 | MEDIUM-LOW | Seam contract recovered; registry manifest schema missing |
| 5–9 | MS-03…07 | BLOCKED | No content recovered; requires owner recovery |

## Walkthrough: MS-00 control store as the reference exercise

1. **Read** `specs/MS-00.md` §Schema and §CAS SQL. Create the four tables
   (`metadata`, `events`, `attempts`, `lease_generations`) exactly as written,
   with the append-only triggers on `events`.
2. **Implement** `claim`, `finish`, `submit` against the CAS SQL verbatim;
   assert `cursor.rowcount == 1` and roll back otherwise.
3. **Run the conformance suite** (`conformance/`) by subclassing
   `reference_harness.Harness` over your SQLite store. Positive tests must pass;
   then run the four mutant detectors against your store — all must report
   clean.
4. **Crash matrix**: implement KP-01..KP-08, KP-15..KP-17 as fault-injection
   tests (kill between COMMIT and ack; double-finish race ≥100 interleavings;
   byte-flip tamper). Expected typed outcomes are in the MS-00 crash matrix.
5. **Reconciliation**: implement §8 Steps 0–6; prove idempotent re-run and
   projection determinism (two runs agree exactly).
6. **Attestation**: emit an attestation token per
   `specs/ATTESTATION-VERSIONING.md` binding your commit SHA to the gate set
   you passed.

You have a conformant MS-00 when: conformance suite green, KP rows green,
and a second terminal transition is impossible even with a malicious writer.

## Contributor invitation

Independent implementations are explicitly invited. If you build one, open an
issue here with your repo URL and attestation token; conformance results are
reviewable by anyone using this suite.

**90-day fallback note:** if no maintainer of this repository responds within
90 days, contributors may fork this repository and continue under the same
GOVERNANCE.md and VERSIONING.md rules unmodified — the governance rules are
themselves the continuity mechanism, and a fork that weakens them is not a
RESIDUAL spec successor. Attestation consumers should treat the fork's
`gate_history` chain as authoritative only if it extends the chain from this
repository's last tagged release without invalid entries.
