"""REV-021 regression ledger: the prereg §8 gate must be a property of the CORPUS,
not of its argument (REV-LANE #015 §2; P20 — an invariance check must be invariant
to the transformation it certifies; KB #018 exhibit 1 — absence refuses, never passes).
"""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "benchmark", "oracle_run"))

import common  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.path.isdir(common.TASKS_DIR), reason="oracle corpus not present")


def _all_pass_tasks():
    tasks = common.discover_tasks(split=None, include_pilot=True)
    return [t for t in tasks
            if t["verdict"] and str(t["verdict"].get("verdict", "")).upper() == "PASS"]


def test_gate_refuses_empty():
    """Zero tasks is vacuously clean and vacuous truth does not run studies."""
    with pytest.raises(RuntimeError, match="REV-021"):
        common.require_clean_ledger([])


def test_gate_refuses_subset_census():
    """An all-PASS subset must not read CLEAN while ledger-PASS siblings of the same
    split sit on disk outside the handed list."""
    tasks = _all_pass_tasks()
    assert len(tasks) >= 2, "corpus too small to exercise the subset check"
    subset = tasks[:-1]
    dropped_id = tasks[-1]["id"]
    with pytest.raises(RuntimeError, match=dropped_id):
        common.require_clean_ledger(subset)


def test_gate_passes_full_pass_census():
    """The legitimate full-run call: every ledger-PASS task of the handed splits present.
    A WRITTEN FAIL is a recorded rejection, excluded from the census; a MISSING verdict is not
    (see the absence tests below — GAUGE #007)."""
    tasks = _all_pass_tasks()
    st = common.require_clean_ledger(tasks)
    assert st["clean"] and not st["fail_ids"] and not st["missing_ids"]
    assert len(st["pass_ids"]) == len(tasks)


# ── GAUGE #007: the census guards ABSENCE, not only presence (my GAUGE #006 finding + CDX #010 fixtures) ──
import json as _json


def _corpus(root, tasks):
    """Build a temp corpus. tasks: list of (tid, split, verdict) where verdict is 'PASS'/'FAIL',
    None (no verdict.json written = absent receipt), or 'CORRUPT' (unreadable JSON)."""
    for tid, split, verdict in tasks:
        d = os.path.join(root, tid)
        os.makedirs(d)
        with open(os.path.join(d, "meta.json"), "w") as f:
            _json.dump({"id": tid, "split": split}, f)
        if verdict == "CORRUPT":
            with open(os.path.join(d, "verdict.json"), "w") as f:
                f.write("{not valid json")
        elif verdict is not None:
            with open(os.path.join(d, "verdict.json"), "w") as f:
                _json.dump({"task_id": tid, "verdict": verdict}, f)
    return root


def test_gate_refuses_missing_verdict_absence(tmp_path):
    # A PASS task that silently loses its verdict.json must REFUSE, not vanish — the exact
    # claims-are-not-receipts silent-drop the rev2 rebuild (5d64dca) existed to catch.
    root = _corpus(str(tmp_path), [("t01", "analysis", "PASS"),
                                   ("t02", "analysis", "PASS"),
                                   ("t03", "analysis", None)])          # meta present, verdict absent
    handed = [t for t in common.discover_tasks(split=None, include_pilot=True, tasks_dir=root)
              if t["id"] in ("t01", "t02")]
    with pytest.raises(RuntimeError, match="missing-verdict.*t03"):
        common.require_clean_ledger(handed, tasks_dir=root)


def test_gate_corrupt_verdict_refuses_like_missing(tmp_path):
    # A corrupt/unreadable verdict.json is an absent receipt, not a drop.
    root = _corpus(str(tmp_path), [("t01", "analysis", "PASS"),
                                   ("t02", "analysis", "CORRUPT")])
    handed = [t for t in common.discover_tasks(split=None, include_pilot=True, tasks_dir=root)
              if t["id"] == "t01"]
    with pytest.raises(RuntimeError, match="missing-verdict.*t02"):
        common.require_clean_ledger(handed, tasks_dir=root)


def test_gate_written_fail_is_legitimate_drop(tmp_path):
    # The complement: a WRITTEN FAIL is a recorded rejection — excluded from the census, run allowed.
    root = _corpus(str(tmp_path), [("t01", "analysis", "PASS"),
                                   ("t02", "analysis", "PASS"),
                                   ("t03", "analysis", "FAIL")])        # written rejection = legit drop
    handed = [t for t in common.discover_tasks(split=None, include_pilot=True, tasks_dir=root)
              if t["id"] in ("t01", "t02")]
    st = common.require_clean_ledger(handed, tasks_dir=root)
    assert st["clean"] and st["pass_ids"] == ["t01", "t02"]


def test_gate_refuses_all_dropped_subset(tmp_path):
    # CDX #010 fixture: handing only DROPPED tasks while PASS siblings sit on disk must refuse.
    root = _corpus(str(tmp_path), [("t01", "analysis", "PASS"),
                                   ("t02", "analysis", "FAIL")])
    handed = [t for t in common.discover_tasks(split=None, include_pilot=True, tasks_dir=root)
              if t["id"] == "t02"]                                      # hand only the dropped one
    with pytest.raises(RuntimeError, match="REV-021.*t01"):
        common.require_clean_ledger(handed, tasks_dir=root)
