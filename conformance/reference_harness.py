"""Minimal reference harness stub for the RESIDUAL conformance suite.

This is NOT the production MS-00/MS-08. It is a stdlib-only, in-memory
reference implementing the normative contract surface the conformance suite
checks:

- MS-00 I-1 exactly-one-terminal (CAS on terminal_state)
- MS-00 I-2 atomic state+event
- MS-00 I-4 idempotent admission (event_id dedupe returning stored {seq, hash})
- MS-00 I-6 fail-closed hash-chain integrity (genesis '0'*64)
- MS-08 commit-before-ack ordering
- MS-08 durable fencing tokens (strictly monotonic, stale rejected)

UNVERIFIED against the live implementation: this suite has not been run
against ninja-ops-guy/residual-agent-harness. Binding to a production
implementation is a one-fixture change: subclass Harness and override the
primitives, then run conformance.test_conformance_positive against it.
"""
from __future__ import annotations

import hashlib
import json

GENESIS = "0" * 64

TERMINAL_STATES = {"CANDIDATE", "VIOLATED", "FAILED", "CANCELLED", "AUDIT_FAILED"}
PRE_TERMINAL_STATES = {"RESERVED", "RUNNING", "CANDIDATE"}


class JournalError(Exception):
    """Typed rejection of an illegal transition or stale fencing."""


