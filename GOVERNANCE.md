# Governance — RESIDUAL Specification Layer

This document governs how the specifications in this repository change. It is
itself subject to these rules.

## Amendment classes

| Class | Scope | Comment window | Reviewer requirement | Evidence requirement |
|---|---|---|---|---|
| **Editorial** | Patch-level changes (wording, formatting, citations; no normative change) | 7 days | At least one reviewer who did not author the change | None beyond CI version-check |
| **Gate addition** | A new qualification gate, conformance test class, or normative requirement | 30 days | At least one reviewer who did not author the change | Conformance suite extended; positive test demonstrates the gate is satisfiable |
| **Gate tightening** | Strengthening an existing gate (stricter predicate, broader coverage) | 30 days | At least one reviewer who did not author the change | Mutation-verified tests demonstrating the tightened gate catches the intended failure class |
| **Gate removal** | Removing an existing gate | Only permitted if replaced by a strictly stronger gate that subsumes it (see below) | At least one reviewer who did not author the change | Mutation-verified tests demonstrating no weakening: the replacement fails on every failure the original caught, plus at least one new failure class |

## Gates only tighten

> Existing gates may never be loosened within a major version. A gate may be
> removed only if replaced by a strictly stronger gate that subsumes it.

**Strictly stronger** means: the replacement gate catches every failure the
original gate caught, plus at least one new failure class. Formally, if
`failures(G)` is the set of implementation behaviors that gate `G` rejects, a
replacement `G'` is strictly stronger iff `failures(G) ⊂ failures(G')` (strict
subset). Equality is not sufficient; neither is displacement (catching a
different, overlapping set).

### Mutation verification (evidence requirement)

For gate tightening and gate removal-by-replacement, the proposer must supply
mutation-verified tests: a set of deliberately non-compliant harness mutations
(failure injections) such that

1. every mutation the original gate rejected is still rejected by the
   replacement, and
2. at least one mutation passes the original gate but is rejected by the
   replacement.

Negative conformance tests in `conformance/` are the canonical vehicle: they
must actually exercise the non-compliance path and observe rejection. A test
that passes vacuously (never reaches the enforcement point) is not evidence.

## Reviewer requirement

Every amendment, of any class, requires at least one reviewer who did not
author the change. Self-approval is never sufficient. Reviewer identity is
recorded in the PR that carries the amendment.

## Procedural rules

1. The comment window opens when the amendment PR is posted and is measured in
   wall-clock days. No early merge, even with approval.
2. During the comment window, any party may lodge an objection; unresolved
   objections block the amendment until withdrawn or adjudicated by a
   non-author reviewer consensus.
3. UNKNOWN/BLOCKED outcomes are never recorded as PASS, in any gate, at any
   time.
4. First-attempt failures are retained; tests are never weakened to obtain
   green.
5. Every amendment PR carries exact base/head SHA attestation and a blob-hash
   manifest (SHA-256) of changed files.
6. No single maintainer is a point of trust: this file, `VERSIONING.md`, the
   version history in `RELEASES.md`, and the conformance suite are sufficient
   for an outsider to evaluate whether a change followed these rules.
