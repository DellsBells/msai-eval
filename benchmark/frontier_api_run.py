"""frontier_api_run.py — the paid-API frontier keystone run (multi-judge panel, R>=2).

Reuses the SAME keystone_ladder(n=10, seed=0) as the chat-window R=2 run, so the result is a
direct apples-to-apples comparison: does the distinctive "statistically real but BELOW resolution"
subtle verdict hold on genuine frontier API judges, or is it a coarse-gauge phenomenon?

Each response is rated INDEPENDENTLY on a blind, self-contained 1-5 scale (no pairs, no "which is
better"), R repeats per judge (repeatability), across the judge panel (reproducibility). Rows feed
the validated Gage R&R gauge via ev.msai.compare(). Cost-guarded with a hard ceiling; raw scores
persisted so we never re-spend.

Usage:
  python frontier_api_run.py [--n=10] [--R=3] [--workers=6] [--ceiling=10]
                             [--judges=openai,xai,gemini,claude,deepseek] [--append]
                             [--smoke] [--preflight-only]

--append: MERGE this run's judges into an existing frontier_api_scores.json instead of overwriting.
          Use it to add a new lineage (e.g. deepseek) without re-spending on the others:
              python frontier_api_run.py --judges=deepseek --append
"""
import json
import os
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elo_validation as ev

OUT_PATH = os.path.join(HERE, "frontier_api_scores.json")


def load_env(path=os.path.join(HERE, ".env")):
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def arg(flag, default):
    for a in sys.argv:
        if a.startswith(flag):
            return a.split("=", 1)[1]
    return default


# ---- judge panel: each lab's current frontier flagship ------------------------------------------
# price = ($/1M input, $/1M output), used only for the running cost guard (conservative overestimate).
ALL_JUDGES = [
    dict(name="openai",   kind="openai",    model="gpt-5.5",
         base=None,                                                          env="OPENAI_API_KEY",
         price=(5.0, 30.0),  reasoning="low"),
    dict(name="xai",      kind="openai",    model="grok-4.3",
         base="https://api.x.ai/v1",                                         env="XAI_API_KEY",
         price=(5.0, 15.0),  reasoning=None),
    dict(name="gemini",   kind="openai",    model="models/gemini-3.1-pro-preview",
         base="https://generativelanguage.googleapis.com/v1beta/openai/",    env="GEMINI_API_KEY",
         price=(2.5, 15.0),  reasoning=None),
    dict(name="claude",   kind="anthropic", model="claude-opus-4-8",
         base=None,                                                          env="ANTHROPIC_API_KEY",
         price=(5.0, 25.0),  reasoning=None),
    dict(name="deepseek", kind="openai",    model="deepseek-v4-pro",
         base="https://api.deepseek.com",                                    env="DEEPSEEK_API_KEY",
         price=(2.0, 4.0),   reasoning=None),
]

TEMP = 0.6
CLIP_PROMPT, CLIP_ANSWER = 700, 1200          # IDENTICAL to frontier_batch.py so items match the R=2 run
SEED = 0
CLAUDE_MAX_TOKENS = 32                          # bumped 16->32: Opus at 16 occasionally returned empty


def make_client(j):
    if j["kind"] == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=os.environ[j["env"]], max_retries=5)
    from openai import OpenAI
    kw = dict(api_key=os.environ[j["env"]], max_retries=5)
    if j["base"]:
        kw["base_url"] = j["base"]
    return OpenAI(**kw)


def clip(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n].rstrip() + " …[truncated]"


def build_prompt(prompt, answer):
    return (
        "This is a SELF-CONTAINED rating task. Disregard any prior conversation, saved memory, or "
        "personalization — judge ONLY on what is shown below, as a neutral first-time rater.\n\n"
        "Rate the QUALITY of this ANSWER to the PROMPT on a 1-5 INTEGER scale (5=excellent, 1=poor), "
        "on its own merits.\n\n"
        f"PROMPT: {clip(prompt, CLIP_PROMPT)}\n"
        f"ANSWER: {clip(answer, CLIP_ANSWER)}\n\n"
        "Output ONLY a single integer 1-5. Nothing else."
    )


