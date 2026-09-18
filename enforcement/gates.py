"""Canonical, machine-checkable qualification gate definitions G0-G7.

This module is the enforcement-layer source of truth for what each
qualification gate REQUIRES. It encodes the normative requirements of
specs/qualification/G0-G7.md as data (required checks, required flags,
gate dependencies) plus a deterministic evaluator.

Governance binding (GOVERNANCE.md, "Gates only tighten"):
  Existing gates may never be loosened within a major version. A gate may be
  removed only if replaced by a strictly stronger gate that subsumes it.

Consequently EVERY edit to GATE_DEFINITIONS is a gate-change amendment:
  - adding a required check/flag/dependency  -> "tightened"
  - removing or renaming one                  -> NOT PERMITTED within a major
                                                 version (that is loosening)
  - replacing a gate                          -> "replaced_by_stronger" with
                                                 mutation-verified subsumption
                                                 evidence (GOVERNANCE.md)
Any change must be recorded in enforcement/GATE-AUDIT-LOG.md and is detected
by enforcement/gate_integrity_report.py.

Hashing: gate_hash and gate_set_hash below are the values referenced by
specs/ATTESTATION-VERSIONING.md sections 2-3 (gate_version, gate_set_hash,
gate_history entries). They are computed over the canonical JSON of the
definition, so any textual change to a definition changes its hash.

NOTE: G2-G7 exit criteria are scaffolded (specs/qualification/G0-G7.md marks
them MISSING pending recovery of PR #152). The requirements encoded here are
strictly those stated in recovered documents; when PR #152 lands, its
definitions are merged per the "Recovery action" in G0-G7.md and any
divergence is a gate-change amendment.
"""
from __future__ import annotations

import hashlib
import json
import re

VALID_VERDICTS = ("PASS", "FAIL", "UNKNOWN", "BLOCKED")
# GOVERNANCE.md procedural rule 3: UNKNOWN/BLOCKED are never recorded as PASS.
_PASS = "PASS"

_HEAD_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Each gate definition:
#   spec_ref        anchor into specs/qualification/G0-G7.md
#   summary         one-line recovered requirement
#   required_checks evidence check names; each must be present in the evidence
#                   record with verdict exactly "PASS"
#   required_flags  boolean/string evidence fields that must equal the given
#                   value (normative disqualifiers, e.g. G5's "deterministic
#                   simulator results do not qualify")
#   depends_on      gates that must all carry verdict PASS in the record's
#                   "dependencies" map
GATE_DEFINITIONS: dict[str, dict] = {
    "G0": {
        "spec_ref": "specs/qualification/G0-G7.md#g0--durable-ledger-core",
        "summary": ("Durable ledger core + admission: contract suite green "
                    "against the reference with zero test edits; seam DAG "
                    "resolved; KP-01..08 and KP-15..17 green."),
        "required_checks": [
            "contract_suite_green",
            "seam_dag_resolved_or_exempted",
            "kp_01_08_green",
            "kp_15_17_green",
        ],
        "required_flags": {"zero_test_edits": True},
        "depends_on": [],
    },
    "G1": {
        "spec_ref": "specs/qualification/G0-G7.md#g1--reconciliation-and-writer-service",
        "summary": ("Reconciliation (KP-11..13, KP-18) + projection determinism "
                    "+ control.reconciled evidence; MS-08 writer service: "
                    "lease CAS under contention, stale-fencing rejection, "
                    "KP-14 watchdog-ablation diff == []."),
        "required_checks": [
            "kp_11_13_green",
            "kp_18_green",
            "projection_determinism_proof",
            "control_reconciled_evidence",
            "writer_lease_cas_under_contention",
            "stale_fencing_rejection",
        ],
        "required_flags": {"kp14_watchdog_ablation_diff_empty": True},
        "depends_on": ["G0"],
    },
    "G2": {
        "spec_ref": "specs/qualification/G0-G7.md#g2--production-control-closure",
        "summary": ("Restart terminal-state preservation and "
                    "no-duplicate-external-action rewired onto the ledger; "
                    "retained FAIL cells #207/#212 requalified WITHOUT "
                    "weakening tests; schema migration strategy. "
                    "(Scaffolded; detailed exit criteria MISSING.)"),
        "required_checks": [
            "restart_terminal_state_preservation_on_ledger",
            "no_duplicate_external_action_on_ledger",
            "fail_cell_207_stress_b1_requalified",
            "fail_cell_212_usage_accounting_requalified",
            "schema_migration_strategy",
        ],
        "required_flags": {"tests_weakened_to_obtain_green": False},
        "depends_on": ["G1"],
    },
    "G3": {
        "spec_ref": "specs/qualification/G0-G7.md#g3--provider-contract-closure",
        "summary": ("Provider-resolver canonical contract landed "
                    "(F-1..F-4 closed); real-provider E2E evidence bound to "
                    "exact head. (Scaffolded.)"),
        "required_checks": [
            "provider_findings_f1_f4_closed",
            "real_provider_e2e_evidence",
        ],
        "required_flags": {"e2e_bound_to_exact_head": True},
        "depends_on": ["G2"],
    },
    "G4": {
        "spec_ref": "specs/qualification/G0-G7.md#g4--recovery-and-resilience",
        "summary": ("Integrated recovery suite against the reconciled ledger; "
                    "host-loss/recovery evidence retained; disaster/restart "
                    "matrix green at exact head. (Scaffolded.)"),
        "required_checks": [
            "integrated_recovery_suite_green",
            "host_loss_recovery_evidence_retained",
            "disaster_restart_matrix_green",
        ],
        "required_flags": {"matrix_run_at_exact_head": True},
        "depends_on": ["G3"],
    },
    "G5": {
        "spec_ref": "specs/qualification/G0-G7.md#g5--soak-and-determinism",
        "summary": ("D0-D4 determinism classes defined and applied; 24h/72h "
                    "wall-clock soak with a REAL executor (deterministic "
                    "simulator results do not qualify); orchestration-overhead "
                    "measurement. (Scaffolded.)"),
        "required_checks": [
            "d0_d4_classes_applied",
            "soak_24h_72h_executed",
            "orchestration_overhead_measured",
        ],
        "required_flags": {"soak_executor_real": True},
        "depends_on": ["G4"],
    },
    "G6": {
        "spec_ref": "specs/qualification/G0-G7.md#g6--observability-and-security",
        "summary": ("SLO compliance evidence; bounded-cardinality metrics; "
                    "telemetry-failure isolation; secret-leakage scan in CI; "
                    "health-endpoint separation; bounded queues/backpressure; "
                    "graceful drain. (Scaffolded.)"),
        "required_checks": [
            "slo_compliance_evidence",
            "bounded_cardinality_metrics",
            "telemetry_failure_isolation",
            "secret_leakage_scan_in_ci",
            "health_endpoint_separation",
            "bounded_queues_backpressure",
            "graceful_drain",
        ],
        "required_flags": {},
        "depends_on": ["G5"],
    },
    "G7": {
        "spec_ref": "specs/qualification/G0-G7.md#g7--release-candidate-freeze",
        "summary": ("Frozen RC lane with all exit criteria checked; exact-head "
                    "CI PASS at the RC commit; artifact freeze; maintainer "
                    "attestation. Depends on G0-G6. (Scaffolded.)"),
        "required_checks": [
            "rc_lane_frozen_all_criteria_checked",
            "ci_pass_at_rc_commit",
            "artifact_freeze_bound_to_commit",
            "maintainer_attestation",
        ],
        "required_flags": {},
        "depends_on": ["G0", "G1", "G2", "G3", "G4", "G5", "G6"],
    },
}


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def gate_hash(gate_id: str) -> str:
    """Content hash of one gate definition (ATTESTATION-VERSIONING §3)."""
    return hashlib.sha256(_canonical({gate_id: GATE_DEFINITIONS[gate_id]})).hexdigest()