def _canonical(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


class Harness:
    """Reference MS-00 ledger + MS-08 writer, in-memory."""

    def __init__(self, control_plane_id: str = "ref-0"):
        self.control_plane_id = control_plane_id
        self.events: list[dict] = []          # append-only hash chain
        self.by_event_id: dict[str, dict] = {}
        self.attempts: dict[str, dict] = {}
        self.fencing_token = 0                # durable writer token
        self._committed: list[dict] = []      # committed event shadow copy

    # --- internals -------------------------------------------------------

    def _digest(self, record: dict) -> str:
        return hashlib.sha256(_canonical(record)).hexdigest()

    def _append_event(self, event: dict) -> dict:
        seq = len(self.events) + 1
        prev = self.events[-1]["digest"] if self.events else GENESIS
        row = {"seq": seq, "event_id": event["event_id"],
               "prev_hash": prev, "record": json.loads(json.dumps(event))}
        row["digest"] = self._digest(
            {"seq": seq, "event_id": event["event_id"], "prev_hash": prev,
             "record": row["record"]})
        self.events.append(row)
        self.by_event_id[event["event_id"]] = row
        return row

    def _commit(self):
        # commit-before-ack: acks are built from committed state only.
        self._committed = list(self.events)

    def _ack(self, row: dict, disposition: str) -> dict:
        return {"seq": row["seq"], "hash": row["digest"],
                "disposition": disposition, "fencing_token": self.fencing_token,
                "reason": None}

    # --- MS-08 admission --------------------------------------------------

    def acquire_writer_lease(self, writer_id: str) -> int:
        self.fencing_token += 1
        self._append_event({"event_id": f"lease-{self.fencing_token}",
                            "kind": "control.writer_lease",
                            "writer": writer_id,
                            "fencing_token": self.fencing_token})
        self._commit()
        return self.fencing_token

    def submit(self, event: dict, fencing_token: int) -> dict:
        """Validate -> dedupe -> write -> commit -> ack (commit-before-ack)."""
        if fencing_token < self.fencing_token:
            raise JournalError("stale_fencing")
        if "event_id" not in event:
            raise JournalError("schema")
        existing = self.by_event_id.get(event["event_id"])
        if existing is not None:
            return self._ack(existing, "duplicate")
        row = self._append_event(event)
        self._commit()
        return self._ack(row, "accepted")

    # --- MS-00 attempt lifecycle ------------------------------------------

    def claim(self, attempt_id: str, task_id: str, event_id: str) -> dict:
        for a in self.attempts.values():
            if a["task_id"] == task_id and a["terminal_state"] is None:
                raise JournalError("active or quarantined")
        if attempt_id in self.attempts:
            raise JournalError("duplicate attempt_id")
        self.attempts[attempt_id] = {
            "attempt_id": attempt_id, "task_id": task_id,
            "state": "RESERVED", "terminal_state": None, "revoked": False,
        }
        row = self._append_event({"event_id": event_id, "kind": "attempt.claimed",
                                  "attempt_id": attempt_id, "task_id": task_id})
        self._commit()
        return self._ack(row, "accepted")

    def finish(self, attempt_id: str, to_state: str, event_id: str) -> dict:
        if to_state not in TERMINAL_STATES:
            raise JournalError("illegal_transition")
        a = self.attempts.get(attempt_id)
        if a is None:
            raise JournalError("unknown attempt")
        # CAS predicate: legal pre-terminal set AND terminal_state IS NULL
        if a["state"] not in PRE_TERMINAL_STATES or a["terminal_state"] is not None:
            raise JournalError("exactly-one-terminal CAS failed")
        if to_state == "CANDIDATE" and a["revoked"]:
            raise JournalError("revoked guard")
        # atomic state+event: mutate and append before commit
        a["state"] = to_state
        a["terminal_state"] = to_state
        try:
            row = self._append_event({"event_id": event_id,
                                      "kind": "attempt.finished",
                                      "attempt_id": attempt_id, "to": to_state})
        except Exception:
            a["state"] = "RESERVED"
            a["terminal_state"] = None
            raise
        self._commit()
        return self._ack(row, "accepted")

    # --- MS-00 I-6 integrity ------------------------------------------------

    def verify_chain(self) -> None:
        prev = GENESIS
        for row in self.events:
            if row["prev_hash"] != prev:
                raise JournalError("hash chain broken")
            if row["digest"] != self._digest(
                    {"seq": row["seq"], "event_id": row["event_id"],
                     "prev_hash": row["prev_hash"], "record": row["record"]}):
                raise JournalError("digest mismatch")
            prev = row["digest"]

    def tamper(self, index: int) -> None:
        """Test hook: flip one byte of a stored event record on 'disk'."""
        rec = self.events[index]["record"]
        rec["_tampered"] = True


# --- Non-compliant mutants (used ONLY by the negative conformance tests) ----
# Each mutant removes exactly one normative enforcement. Negative tests must
# observe the mutant actually performing the forbidden behavior (never
# vacuous).

class AckBeforeCommitHarness(Harness):
    """Violation of MS-08 commit-before-ack: acks uncommitted events."""

    def _ack(self, row, disposition):
        ack = super()._ack(row, disposition)
        ack["_committed_at_ack"] = row in self._committed  # observability hook
        return ack

    def submit(self, event, fencing_token):
        # ack computed BEFORE commit
        if fencing_token < self.fencing_token:
            raise JournalError("stale_fencing")
        existing = self.by_event_id.get(event["event_id"])
        if existing is not None:
            return self._ack(existing, "duplicate")
        row = self._append_event(event)
        ack = self._ack(row, "accepted")
        self._commit()
        return ack


class NoDedupeHarness(Harness):
    """Violation of MS-00 I-4: retries are admitted twice."""

    def submit(self, event, fencing_token):
        if fencing_token < self.fencing_token:
            raise JournalError("stale_fencing")
        row = self._append_event(event)  # no dedupe check
        self._commit()
        return self._ack(row, "accepted")


class DoubleTerminalHarness(Harness):
    """Violation of MS-00 I-1: second terminal transition succeeds."""

    def finish(self, attempt_id, to_state, event_id):
        a = self.attempts.get(attempt_id)
        if a is None:
            raise JournalError("unknown attempt")
        a["state"] = to_state
        a["terminal_state"] = to_state  # overwritten, no CAS
        row = self._append_event({"event_id": event_id,
                                  "kind": "attempt.finished",
                                  "attempt_id": attempt_id, "to": to_state})
        self._commit()
        return self._ack(row, "accepted")


class NoChainVerifyHarness(Harness):
    """Violation of MS-00 I-6: tampered chain opens without error."""

    def verify_chain(self) -> None:
        return None
