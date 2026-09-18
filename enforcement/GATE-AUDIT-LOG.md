# Gate Audit Log — append-only

This log is the public, versioned record of every change to the qualification
gate definitions (`enforcement/gates.py`, implementing
`specs/qualification/G0-G7.md`). It exists to make gate weakening expensive,
visible, and reviewable.

## Format (normative)

1. **Append-only.** Entries are never edited, reordered, or deleted.
   Corrections are new entries referencing the corrected `seq`.
2. **One entry per gate change**, in `seq` order, as a fenced ```json block
   under an `## Entry <seq>` heading.
3. **Required fields:**
   - `seq` — monotonic integer, 1-based, contiguous.
   - `timestamp` — ISO-8601 UTC.
   - `author` — identity of the amendment author.
   - `spec_version` — semver of the spec release carrying the change.
   - `gate_id` — the gate changed (G0-G7).
   - `change_class` — one of `added`, `tightened`, `replaced_by_stronger`
     (per `specs/ATTESTATION-VERSIONING.md` section 3). `loosened` and
     `removed` are NOT valid within a major version
     (`GOVERNANCE.md`: existing gates may never be loosened).
   - `rationale` — why the change is necessary.
   - `evidence_links` — PRs, mutation-verification output, conformance runs.
     For `tightened`/`replaced_by_stronger` this MUST include the
     mutation-verified test evidence required by `GOVERNANCE.md`.
   - `reviewer_signatures` — at least one reviewer who did not author the
     change (`GOVERNANCE.md` reviewer requirement).
   - `gate_hash_after` — `gates.gate_hash(gate_id)` after the change.
   - `prev_entry_hash` — `entry_hash` of entry `seq-1`; genesis is `'0'*64`.
   - `entry_hash` — SHA-256 of the canonical JSON (sorted keys, no spaces)
     of all fields above except `entry_hash` itself.
4. **CAS-ledger binding.** Each entry is admitted to the MS-00 ledger as an
   attestation event using the schema of `specs/ATTESTATION-VERSIONING.md`
   section 4: `event_id = entry_hash`, `domain='attestation'`,
   `kind='gate_change.logged'`, chained via `prev_hash` (AT-2). The
   `gate_history` sequence of ATTESTATION-VERSIONING section 3 is exactly the
   projection of this log's `(spec_version, gate_id, gate_hash_after,
   change_class)` tuples.
5. **Verification.** `enforcement/gate_integrity_report.py` replays this log:
   it recomputes every `entry_hash`, checks the `prev_entry_hash` chain,
   rejects any entry whose `change_class` is outside the valid set, and
   compares `gate_hash_after` values against the live definitions in
   `enforcement/gates.py`. Any gate state not explained by a valid log entry
   is reported as DRIFT and fails the report (and CI).

## Entries

## Entry 1 — G0 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "47698f22b6cb92128820f139958e1a9c68517199741bf3de36f20d87cad36342",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "774c665c2ad1bec42bdb8c05dd9eaf01f7b30145b91aaecc4308ddf11812c436",
  "gate_id": "G0",
  "prev_entry_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "rationale": "Initial publication of qualification gate G0 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 1,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 2 — G1 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "227171ba49f428fa2fa0f320e550ce9e8c1273e689f0da8cf562f6d622191e41",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "90596a3a0b5eb9e9251ea250a6efeff01dcce6ce464b51458a8f50b7318726f3",
  "gate_id": "G1",
  "prev_entry_hash": "47698f22b6cb92128820f139958e1a9c68517199741bf3de36f20d87cad36342",
  "rationale": "Initial publication of qualification gate G1 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 2,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 3 — G2 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "aee7c8ce4cecc60d2067f3d560eb4248e536c2cf2837d79fe5197641ad0ad137",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "2bc91efd736696c11762b64e04c70c4d350294669fa395e626a60f082c577d5e",
  "gate_id": "G2",
  "prev_entry_hash": "227171ba49f428fa2fa0f320e550ce9e8c1273e689f0da8cf562f6d622191e41",
  "rationale": "Initial publication of qualification gate G2 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 3,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 4 — G3 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "209f6137ad05ac67d2d522c929adba16d2c6c703d6d14b7a798667cd75917959",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "e72059fad35bbe11894caaf6b8b37423d32f07fcd358ee270b66abe89b34ad04",
  "gate_id": "G3",
  "prev_entry_hash": "aee7c8ce4cecc60d2067f3d560eb4248e536c2cf2837d79fe5197641ad0ad137",
  "rationale": "Initial publication of qualification gate G3 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 4,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 5 — G4 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "c5c765768f2ca2192a43cc83c056318357eb13c75f86c363a25acd8e355368a4",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "242c241628f24d7ae58530fb9b14ea07679af67c6207f4e5c2808793e24615e1",
  "gate_id": "G4",
  "prev_entry_hash": "209f6137ad05ac67d2d522c929adba16d2c6c703d6d14b7a798667cd75917959",
  "rationale": "Initial publication of qualification gate G4 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 5,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 6 — G5 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "cc3b0281969a73e46e4b0554010669b433fabc3602f08f0efabaedac19524d6c",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "9cab3fe9b645d979602607693bbb90b0666a26515463bc330fdb8f0286fb50df",
  "gate_id": "G5",
  "prev_entry_hash": "c5c765768f2ca2192a43cc83c056318357eb13c75f86c363a25acd8e355368a4",
  "rationale": "Initial publication of qualification gate G5 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 6,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 7 — G6 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "ee792e491fe275c9f544095a3c4ea2bd34053b43564d35065e14dcbcdd852607",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "24b3bbb508786955c7fba52d1fa9fd4a129a645178b7a470b035aab31ad556de",
  "gate_id": "G6",
  "prev_entry_hash": "cc3b0281969a73e46e4b0554010669b433fabc3602f08f0efabaedac19524d6c",
  "rationale": "Initial publication of qualification gate G6 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 7,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```

## Entry 8 — G7 added (spec 1.0.0)

```json
{
  "author": "lane/4-gate-enforcement (spec-layer seed)",
  "change_class": "added",
  "entry_hash": "6c913dbd41b0f28cebcc47fe919c8f569ae7975ddf15c8f858156145af4689b4",
  "evidence_links": [
    "specs/qualification/G0-G7.md",
    "GOVERNANCE.md",
    "enforcement/negative_tests/test_gate_negatives.py"
  ],
  "gate_hash_after": "bc2b721ccf99fc2d320c30b4ccbf2d54184a00de87157457784031ab87641806",
  "gate_id": "G7",
  "prev_entry_hash": "ee792e491fe275c9f544095a3c4ea2bd34053b43564d35065e14dcbcdd852607",
  "rationale": "Initial publication of qualification gate G7 under spec v1.0.0; requirements recovered per specs/qualification/G0-G7.md.",
  "reviewer_signatures": [
    "PENDING: non-author reviewer sign-off at v1.0.0 tag (GOVERNANCE.md reviewer requirement)"
  ],
  "seq": 8,
  "spec_version": "1.0.0",
  "timestamp": "2026-09-19T00:00:00Z"
}
```
