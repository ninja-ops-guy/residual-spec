# Attestation Token Versioning — Design Spec

> **STATUS: DESIGN (normative for future implementation).** This document is
> authored by the spec layer; it does not modify any implementation repository.
> It defines how attestation tokens record spec version, gate version, and
> implementation version, and specifies the CAS ledger schema change required
> to store them. This design feeds the implementation repo later.

## 1. Purpose

An attestation token asserts: "implementation `I` at commit `C` passed
qualification gate set `G` of specification version `S`." Consumers must be
able to verify, offline, which spec/gate version issued an attestation, and
must be able to detect any retroactive gate weakening.

## 2. Attestation token record

```json
{
  "attestation_id": "sha256 of canonical form of this record minus this field",
  "spec_version": "1.0.0",
  "spec_head_sha": "<git commit SHA of residual-spec at issue time>",
  "gate_version": "G0@1.0.0",
  "gate_set_hash": "sha256 of canonical JSON of the gate definitions applied",
  "implementation": {
    "repo": "ninja-ops-guy/residual-agent-harness",
    "commit_sha": "<40-hex>",
    "tree_sha": "<40-hex>"
  },
  "evidence_manifest_hash": "sha256 of the machine-readable evidence manifest",
  "verdicts": {"G0": "PASS", "KP-01": "PASS", "...": "..."},
  "issued_ns": 1234567890,
  "issuer": "<identity of issuing verifier>",
  "prev_attestation_hash": "sha256 of previous attestation for same implementation lineage, or '0'*64"
}
```

Normative rules:

1. `spec_version` and `gate_version` are copied from the spec repo state at
   issue time; the issuer MUST resolve `spec_head_sha` and MUST NOT issue
   against an untagged, uncommitted spec state.
2. `verdicts` values are drawn from `PASS | FAIL | UNKNOWN | BLOCKED`.
   UNKNOWN/BLOCKED is never coerced to PASS.
3. Token identity is content-addressed (`attestation_id`); the token is
   immutable once issued. Corrections are new tokens linked via
   `prev_attestation_hash`, never edits.
4. A consumer verifies a token by: recomputing `attestation_id`; checking
   `spec_head_sha` is an ancestor of (or equal to) a tagged spec release;
   recomputing `gate_set_hash` from the gate definitions at that spec commit;
   and walking `prev_attestation_hash` to confirm lineage continuity.

## 3. Gate version history (append-only)

- Each spec release publishes `gate_history`: an append-only sequence of
  entries `(spec_version, gate_id, gate_hash, change_class)` where
  `change_class ∈ {added, tightened, replaced_by_stronger}` per
  `GOVERNANCE.md`. `loosened` and `removed` are not valid classes within a
  major version.
- The history is hash-chained: each entry carries `prev_entry_hash`; genesis is
  `'0'*64`.
- Verification rule: a consumer rejecting retroactive weakening replays the
  chain and asserts every entry's class is in the valid set and, for
  `replaced_by_stronger`, that the subsumption evidence reference is present.

## 4. CAS ledger schema change (normative)

The MS-00 ledger gains one table and one events payload kind. This is the only
schema delta; no existing table is altered (MS-00 I-1..I-6 unchanged).

### 4.1 `attestations` (append-only)

```sql
CREATE TABLE attestations (
  seq                   INTEGER PRIMARY KEY AUTOINCREMENT,
  attestation_id        TEXT UNIQUE NOT NULL,    -- content hash (§2)
  spec_version          TEXT NOT NULL,           -- semver of spec layer
  spec_head_sha         TEXT NOT NULL,           -- 40-hex git commit
  gate_version          TEXT NOT NULL,
  gate_set_hash         TEXT NOT NULL,           -- [0-9a-f]{64}
  impl_repo             TEXT NOT NULL,
  impl_commit_sha       TEXT NOT NULL,           -- 40-hex
  impl_tree_sha         TEXT NOT NULL,           -- 40-hex
  evidence_manifest_hash TEXT NOT NULL,          -- [0-9a-f]{64}
  verdicts_json         TEXT NOT NULL,           -- canonical JSON
  issuer                TEXT NOT NULL,
  issued_ns             INTEGER NOT NULL,
  prev_attestation_hash TEXT NOT NULL,           -- '0'*64 genesis per lineage
  digest                TEXT UNIQUE NOT NULL,    -- sha256 of canonical row
  prev_hash             TEXT NOT NULL            -- chain link within this table
);
-- UPDATE/DELETE forbidden by trigger (same discipline as MS-00 events).
```

Invariants:

- **AT-1 Append-only.** Attestation rows are never updated or deleted
  (trigger-enforced, same mechanism as `events`).
- **AT-2 Chain integrity.** `prev_hash` chains `digest`s in `seq` order;
  verification at ledger open runs with the MS-00 I-6 hash-chain check.
- **AT-3 Admission through MS-08.** Attestation inserts are ordinary
  `propose` events (`domain='attestation'`, `kind='attestation.issued'`) with
  `event_id = attestation_id`; idempotent admission (MS-00 I-4) makes
  re-issuance safe and dedupe-visible.
- **AT-4 Lineage.** For a given `(impl_repo, implementation lineage)`,
  `prev_attestation_hash` forms a per-lineage chain; the first attestation in a
  lineage uses `'0'*64`.
- **AT-5 No verdict retyping.** `verdicts_json` is stored verbatim; readers
  never coerce UNKNOWN/BLOCKED.

### 4.2 Migration

Pure `CREATE TABLE` + trigger addition; `metadata.schema_version` bumps via a
CAS `UPDATE metadata SET value=:v WHERE key='schema_version' AND value=:old`
inside one `BEGIN IMMEDIATE` transaction with a `control.schema_migrated`
event append (MS-00 I-2). Existing ledgers without the table are readable;
attestation admission is rejected with `schema` reason until migrated
(fail closed, never auto-migrated mid-stream).

## 5. Out of scope

Multi-host attestation consensus; revocation lists (corrections are superseding
tokens); signature schemes (a signing layer MAY wrap `attestation_id` but is
not specified here).
