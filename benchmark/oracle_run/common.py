"""common.py — shared plumbing for the code-oracle anchor study harness.

Implements the pieces the sealed pre-registration (docs/CODE_ORACLE_PREREG.md @ 60c6525,
REV-LANE #013, sha256 19bdfc44…) pins: the model tags, the task-dir convention, a stdlib-only
Ollama client (temp/seed/think-off), blind opaque IDs, and the ledger-CLEAN gate (§8).

NOTHING here spends API credits: the panel + generators are local Ollama ($0). The oracle is
pytest. The one hard rule this module enforces in code is prereg §8: a study run REFUSES unless
the corpus verification ledger is CLEAN. Smoke on PASS (clean) tasks is allowed; the full study
is not, until every task's verdict.json says PASS.
"""
from __future__ import annotations
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(os.path.dirname(HERE), "oracle_corpus")
TASKS_DIR = os.path.join(CORPUS, "tasks")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# ── prereg pins (§3 generators, §5 panel) — DO NOT edit without a re-seal ──────────────────────
GEN_CFG_A = "qwen2.5-coder:32b"        # standard prompt
GEN_CFG_B = "qwen2.5vl:7b"             # degraded/terse prompt (capability gap within one lineage)
GEN_TEMP = 0.4
JUDGE_PANEL = ["gemma4:12b", "llama3.2-vision:11b",
               "hf.co/LiquidAI/LFM2-24B-A2B-GGUF:Q4_K_M", "minicpm-v:latest"]
JUDGE_TEMP = 0.6
JUDGE_R = 3
NULL_RATE_REFUSE = 0.10                # §5: per-judge null rate >10% -> judge excluded/disclosed
MIN_JUDGES = 3                         # §8: panel J<3 -> study refuses


def discover_tasks(split="analysis", include_pilot=False, tasks_dir=None):
    """Yield task dicts {id, dir, meta, verdict} for the corpus, in id order.
    tasks_dir defaults to the real corpus; tests point it at a temp fixture."""
    tasks_dir = tasks_dir or TASKS_DIR
    out = []
    for tid in sorted(os.listdir(tasks_dir)):
        d = os.path.join(tasks_dir, tid)
        if not os.path.isdir(d):
            continue
        meta = _read_json(os.path.join(d, "meta.json"))
        verdict = _read_json(os.path.join(d, "verdict.json"))
        if meta is None:
            continue
        sp = meta.get("split", "analysis")
        if sp == "pilot" and not include_pilot:
            continue
        if split and sp != split and not (include_pilot and sp == "pilot"):
            continue
        out.append({"id": tid, "dir": d, "meta": meta, "verdict": verdict})
    return out


def ledger_status(tasks):
    """§4/§8: the corpus ships a per-task verdict.json ledger. CLEAN = every task PASS.
    Returns {clean: bool, pass_ids, fail_ids, missing_ids}."""
    pass_ids, fail_ids, missing = [], [], []
    for t in tasks:
        v = t.get("verdict")
        if v is None:
            missing.append(t["id"])
        elif str(v.get("verdict", "")).upper() == "PASS":
            pass_ids.append(t["id"])
        else:
            fail_ids.append(t["id"])
    return {"clean": (not fail_ids and not missing), "pass_ids": pass_ids,
            "fail_ids": fail_ids, "missing_ids": missing}


