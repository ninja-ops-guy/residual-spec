"""Positive conformance tests: a compliant implementation MUST pass all of these.

Every test here runs against the reference harness stub and encodes a
normative requirement from specs/MS-00.md and specs/MS-08.md. A production
implementation binds by subclassing Harness (see reference_harness.py
docstring).
"""
import unittest

from reference_harness import Harness, JournalError


class TestExactlyOneTerminal(unittest.TestCase):  # MS-00 I-1
    def test_second_terminal_rejected(self):
        h = Harness()
        tok = h.acquire_writer_lease("w1")
        h.claim("a1", "t1", "e-claim-1")
        h.finish("a1", "FAILED", "e-fin-1")
        with self.assertRaises(JournalError):
            h.finish("a1", "VIOLATED", "e-fin-2")
        self.assertEqual(h.attempts["a1"]["terminal_state"], "FAILED")

    def test_terminal_count_exactly_one(self):
        h = Harness()
        h.claim("a1", "t1", "e-claim-1")
        h.finish("a1", "CANDIDATE", "e-fin-1")
        finals = [e for e in h.events if e["record"].get("kind") == "attempt.finished"]
        self.assertEqual(len(finals), 1)


class TestIdempotentAdmission(unittest.TestCase):  # MS-00 I-4
    def test_retry_after_ambiguous_commit_resolves_duplicate(self):
        h = Harness()
        tok = h.acquire_writer_lease("w1")
        ack1 = h.submit({"event_id": "e1", "kind": "x"}, tok)
        ack2 = h.submit({"event_id": "e1", "kind": "x"}, tok)
        self.assertEqual(ack1["disposition"], "accepted")
        self.assertEqual(ack2["disposition"], "duplicate")
        self.assertEqual((ack1["seq"], ack1["hash"]), (ack2["seq"], ack2["hash"]))
        self.assertEqual(len([e for e in h.events if e["event_id"] == "e1"]), 1)


class TestCommitBeforeAck(unittest.TestCase):  # MS-08 §2.2
    def test_ack_reflects_committed_state(self):
        h = Harness()
        tok = h.acquire_writer_lease("w1")
        ack = h.submit({"event_id": "e1", "kind": "x"}, tok)
        # acked row must be present in the committed shadow
        self.assertTrue(any(r["seq"] == ack["seq"] for r in h._committed))

    def test_stale_fencing_rejected(self):  # MS-08 §4.3
        h = Harness()
        tok1 = h.acquire_writer_lease("w1")
        tok2 = h.acquire_writer_lease("w2")
        with self.assertRaises(JournalError):
            h.submit({"event_id": "e1", "kind": "x"}, tok1)
        ack = h.submit({"event_id": "e1", "kind": "x"}, tok2)
        self.assertEqual(ack["disposition"], "accepted")

    def test_tokens_strictly_monotonic(self):
        h = Harness()
        toks = [h.acquire_writer_lease(f"w{i}") for i in range(5)]
        self.assertEqual(toks, sorted(toks))
        self.assertEqual(len(set(toks)), 5)


class TestFailClosedIntegrity(unittest.TestCase):  # MS-00 I-6
    def test_clean_chain_verifies(self):
        h = Harness()
        tok = h.acquire_writer_lease("w1")
        h.submit({"event_id": "e1", "kind": "x"}, tok)
        h.verify_chain()  # must not raise

    def test_genesis_is_zero_digest(self):
        h = Harness()
        tok = h.acquire_writer_lease("w1")
        h.submit({"event_id": "e1", "kind": "x"}, tok)
        self.assertEqual(h.events[0]["prev_hash"], "0" * 64)


class TestClaimExclusion(unittest.TestCase):  # MS-00 KP-02
    def test_second_claim_while_active_rejected(self):
        h = Harness()
        h.claim("a1", "t1", "e-claim-1")
        with self.assertRaises(JournalError):
            h.claim("a2", "t1", "e-claim-2")


if __name__ == "__main__":
    unittest.main()