def gate_set_hash() -> str:
    """Content hash of the full gate set (ATTESTATION-VERSIONING §2)."""
    return hashlib.sha256(_canonical(GATE_DEFINITIONS)).hexdigest()


def evaluate_gate(gate_id: str, evidence: dict) -> dict:
    """Evaluate one gate against a qualification evidence record.

    evidence record shape:
      {
        "head_sha": "<40-hex git SHA the evidence is bound to>",
        "checks":   {"<check_name>": "PASS|FAIL|UNKNOWN|BLOCKED", ...},
        "flags":    {"<flag_name>": <value>, ...},
        "dependencies": {"G0": "PASS|FAIL|UNKNOWN|BLOCKED", ...}
      }

    Returns {"gate": gate_id, "verdict": "PASS"|"FAIL", "reasons": [str]}.
    Fail-closed: any missing, unknown, or malformed input is a FAIL with a
    named reason. UNKNOWN/BLOCKED is never coerced to PASS.
    """
    if gate_id not in GATE_DEFINITIONS:
        raise KeyError(f"unknown gate {gate_id!r}")
    spec = GATE_DEFINITIONS[gate_id]
    reasons: list[str] = []

    head = evidence.get("head_sha")
    if not (isinstance(head, str) and _HEAD_SHA_RE.match(head)):
        reasons.append("evidence_not_bound_to_exact_head_sha")

    checks = evidence.get("checks") or {}
    for name in spec["required_checks"]:
        verdict = checks.get(name)
        if verdict != _PASS:
            reasons.append(
                f"check_not_pass:{name}="
                f"{verdict if verdict in VALID_VERDICTS else 'MISSING'}")

    flags = evidence.get("flags") or {}
    for name, expected in spec["required_flags"].items():
        actual = flags.get(name, "<MISSING>")
        if actual != expected:
            reasons.append(f"flag_violation:{name}={actual!r} (required {expected!r})")

    deps = evidence.get("dependencies") or {}
    for dep in spec["depends_on"]:
        verdict = deps.get(dep)
        if verdict != _PASS:
            reasons.append(
                f"dependency_not_pass:{dep}="
                f"{verdict if verdict in VALID_VERDICTS else 'MISSING'}")

    return {"gate": gate_id,
            "verdict": _PASS if not reasons else "FAIL",
            "reasons": reasons}


def evaluate_all(evidence: dict) -> dict[str, dict]:
    """Evaluate every gate G0-G7 against one evidence record."""
    return {gid: evaluate_gate(gid, evidence) for gid in sorted(GATE_DEFINITIONS)}