def call_judge(clients, j, text):
    # REV-005 remainder: parse with the SINGLE hardened parser (ev.parse_rating — rejects fractions/
    # percentages/multi-digit and reads worded "4 out of 5"), and RETURN THE RAW COMPLETION so every
    # score is re-auditable from evidence without re-spending (forward-only; existing scores keep their
    # schema). Returns (score, in_tokens, out_tokens, raw_completion).
    c = clients[j["name"]]
    if j["kind"] == "anthropic":                                   # Opus: no temperature, no thinking
        r = c.messages.create(model=j["model"], max_tokens=CLAUDE_MAX_TOKENS,
                              messages=[{"role": "user", "content": text}])
        out = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        u = r.usage
        return ev.parse_rating(out), u.input_tokens, u.output_tokens, out
    msgs = [{"role": "user", "content": text}]
    attempts = []
    if j["reasoning"]:                                             # gpt-5.x: reasoning models use max_completion_tokens
        attempts.append(dict(max_completion_tokens=2048, reasoning_effort=j["reasoning"]))
        attempts.append(dict(max_completion_tokens=2048))
    else:
        attempts.append(dict(max_tokens=2048, temperature=TEMP))
        attempts.append(dict(max_completion_tokens=2048))
        attempts.append(dict(max_tokens=64))
    last = None
    for kw in attempts:
        try:
            r = c.chat.completions.create(model=j["model"], messages=msgs, **kw)
            out = r.choices[0].message.content or ""
            u = r.usage
            return ev.parse_rating(out), (u.prompt_tokens or 0), (u.completion_tokens or 0), out
        except Exception as e:
            last = e
            continue
    raise last


def merge_and_save(new_rows, new_meta, judges, append):
    """new_rows: list of (tier,pair,config,judge,rep,score,raw). Overwrite, or merge into existing file.
    REV-005: `raw` (the judge's raw completion, capped) is persisted so a score can be re-audited from
    evidence without re-spending. Backward-compatible read: old files simply have no `raw` key."""
    def row_dict(t, p, c, jn, rp, s, raw=None):
        d = dict(tier=t, pair=p, config=c, judge=jn, rep=rp, score=(None if s != s else s))
        if raw is not None:
            d["raw"] = str(raw)[:4000]                          # cap defensively; rating replies are short
        return d
    fresh = [row_dict(*r) for r in new_rows]
    if append and os.path.exists(OUT_PATH):
        prev = json.load(open(OUT_PATH))
        new_judge_names = {j["name"] for j in judges}
        kept = [s for s in prev["scores"] if s["judge"] not in new_judge_names]   # drop old rows for judges we re-ran
        merged = kept + fresh
        meta = dict(prev.get("meta", {}))
        meta.setdefault("judges", {}); meta["judges"].update(new_meta.get("judges", {}))
        meta["cost_usd"] = round(meta.get("cost_usd", 0.0) + new_meta.get("cost_usd", 0.0), 4)
        meta["appended"] = meta.get("appended", []) + [{"judges": list(new_judge_names),
                                                         "cost_usd": new_meta.get("cost_usd"),
                                                         "failures": new_meta.get("failures")}]
        json.dump({"meta": meta, "scores": merged}, open(OUT_PATH, "w"), indent=1)
        return len(merged), sorted({s["judge"] for s in merged})
    json.dump({"meta": new_meta, "scores": fresh}, open(OUT_PATH, "w"), indent=1)
    return len(fresh), sorted(new_meta.get("judges", {}))


