"""oracle_runner.py — the judge-independent reference (u_ref ~ 0).

Prereg §2: oracle verdict per solution = pass-rate over the HIDDEN tests, executed deterministically
in a pinned sandbox (venv python, temp cwd, timeout, NO network). §2 mitigation: 2x replication per
solution; any discordance -> the task is QUARANTINED (a flaky oracle cannot anchor anyone).
Prereg §3: tiers assigned AFTER oracle, BEFORE judging, by pass-rate gap g = passrate_A - passrate_B:
resolve |g|>=0.5, subtle 0<|g|<0.5, tie g=0. Per-tier counts fall where the oracle puts them.

This module spends NO API credits and needs NO model: it runs existing/candidate solutions through
pytest. That is exactly why the corpus can be self-certified before it certifies any judge.
"""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

# A conftest that hard-disables network inside the sandbox (prereg §2 "no network"). Written into
# each run dir so any test that opens a socket fails loudly instead of reaching out.
_NO_NETWORK_CONFTEST = (
    "import socket as _s\n"
    "def _blocked(*a, **k):\n"
    "    raise RuntimeError('oracle sandbox: network is disabled (prereg §2)')\n"
    "_s.socket = _blocked\n"
    "_s.create_connection = _blocked\n"
)


def run_solution(task_dir, solution_code, timeout=60, py=None):
    """Run one candidate solution through the task's hidden tests in an isolated sandbox.
    Returns {passed, failed, errors, total, pass_rate, all_pass, ok}. `ok` is False if the run
    itself failed to execute (timeout / collection error) — distinct from tests failing."""
    py = py or sys.executable
    hidden = os.path.join(task_dir, "hidden_tests.py")
    if not os.path.exists(hidden):
        return {"passed": 0, "failed": 0, "errors": 0, "total": 0, "pass_rate": 0.0,
                "all_pass": False, "ok": False, "note": "no hidden_tests.py"}
    d = tempfile.mkdtemp(prefix="oracle_")
    try:
        with open(os.path.join(d, "solution.py"), "w", encoding="utf-8") as f:
            f.write(solution_code or "")
        shutil.copy(hidden, os.path.join(d, "hidden_tests.py"))
        with open(os.path.join(d, "conftest.py"), "w", encoding="utf-8") as f:
            f.write(_NO_NETWORK_CONFTEST)
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(
                [py, "-m", "pytest", "hidden_tests.py", "-q", "-p", "no:cacheprovider",
                 "--no-header", "-o", "addopts="],
                cwd=d, env=env, capture_output=True, text=True, timeout=timeout,
            )
            out = proc.stdout + "\n" + proc.stderr
        except subprocess.TimeoutExpired:
            return {"passed": 0, "failed": 0, "errors": 0, "total": 0, "pass_rate": 0.0,
                    "all_pass": False, "ok": False, "note": "timeout"}
        passed, failed, errors = _parse_counts(out)
        total = passed + failed + errors
        return {"passed": passed, "failed": failed, "errors": errors, "total": total,
                "pass_rate": (passed / total) if total else 0.0,
                "all_pass": bool(total > 0 and failed == 0 and errors == 0),
                "ok": total > 0}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def oracle_score(task_dir, solution_code, replicate=2, timeout=60, py=None):
    """§2: run the solution `replicate` times; discordant pass counts -> quarantine (flaky oracle)."""
    runs = [run_solution(task_dir, solution_code, timeout=timeout, py=py) for _ in range(replicate)]
    keys = {(r["passed"], r["failed"], r["errors"]) for r in runs}
    concordant = len(keys) == 1 and all(r["ok"] for r in runs)
    r0 = runs[0]
    return {"pass_rate": r0["pass_rate"], "all_pass": r0["all_pass"], "passed": r0["passed"],
            "total": r0["total"], "replication_ok": concordant,
            "quarantined": not concordant, "runs": runs}


def assign_tier(passrate_a, passrate_b):
    """§3: mechanical, oracle-assigned. g = passrate_A - passrate_B."""
    g = passrate_a - passrate_b
    if abs(g) >= 0.5:
        tier = "resolve"
    elif g == 0:
        tier = "tie"
    else:
        tier = "subtle"
    return {"g": g, "tier": tier}


def _parse_counts(out):
    # robust token scan (pytest summary wording varies): "N passed", "N failed", "N error(s)"
    passed = failed = errors = 0
    for m in re.finditer(r"(\d+)\s+(passed|failed|errors?)", out):
        val, word = int(m.group(1)), m.group(2)
        if word == "passed":
            passed = val
        elif word == "failed":
            failed = val
        else:
            errors = val
    return passed, failed, errors


def self_check(task):
    """Corpus self-verification echo (§4): the reference solution should all-pass, the broken one
    should NOT. Uses the on-disk reference/broken solutions — no model. Feeds the smoke."""
    d = task["dir"]
    ref = _read(os.path.join(d, "reference_solution.py"))
    brk = _read(os.path.join(d, "broken_solution.py"))
    r_ref = oracle_score(d, ref) if ref is not None else None
    r_brk = oracle_score(d, brk) if brk is not None else None
    return {"reference": r_ref, "broken": r_brk,
            "reference_all_pass": bool(r_ref and r_ref["all_pass"]),
            "broken_fails": bool(r_brk and not r_brk["all_pass"])}


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


if __name__ == "__main__":
    # Model-free smoke: verify the oracle on PASS (ledger-clean) tasks via their on-disk solutions.
    ids = sys.argv[1:] or ["t05", "t07"]
    tasks = {t["id"]: t for t in common.discover_tasks(split=None, include_pilot=True)}
    common.require_clean_ledger(list(tasks.values()), allow_smoke_on=ids)   # §8: PASS-only smoke
    print(f"ORACLE SMOKE (model-free) on {ids}")
    for tid in ids:
        sc = self_check(tasks[tid])
        print(f"  {tid}: reference all_pass={sc['reference_all_pass']} "
              f"(rate={sc['reference']['pass_rate']:.2f}, replication_ok={sc['reference']['replication_ok']}) | "
              f"broken fails={sc['broken_fails']} (rate={sc['broken']['pass_rate']:.2f})")
    print(json.dumps({"smoke": ids, "status": "oracle plumbing verified"}, indent=1))
