"""gen_solutions.py — solution generators (prereg §3).

cfg-A: qwen2.5-coder:32b, STANDARD prompt (the task's prompt.md verbatim + a fixed output
       instruction). cfg-B: qwen2.5vl:7b, DEGRADED/terse prompt — the same capability lineage
       (Qwen) crippled by a worse prompt, so the oracle-measured quality gap is a prompt effect,
       not a lineage confound. Both temp 0.4, seeded. The generator sees prompt.md ONLY — never the
       hidden tests, the reference, or the broken solution.

Degradation is tuned on the PILOT SPLIT ONLY (§3); `degrade_prompt` here is the harness default,
to be pinned against the 8 pilot tasks before the analysis run. Raw completions are persisted
(REV-005 discipline) so every generated solution is re-auditable without re-generating.
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

_OUTPUT_INSTRUCTION = (
    "\n\nImplement the function exactly as specified. Respond with ONE ```python fenced code block "
    "containing a complete, self-contained module (standard library only). No prose, no tests."
)


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def build_prompt(task, config):
    """cfg-A gets the full prompt.md; cfg-B gets a degraded/terse version. Output instruction is
    identical so the ONLY manipulated variable is the task description's richness."""
    prompt_md = _read(os.path.join(task["dir"], "prompt.md")) or ""
    if config == "A":
        body = prompt_md
    elif config == "B":
        body = degrade_prompt(prompt_md)
    else:
        raise ValueError(f"config must be 'A' or 'B', got {config!r}")
    return body.rstrip() + _OUTPUT_INSTRUCTION


DEGRADE_LEVEL = 2  # PINNED on pilot evidence 2026-07-09 (pilot_tune_results.json):
                   # level 1 (title+signature only) gave 5 resolve / 3 subtle / 0 tie with
                   # cfg-B at 0.0 on 6/8 pilot tasks — too harsh, no negative-control ties.
                   # Level 2 adds the first worked example. §3: tuned on the pilot split ONLY.


def degrade_prompt(prompt_md, level=None):
    """Degradation ladder (tuned on the pilot split ONLY, §3; pinned via DEGRADE_LEVEL).
    Level 1: title + first signature-bearing line. Level 2: level 1 + the first worked
    example block. A terser task statement that a capable model can still attempt but is
    likelier to under-specify against the hidden tests."""
    import re
    if level is None:
        level = DEGRADE_LEVEL
    lines = prompt_md.splitlines()
    title = next((ln for ln in lines if ln.startswith("#")), "").lstrip("# ").strip()
    # the real function signature is a `def name(...)` line (usually inside a ```python block)
    sig = next((ln.strip() for ln in lines if re.match(r"\s*def\s+\w+\s*\(", ln)), "")
    keep = []
    if title:
        keep.append(f"Write a Python function for: {title}.")
    if sig:
        keep.append(f"Signature: `{sig}`")
    if level >= 2:
        m = re.search(r"(?im)^#{1,3}[^\n]*examples?[^\n]*$", prompt_md)
        if m:
            tail = prompt_md[m.end():]
            nxt = re.search(r"(?m)^#{1,3}\s", tail)
            body = tail[:nxt.start()] if nxt else tail
            keep.append("One example:\n" + body.strip()[:600])
    keep.append("Infer reasonable behavior from the name and signature.")
    return "\n".join(keep)


def generate(task, config, seed=0, timeout=600):
    """Live generation for one task+config. Returns {code, raw, model, seed}. Spends local compute
    only ($0). Callers gate this behind the ledger check — do not batch-run before the ledger is CLEAN."""
    model = common.GEN_CFG_A if config == "A" else common.GEN_CFG_B
    prompt = build_prompt(task, config)
    raw = common.ollama_chat(model, prompt, temperature=common.GEN_TEMP, seed=seed, timeout=timeout)
    return {"code": common.extract_code(raw), "raw": raw, "model": model, "seed": seed,
            "task_id": task["id"], "config": config}


def persist(task, config, result, out_root=None):
    """Write the generated solution + its raw completion under tasks/<id>/solutions/ (auditable)."""
    d = out_root or os.path.join(task["dir"], "solutions")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"cfg{config}.py"), "w", encoding="utf-8") as f:
        f.write(result["code"] or "")
    with open(os.path.join(d, f"cfg{config}.raw.txt"), "w", encoding="utf-8") as f:
        f.write(result["raw"] or "")
    return d


if __name__ == "__main__":
    # DRY structural smoke (no model call — honors "do NOT start solution generation"): build and show
    # both prompts for a PASS task, proving the standard-vs-degraded construction. Use --live <id> to
    # generate for ONE clean task once rev-lane greenlights + the ledger is CLEAN.
    args = sys.argv[1:]
    tasks = {t["id"]: t for t in common.discover_tasks(split=None, include_pilot=True)}
    if args and args[0] == "--live":
        tid = args[1]
        common.require_clean_ledger(list(tasks.values()), allow_smoke_on=[tid])
        for cfg in ("A", "B"):
            res = generate(tasks[tid], cfg)
            persist(tasks[tid], cfg, res)
            print(f"[{tid}] cfg-{cfg} ({res['model']}): {len(res['code'])} chars of code generated")
    else:
        tid = args[0] if args else "t05"
        common.require_clean_ledger(list(tasks.values()), allow_smoke_on=[tid])
        print(f"GEN DRY SMOKE (no model call) on {tid}:")
        for cfg in ("A", "B"):
            p = build_prompt(tasks[tid], cfg)
            print(f"\n--- cfg-{cfg} prompt ({common.GEN_CFG_A if cfg=='A' else common.GEN_CFG_B}), "
                  f"{len(p)} chars ---\n{p[:600]}")
        print(json.dumps({"smoke": tid, "status": "prompt construction verified (dry)"}, indent=1))