def require_clean_ledger(tasks, allow_smoke_on=None, tasks_dir=None):
    """Prereg §8 gate. Raises unless the ledger is CLEAN. `allow_smoke_on` is a list of task ids
    that are individually PASS — a smoke on those is permitted even while the whole corpus is not
    yet CLEAN (they are each ledger-clean). Any non-PASS id in allow_smoke_on is rejected.

    REV-021: cleanliness is a property of the CORPUS, not of the argument. The gate refuses
    zero tasks (an empty list is vacuously clean and vacuous truth does not run studies), and
    it censuses the on-disk corpus itself: every ledger-PASS task dir whose split appears in
    the handed list must BE in the handed list, or the caller mis-filtered and the gate is
    being asked to bless a subset.

    GAUGE #007 (counter-verify follow-up, CDX #010 fixtures): the census guards ABSENCE as well
    as presence. A WRITTEN non-PASS (FAIL) is a recorded rejection — legitimately dropped. A
    MISSING/unreadable verdict.json is no receipt at all — the exact claims-are-not-receipts
    silent-drop the rev2 rebuild (5d64dca) killed — so it REFUSES, never silently vanishes.
    tasks_dir defaults to the real corpus; tests point it at a temp fixture."""
    tasks_dir = tasks_dir or TASKS_DIR
    if not tasks:
        raise RuntimeError("prereg §8 REFUSAL (REV-021): zero tasks handed to the gate — "
                           "an empty corpus is not CLEAN, it is absent. No study run.")
    handed = {t["id"] for t in tasks}
    handed_splits = {t["meta"].get("split", "analysis") for t in tasks}
    for tid in sorted(os.listdir(tasks_dir)):
        d = os.path.join(tasks_dir, tid)
        if not os.path.isdir(d):
            continue
        meta = _read_json(os.path.join(d, "meta.json"))
        if meta is None:
            continue
        in_scope = (meta.get("split", "analysis") in handed_splits) and (tid not in handed)
        if not in_scope:
            continue
        v = _read_json(os.path.join(d, "verdict.json"))
        if v is None:
            raise RuntimeError(
                f"prereg §8 REFUSAL (missing-verdict): task {tid} (split "
                f"{meta.get('split','analysis')!r}) is on disk with no readable verdict.json and is "
                f"not in the handed list — an ABSENT receipt is not a drop (claims-are-not-receipts; "
                f"the rev2 lesson). Write its verdict or record an explicit drop before the gate runs.")
        if str(v.get("verdict", "")).upper() == "PASS":
            raise RuntimeError(
                f"prereg §8 REFUSAL (REV-021): task {tid} (split "
                f"{meta.get('split','analysis')!r}, ledger-PASS on disk) is missing from the "
                f"handed list — the gate does not bless subsets of the corpus census.")
        # else: a WRITTEN non-PASS (FAIL) — a recorded rejection, legitimately excluded from the census.
    st = ledger_status(tasks)
    if allow_smoke_on is not None:
        bad = [t for t in allow_smoke_on if t not in st["pass_ids"]]
        if bad:
            raise RuntimeError(f"prereg §8: smoke requested on non-PASS (not ledger-clean) tasks {bad}; "
                               f"smoke only on PASS tasks. PASS set: {st['pass_ids']}")
        return st
    if not st["clean"]:
        raise RuntimeError(
            f"prereg §8 REFUSAL: corpus verification ledger is NOT CLEAN — "
            f"{len(st['fail_ids'])} FAIL, {len(st['missing_ids'])} missing. No study run. "
            f"Smoke on PASS tasks with allow_smoke_on=[...]. FAIL: {st['fail_ids'][:8]}...")
    return st


def ollama_chat(model, prompt, temperature, seed, think=False, timeout=600):
    """Single-turn Ollama /api/chat call (stdlib urllib; local, $0). Returns the raw content string.
    seed + temperature make it reproducible; think=False disables chain-of-thought where supported."""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": think,
        "options": {"temperature": temperature, "seed": int(seed)},
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode("utf-8"))
    return resp.get("message", {}).get("content", "") or ""


def blind_id(task_id, config, salt):
    """Opaque, stable, non-reversible-by-eye rating ID (§2/§5: judges see IDs, never config/tier
    labels or test results). Deterministic from a per-run salt so the reveal map reproduces."""
    import hashlib
    h = hashlib.sha256(f"{salt}\x1f{task_id}\x1f{config}".encode("utf-8")).hexdigest()
    return "sol-" + h[:12]


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def extract_code(text):
    """Pull a python code block out of a model completion; fall back to the whole text.
    Generators are told to emit a single ```python fenced block implementing the function."""
    if not text:
        return ""
    lines = text.splitlines()
    out, in_block, fence = [], False, None
    for ln in lines:
        s = ln.strip()
        if not in_block and s.startswith("```"):
            in_block, fence = True, s
            continue
        if in_block and s.startswith("```"):
            break
        if in_block:
            out.append(ln)
    return "\n".join(out) if out else text
