"""Negative conformance tests: non-compliant implementations MUST fail.

Each test drives a mutant harness (reference_harness.*Mutant) through the
non-compliance path and asserts the violation is OBSERVABLE — i.e. the mutant
really performs the forbidden behavior and the contract check really catches
it. These tests are the gates-only-tighten enforcement vehicle: any change
that loosens a gate must make one of these detection checks stop detecting
its mutant, which fails the suite.

Anti-vacuity guard: each test asserts the mutant completed the operation
(e.g. returned an 'accepted' ack) BEFORE asserting the violation is detected,
so a mutant that merely crashes cannot satisfy the test.
"""
import unittest

from reference_harness import (
    AckBeforeCommitHarness, DoubleTerminalHarness, Harness, JournalError,
    NoChainVerifyHarness, NoDedupeHarness,
)


def detect_ack_before_commit(h) -> bool:
    """Contract check: True iff the harness acked an uncommitted event."""
    tok = h.acquire_writer_lease("w1")
    ack = h.submit({"event_id": "e1", "kind": "x"}, tok)
    assert ack["disposition"] == "accepted"  # operation really happened
    return ack.get("_committed_at_ack") is False


def detect_no_dedupe(h) -> bool:
    """Contract check: True iff a retry produced a second accepted event."""
    tok = h.acquire_writer_lease("w1")
    ack1 = h.submit({"event_id": "e1", "kind": "x"}, tok)
    ack2 = h.submit({"event_id": "e1", "kind": "x"}, tok)
    assert ack1["disposition"] == "accepted"
    return ack2["disposition"] == "accepted" and ack2["seq"] != ack1["seq"]


def detect_double_terminal(h) -> bool:
    """Contract check: True iff two terminal transitions both succeeded."""
    h.claim("a1", "t1", "e-claim-1")
    h.finish("a1", "FAILED", "e-fin-1")
    try:
        h.finish("a1", "VIOLATED", "e-fin-2")
    except JournalError:
        return False
    return h.attempts["a1"]["terminal_state"] == "VIOLATED"


def detect_no_chain_verify(h) -> bool:
    """Contract check: True iff a tampered chain opens without error."""
    tok = h.acquire_writer_lease("w1")
    h.submit({"event_id": "e1", "kind": "x"}, tok)
    h.tamper(1)
    try:
        h.verify_chain()
    except JournalError:
        return False
    return True


class TestNegativeMutantsAreCaught(unittest.TestCase):
    # --- each mutant really exhibits its violation (non-vacuous) -----------
    def test_mutant_ack_before_commit_exhibits_violation(self):
        self.assertTrue(detect_ack_before_commit(AckBeforeCommitHarness()))

    def test_mutant_no_dedupe_exhibits_violation(self):
        self.assertTrue(detect_no_dedupe(NoDedupeHarness()))

    def test_mutant_double_terminal_exhibits_violation(self):
        self.assertTrue(detect_double_terminal(DoubleTerminalHarness()))

    def test_mutant_no_chain_verify_exhibits_violation(self):
        self.assertTrue(detect_no_chain_verify(NoChainVerifyHarness()))

    # --- the compliant reference harness passes every detector -------------
    def test_reference_harness_clean_on_all_detectors(self):
        self.assertFalse(detect_ack_before_commit(Harness()))
        self.assertFalse(detect_no_dedupe(Harness()))
        self.assertFalse(detect_double_terminal(Harness()))
        self.assertFalse(detect_no_chain_verify(Harness()))


class TestNegativeDrivesEnforcementPath(unittest.TestCase):
    """Meta-tests: prove detection is not vacuous by reaching the enforcement
    point. If a future change bypasses enforcement (e.g. finish() starts
    raising for unrelated reasons), these fail loudly instead of silently
    passing."""

    def test_double_terminal_detector_reaches_second_finish(self):
        h = DoubleTerminalHarness()
        h.claim("a1", "t1", "e-claim-1")
        ack = h.finish("a1", "FAILED", "e-fin-1")
        self.assertEqual(ack["disposition"], "accepted")
        # enforcement point reached: compliant harness must reject here
        compliant = Harness()
        compliant.claim("a1", "t1", "e-claim-1")
        compliant.finish("a1", "FAILED", "e-fin-1")
        with self.assertRaises(JournalError):
            compliant.finish("a1", "VIOLATED", "e-fin-2")

    def test_chain_detector_actually_tampers(self):
        h = NoChainVerifyHarness()
        tok = h.acquire_writer_lease("w1")
        h.submit({"event_id": "e1", "kind": "x"}, tok)
        h.tamper(1)
        self.assertTrue(h.events[1]["record"].get("_tampered"))
        # the same tamper is caught by the compliant verifier
        h2 = Harness()
        tok2 = h2.acquire_writer_lease("w1")
        h2.submit({"event_id": "e1", "kind": "x"}, tok2)
        h2.tamper(1)
        with self.assertRaises(JournalError):
            h2.verify_chain()


if __name__ == "__main__":
    unittest.main()