def main():
    load_env()
    N = int(arg("--n=", 10))
    R = int(arg("--R=", 3))
    WORKERS = int(arg("--workers=", 6))
    CEILING = float(arg("--ceiling=", 10.0))
    SMOKE = "--smoke" in sys.argv
    PREFLIGHT_ONLY = "--preflight-only" in sys.argv
    APPEND = "--append" in sys.argv
    if SMOKE:
        N, R = 1, 1

    want = arg("--judges=", "openai,xai,gemini,claude").split(",")
    judges = [j for j in ALL_JUDGES if j["name"] in want and os.environ.get(j["env"])]
    missing = [j["name"] for j in ALL_JUDGES if j["name"] in want and not os.environ.get(j["env"])]
    if missing:
        print(f"(skipping judges with no key in .env: {missing})")
    if not judges:
        print("no usable judges — populate benchmark/.env"); return
    clients = {j["name"]: make_client(j) for j in judges}

    print(f"\nFRONTIER API RUN — judges={[j['name'] for j in judges]}  n={N}/tier  R={R}  "
          f"ceiling=${CEILING:g}  {'(APPEND)' if APPEND else ''}")
    print("preflight (one call per judge on its chosen model):")
    sample = build_prompt("What is 2+2?", "It is 4.")
    for j in judges:
        try:
            s, ti, to, _raw = call_judge(clients, j, sample)
            print(f"  {j['name']:8s} {j['model']:28s} OK  score={s}  (in={ti} out={to})")
        except Exception as e:
            print(f"  {j['name']:8s} {j['model']:28s} FAIL  {str(e)[:160]}")
            print("\nAborting: a judge model failed preflight."); return
    if PREFLIGHT_ONLY:
        print("\npreflight-only: all judges good.")
        return

    lad = ev.keystone_ladder(n_per_tier=N, seed=SEED)
    tasks = []
    for t in lad:
        for pi, pair in enumerate(t["pairs"]):
            for cfg in ("chosen", "rejected"):
                text = build_prompt(pair["prompt"], pair[cfg])
                for j in judges:
                    for rep in range(R):
                        tasks.append((t["name"], pi, cfg, j, rep, text))
    print(f"\n{len(tasks)} judge calls queued  "
          f"({len(lad)} tiers x {N} pairs x 2 configs x {R} reps x {len(judges)} judges)")

    lock = threading.Lock()
    abort = threading.Event()
    cost = {"$": 0.0, "in": 0, "out": 0, "done": 0, "fail": 0}
    per_judge = defaultdict(lambda: {"$": 0.0, "in": 0, "out": 0, "n": 0})
    results = []

    def worker(task):
        tier, pi, cfg, j, rep, text = task
        if abort.is_set():
            return
        try:
            s, ti, to, raw = call_judge(clients, j, text)
        except Exception:
            with lock:
                cost["fail"] += 1
            return
        pin, pout = j["price"]
        c = ti / 1e6 * pin + to / 1e6 * pout
        with lock:
            cost["$"] += c; cost["in"] += ti; cost["out"] += to; cost["done"] += 1
            pj = per_judge[j["name"]]; pj["$"] += c; pj["in"] += ti; pj["out"] += to; pj["n"] += 1
            results.append((tier, pi, cfg, j["name"], rep, s, raw))
            if cost["$"] > CEILING:
                abort.set()
            if cost["done"] % 60 == 0:
                print(f"  ... {cost['done']}/{len(tasks)} calls, ${cost['$']:.2f}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(worker, t) for t in tasks]
        for _ in as_completed(futs):
            pass
    elapsed = time.time() - t0
    if abort.is_set():
        print(f"\n!! COST CEILING ${CEILING:g} HIT — aborted at ${cost['$']:.2f}. Partial results below.")

    new_meta = dict(n=N, R=R, seed=SEED, judges={j["name"]: j["model"] for j in judges},
                    cost_usd=round(cost["$"], 4), in_tokens=cost["in"], out_tokens=cost["out"],
                    failures=cost["fail"], elapsed_s=round(elapsed, 1))
    total_rows, all_judges = merge_and_save(results, new_meta, judges, APPEND)

    print(f"\ndone in {elapsed:.0f}s  |  {cost['done']} ok, {cost['fail']} failed  |  this run ${cost['$']:.3f}")
    for jn, pj in per_judge.items():
        print(f"  {jn:8s} {pj['n']:4d} calls  in={pj['in']:>7d} out={pj['out']:>7d}  ${pj['$']:.3f}")
    print(f"scores -> {OUT_PATH}  ({total_rows} rows, judges={all_judges})")
    print("\nRun frontier_reanalyze.py for the four-state keystone verdict (zero spend).")


if __name__ == "__main__":
    main()
