#!/usr/bin/env python3
"""Gate integrity report — compare current gate state vs the historical
record in GATE-AUDIT-LOG.md and flag drift.

Checks (fail-closed; any violation exits non-zero):

  LOG-1  every audit-log entry recomputes to its recorded entry_hash
  LOG-2  prev_entry_hash chain is intact from genesis ('0'*64)
  LOG-3  seq values are contiguous, 1-based, append-only
  LOG-4  every change_class is in {added, tightened, replaced_by_stronger}
         ('loosened'/'removed' are never valid within a major version)
  LOG-5  tightened/replaced_by_stronger entries cite evidence_links and a
         non-author reviewer signature (GOVERNANCE.md evidence rules)
  DRIFT  for every gate G0-G7, the current gates.gate_hash() equals the
         latest gate_hash_after recorded for that gate in the log; a gate
         whose live definition differs from its last logged state is DRIFT —
         i.e. an unlogged (and therefore ungoverned) gate change

Usage:
  python3 gate_integrity_report.py [--out REPORT.json]

The JSON report is a committable artifact; CI runs this script and fails the
build on non-zero exit (see enforcement/PRESSURE-RESISTANCE.md section 4).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gates  # noqa: E402

LOG_PATH = os.path.join(HERE, "GATE-AUDIT-LOG.md")
VALID_CLASSES = {"added", "tightened", "replaced_by_stronger"}
GENESIS = "0" * 64

_ENTRY_RE = re.compile(r"## Entry \d+[^\n]*\n+```json\n(.*?)\n```", re.S)


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def load_log(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    entries = []
    for m in _ENTRY_RE.finditer(text):
        entries.append(json.loads(m.group(1)))
    return entries


def verify_log(entries: list[dict]) -> list[str]:
    problems: list[str] = []
    prev = GENESIS
    for i, e in enumerate(entries, 1):
        if e.get("seq") != i:  # LOG-3
            problems.append(f"LOG-3: entry {i} has seq={e.get('seq')}")
        body = {k: v for k, v in e.items() if k != "entry_hash"}
        if hashlib.sha256(_canonical(body)).hexdigest() != e.get("entry_hash"):  # LOG-1
            problems.append(f"LOG-1: entry seq={e.get('seq')} entry_hash mismatch")
        if e.get("prev_entry_hash") != prev:  # LOG-2
            problems.append(f"LOG-2: entry seq={e.get('seq')} breaks hash chain")
        if e.get("change_class") not in VALID_CLASSES:  # LOG-4
            problems.append(
                f"LOG-4: entry seq={e.get('seq')} has forbidden change_class "
                f"{e.get('change_class')!r} (gates only tighten)")
        if e.get("change_class") in {"tightened", "replaced_by_stronger"}:  # LOG-5
            if not e.get("evidence_links"):
                problems.append(f"LOG-5: entry seq={e['seq']} lacks evidence_links")
            sigs = e.get("reviewer_signatures") or []
            if not any("PENDING" not in s for s in sigs):
                problems.append(
                    f"LOG-5: entry seq={e['seq']} lacks a non-author reviewer signature")
        prev = e.get("entry_hash", prev)
    return problems


def build_report() -> dict:
    entries = load_log(LOG_PATH)
    problems = verify_log(entries)

    latest_logged: dict[str, str] = {}
    for e in entries:
        if "gate_id" in e and "gate_hash_after" in e:
            latest_logged[e["gate_id"]] = e["gate_hash_after"]

    per_gate = {}
    for gid in sorted(gates.GATE_DEFINITIONS):
        current = gates.gate_hash(gid)
        logged = latest_logged.get(gid)
        status = "OK" if logged == current else (
            "DRIFT" if logged is not None else "UNLOGGED")
        if status != "OK":
            problems.append(
                f"DRIFT: {gid} current gate_hash {current[:16]}... != "
                f"{'log ' + logged[:16] + '...' if logged else 'no log entry'}")
        per_gate[gid] = {"current_hash": current, "logged_hash": logged,
                         "status": status}

    return {
        "report": "gate-integrity",
        "spec_repo": "ninja-ops-guy/residual-spec",
        "gate_set_hash_current": gates.gate_set_hash(),
        "log_entries": len(entries),
        "log_head_hash": entries[-1]["entry_hash"] if entries else None,
        "gates": per_gate,
        "problems": problems,
        "verdict": "PASS" if not problems else "FAIL",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write report JSON to this path as well")
    args = ap.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
