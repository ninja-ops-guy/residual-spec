"""Gate-level negative tests: for every gate G0-G7, a configuration that
MUST FAIL the gate.

These are the gates-only-tighten enforcement vehicle at the qualification
layer (complementing the harness-mutant negative tests in conformance/).
Each test:

  1. builds a fully compliant evidence record and asserts the gate PASSES
     (positive control — proves the gate is satisfiable, per GOVERNANCE.md
     "Gate addition" evidence requirement);
  2. mutates exactly one field into a normative violation and asserts the
     gate FAILS with the expected reason;
  3. asserts the mutated field is actually present in the evaluated record
     (anti-vacuity guard — a test that never reaches the enforcement point
     is not evidence, GOVERNANCE.md "Mutation verification").

Visible-signal property: loosening a gate definition in enforcement/gates.py
(removing a required check/flag/dependency, or weakening the evaluator)
makes the corresponding test here fail. See
enforcement/negative_tests/LOOSENING-DEMO-OUTPUT.txt for a captured
demonstration against a scratch copy.

Run:  cd enforcement/negative_tests && python3 -m unittest -v
"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gates import GATE_DEFINITIONS, evaluate_gate  # noqa: E402

HEAD = "3cff6bcd52e352a6ba048c958949a7bbb2a039eb"  # arbitrary well-formed SHA


def compliant_evidence(gate_id: str) -> dict:
    """A record that PASSES gate_id: every required check PASS, every flag at
    its required value, every dependency PASS, bound to an exact head SHA."""
    spec = GATE_DEFINITIONS[gate_id]
    return {
        "head_sha": HEAD,
        "checks": {name: "PASS" for name in spec["required_checks"]},
        "flags": dict(spec["required_flags"]),
        "dependencies": {dep: "PASS" for dep in spec["depends_on"]},
    }


class TestEveryGateHasANegativeConfiguration(unittest.TestCase):
    """One non-vacuous MUST-FAIL configuration per gate, G0-G7."""

    def _assert_negative(self, gate_id, mutate, expected_reason_fragment):
        spec = GATE_DEFINITIONS[gate_id]

        # positive control: the compliant record passes (gate is satisfiable)
        ok = compliant_evidence(gate_id)
        result = evaluate_gate(gate_id, ok)
        self.assertEqual(result["verdict"], "PASS",
                         f"{gate_id} positive control must pass: {result}")

        # negative configuration: exactly one normative violation
        bad = compliant_evidence(gate_id)
        mutate(bad, spec)
        result = evaluate_gate(gate_id, bad)
        self.assertEqual(result["verdict"], "FAIL",
                         f"{gate_id} MUST fail on this configuration")
        self.assertTrue(
            any(expected_reason_fragment in r for r in result["reasons"]),
            f"{gate_id} failure must cite {expected_reason_fragment!r}; "
            f"got {result['reasons']}")
        return bad

    # --- G0: contract suite green only because tests were edited ----------
    def test_G0_fails_when_tests_were_edited(self):
        def mutate(rec, spec):
            rec["flags"]["zero_test_edits"] = False
            assert "zero_test_edits" in rec["flags"]  # anti-vacuity
        self._assert_negative("G0", mutate, "flag_violation:zero_test_edits")

    # --- G1: KP-14 watchdog-ablation outcome diff is non-empty -------------
    def test_G1_fails_when_kp14_diff_nonempty(self):
        def mutate(rec, spec):
            rec["flags"]["kp14_watchdog_ablation_diff_empty"] = False
            assert rec["flags"]["kp14_watchdog_ablation_diff_empty"] is False
        self._assert_negative("G1", mutate,
                              "flag_violation:kp14_watchdog_ablation_diff_empty")

    # --- G2: FAIL cells requalified by weakening tests ----------------------
    def test_G2_fails_when_tests_weakened_to_obtain_green(self):
        def mutate(rec, spec):
            rec["flags"]["tests_weakened_to_obtain_green"] = True
            assert rec["flags"]["tests_weakened_to_obtain_green"] is True
        self._assert_negative("G2", mutate,
                              "flag_violation:tests_weakened_to_obtain_green")

    # --- G3: real-provider E2E not bound to exact head ----------------------
    def test_G3_fails_when_e2e_not_bound_to_exact_head(self):
        def mutate(rec, spec):
            rec["flags"]["e2e_bound_to_exact_head"] = False
            assert rec["flags"]["e2e_bound_to_exact_head"] is False
        self._assert_negative("G3", mutate,
                              "flag_violation:e2e_bound_to_exact_head")

    # --- G4: disaster/restart matrix verdict is UNKNOWN ---------------------
    def test_G4_fails_when_matrix_verdict_unknown(self):
        def mutate(rec, spec):
            rec["checks"]["disaster_restart_matrix_green"] = "UNKNOWN"
            assert rec["checks"]["disaster_restart_matrix_green"] == "UNKNOWN"
        self._assert_negative("G4", mutate,
                              "check_not_pass:disaster_restart_matrix_green=UNKNOWN")

    # --- G5: soak ran on a deterministic simulator (does not qualify) -------
    def test_G5_fails_when_soak_used_simulator(self):
        def mutate(rec, spec):
            rec["flags"]["soak_executor_real"] = False
            assert rec["flags"]["soak_executor_real"] is False
        self._assert_negative("G5", mutate, "flag_violation:soak_executor_real")

    # --- G6: secret-leakage scan BLOCKED in CI ------------------------------
    def test_G6_fails_when_secret_scan_blocked(self):
        def mutate(rec, spec):
            rec["checks"]["secret_leakage_scan_in_ci"] = "BLOCKED"
            assert rec["checks"]["secret_leakage_scan_in_ci"] == "BLOCKED"
        self._assert_negative("G6", mutate,
                              "check_not_pass:secret_leakage_scan_in_ci=BLOCKED")

    # --- G7: a dependency gate did not pass ---------------------------------
    def test_G7_fails_when_dependency_not_pass(self):
        def mutate(rec, spec):
            rec["dependencies"]["G5"] = "FAIL"
            assert rec["dependencies"]["G5"] == "FAIL"
        self._assert_negative("G7", mutate, "dependency_not_pass:G5=FAIL")


class TestUniversalGateRules(unittest.TestCase):
    """Universal rules from specs/qualification/G0-G7.md, applied to ALL gates."""

    def test_unknown_and_blocked_never_pass_any_gate(self):
        for gate_id in GATE_DEFINITIONS:
            for bad_verdict in ("UNKNOWN", "BLOCKED"):
                spec = GATE_DEFINITIONS[gate_id]
                for check in spec["required_checks"]:
                    rec = compliant_evidence(gate_id)
                    rec["checks"][check] = bad_verdict  # anti-vacuity: set, present
                    result = evaluate_gate(gate_id, rec)
                    self.assertEqual(
                        result["verdict"], "FAIL",
                        f"{gate_id}/{check}={bad_verdict} must never PASS")

    def test_missing_check_never_passes_any_gate(self):
        for gate_id in GATE_DEFINITIONS:
            spec = GATE_DEFINITIONS[gate_id]
            for check in spec["required_checks"]:
                rec = compliant_evidence(gate_id)
                del rec["checks"][check]  # absent, not merely non-PASS
                result = evaluate_gate(gate_id, rec)
                self.assertEqual(result["verdict"], "FAIL")
                self.assertIn(f"check_not_pass:{check}=MISSING", result["reasons"])

    def test_evidence_must_bind_exact_head_sha(self):
        for gate_id in GATE_DEFINITIONS:
            for bad_head in (None, "", "latest", "main", "abc123",
                             HEAD.upper(), HEAD[:-1] + "g"):
                rec = compliant_evidence(gate_id)
                rec["head_sha"] = bad_head
                result = evaluate_gate(gate_id, rec)
                self.assertEqual(result["verdict"], "FAIL",
                                 f"{gate_id} with head_sha={bad_head!r} must FAIL")
                self.assertIn("evidence_not_bound_to_exact_head_sha",
                              result["reasons"])

    def test_prose_only_claim_does_not_qualify(self):
        """A record with no machine-readable checks fails every gate."""
        for gate_id in GATE_DEFINITIONS:
            rec = {"head_sha": HEAD, "narrative": "all gates passed, trust me"}
            result = evaluate_gate(gate_id, rec)
            self.assertEqual(result["verdict"], "FAIL")


class TestPositiveControlsAllPass(unittest.TestCase):
    """Every gate is satisfiable (GOVERNANCE.md gate-addition evidence rule)."""

    def test_compliant_evidence_passes_all_gates(self):
        for gate_id in GATE_DEFINITIONS:
            result = evaluate_gate(gate_id, compliant_evidence(gate_id))
            self.assertEqual(result["verdict"], "PASS",
                             f"{gate_id}: {result['reasons']}")


if __name__ == "__main__":
    unittest.main()
