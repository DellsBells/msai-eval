"""Step-1 shakedown: does the gauge separate good compression from bad?

Before building ANY frontier scheme, prove the measurement system works:
  * generate the same task from off-the-shelf configs {fp16, q8, q4, q2, sentinel}
    using MLX (one base model, quantized locally to each level),
  * have a blind multi-lineage judge panel (local Ollama models) score each
    generation, several trials at temperature>0,
  * feed the rows to msai_eval.reliability() then compare(baseline="fp16"),
  * print the Step-1 gate.

GATE TO PASS (per docs/history/BUILD_PLAN_compression.md):
  gauge QUALIFIED (finite guard band: not frozen + balanced replicates — ndc is
    advisory context only, NOT a gate; it is selection-sensitive on hand-picked configs)  AND
  q2 + sentinel read "REAL drop"  AND  q4 reads "within noise".
If q2 doesn't separate from fp16, STOP and fix the gauge before building anything.

    .venv/bin/python shakedown/shakedown.py --smoke      # fast first run
    .venv/bin/python shakedown/shakedown.py              # fuller run

Needs: mlx, mlx-lm (MLX-compatible python), a running Ollama (judge panel), msai-eval.
"""
from __future__ import annotations
import argparse, json, re, sys, time
import requests

OLLAMA_CHAT = "http://localhost:11434/api/chat"

# A small generic instruction set. Swap in the real 20-photo listing manifest later;
# the gauge only needs a task whose quality a panel can score.
TASKS = [
    "Write a one-sentence product description for a pair of used leather hiking boots, size 11.",
    "Summarize in 2 sentences why a vintage film camera might appeal to a buyer.",
    "List three honest condition notes a seller should disclose for a 5-year-old laptop.",
    "Write a friendly 2-sentence reply to a buyer asking if a jacket is still available.",
    "Give a concise title (under 12 words) for a listing of a mid-century walnut side table.",
    "Explain in 2 sentences why bundling two video games could help them sell faster.",
    "Write a one-sentence shipping note reassuring a buyer their fragile vase is well packed.",
    "Describe, in 2 sentences, the key selling point of a barely-used espresso machine.",
    "Draft a 2-sentence return-policy blurb that is fair to both buyer and seller.",
    "Write a single clear sentence describing the color and material of a wool overcoat.",
    "Give two short bullet points a buyer would want to know about a used mountain bike.",
    "Write a one-sentence apology and fix for a listing that had the wrong size posted.",
]
SENTINEL_PROMPT = "Write a haiku about a rock."   # off-topic on purpose -> obviously bad

JUDGE_RUBRIC = (
    "You are grading a marketplace-listing assistant. Rate how well the RESPONSE "
    "accomplishes the TASK, using these anchors:\n"
    "  1 = off-topic, empty, or unusable\n"
    "  2 = on-topic but clear errors or misses the ask\n"
    "  3 = acceptable; does the task but bland or slightly off\n"
    "  4 = good; accurate and clear, postable with minor nits\n"
    "  5 = excellent; accurate, natural, and polished\n\n"
    "TASK:\n{task}\n\nRESPONSE:\n{response}\n\n"
    "Reply with ONLY the single integer 1, 2, 3, 4, or 5. No other text."
)


def gen_mlx(model, tok, prompt, max_tokens):
    from mlx_lm import generate
    try:
        text = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                       add_generation_prompt=True, tokenize=False)
    except Exception:
        text = prompt
    try:
        return generate(model, tok, prompt=text, max_tokens=max_tokens, verbose=False).strip()
    except TypeError:
        return generate(model, tok, text, max_tokens=max_tokens, verbose=False).strip()


def load_config(model_id, bits, group_size):
    from mlx_lm import load
    import mlx.nn as nn
    model, tok = load(model_id)            # cached on disk after first download
    if bits is not None:
        nn.quantize(model, group_size=group_size, bits=bits)
    return model, tok


def judge_score(judge_model, task, response, temperature):
    """One blind 1-5 rating. think=False keeps reasoning judges from burning the token
    budget on a hidden <think> block (and we want a snap rating, not a judge reasoning
    itself into an answer). Falls back to a plain call for models without thinking."""
    msg = [{"role": "user", "content": JUDGE_RUBRIC.format(task=task, response=response[:1200])}]

    def _call(think):
        body = {"model": judge_model, "messages": msg, "stream": False,
                "options": {"temperature": temperature, "num_predict": 24}}
        if think is not None:
            body["think"] = think
        return requests.post(OLLAMA_CHAT, json=body, timeout=300)

    try:
        r = _call(think=False)
        if r.status_code >= 400:                 # model doesn't support 'think' -> plain call
            r = _call(think=None)
        m = r.json().get("message", {})
        text = (m.get("content") or "") or (m.get("thinking") or "")
        match = re.search(r"[1-5]", text)
        return int(match.group()) if match else None
    except Exception as e:
        print(f"    [judge {judge_model} error: {e}]", file=sys.stderr)
        return None


def gate_verdict(g, comparisons):
    """Step-1 gate on the GUARD-BAND criterion (NOT ndc>=5).

    ndc counts distinct quality LEVELS among the configs you happened to test, so
    clustered configs (good vs broken) cap it low no matter how sharp the gauge — the
    selection-sensitive 'ndc-as-grade' trap the build plan disowns. The guard band is
    the right resolution test for an acceptance comparison, and each config's
    beyond_gauge flag already carries the per-comparison verdict directly."""
    q2  = comparisons.get("q2", {})
    q4  = comparisons.get("q4", {})
    sen = comparisons.get("sentinel", {})
    frozen = any("frozen" in w for w in g.get("warnings", []))
    gb     = g.get("guard_band")
    usable = (gb is not None) and (not frozen) and ((g.get("grr_sd") or 0) > 0)

    # Aggregate resolution = widest CI half-width across the GOOD-config deltas. This is the
    # number that actually bounds a frontier "within noise" claim: it's the precision of the
    # panel-MEAN delta, and it shrinks ~1/sqrt(N judges*trials). The guard band, by contrast,
    # is single-rating noise — floored near the integer 1-5 granularity, so it can't certify
    # sub-point frontier deltas no matter what. Report both; they answer different questions.
    def halfwidth(c):
        ci = c.get("ci")
        return (ci[1] - ci[0]) / 2 if ci else None
    good = {k: comparisons[k] for k in ("q8", "q4") if k in comparisons}
    hw = [halfwidth(c) for c in good.values() if halfwidth(c) is not None]
    ci_hw = max(hw) if hw else None

    print("\n" + "=" * 70 + "\nSTEP-1 GATE  (guard-band criterion)\n" + "=" * 70)
    print(f"  gauge usable (not frozen, finite guard band) .. {usable}")
    if gb is not None:
        print(f"    guard band (single-rating resolution) = {gb:.2f} pts  (GRR SD = {g.get('grr_sd'):.2f})")
    if ci_hw is not None:
        print(f"    aggregate resolution (widest good-config CI half-width) = ±{ci_hw:.2f} pts")
    print(f"    context: ndc = {g.get('ndc')}  (descriptive, non-gating)")

    # Resolution-only mode: a good-configs-only run (no broken q2/sentinel) asks whether the
    # gauge is sharp enough to SEE frontier-sized deltas, not whether it separates broken/good.
    if not (q2 and sen):
        TARGET = 0.15
        sharp = (ci_hw is not None) and (ci_hw <= TARGET)
        for k, c in good.items():
            ci = c.get("ci", [0, 0])
            print(f"  {k:8s} Δ={c.get('delta',0):+.2f}  CI=[{ci[0]:+.2f}, {ci[1]:+.2f}]  -> {c.get('verdict','')}")
        print(f"\n  >>> {'SHARP ENOUGH' if sharp else 'STILL TOO COARSE'} for frontier deltas "
              f"(aggregate resolution ±{ci_hw if ci_hw is not None else float('nan'):.2f} vs ~0.1-0.3 pt target).")
        if not sharp:
            print("      Add judges/trials (CI shrinks ~1/sqrt(N)) or lower judge temp to tighten it.")
        return {"mode": "resolution", "usable": usable, "guard_band": gb,
                "aggregate_ci_halfwidth": ci_hw, "sharp_enough": sharp}

    # Full broken-vs-good gate
    def real_drop(c): return c.get("beyond_gauge") is True and c.get("significant_adj") is True
    def within(c):    return c.get("beyond_gauge") is False
    sen_real, q2_real, q4_noise = real_drop(sen), real_drop(q2), within(q4)
    passed = usable and sen_real and q2_real and q4_noise
    print(f"  sentinel beyond gauge + resolvable ............ {sen_real}   (Δ={sen.get('delta',0):+.2f}, Cliff δ={sen.get('cliffs_delta',0):+.2f})")
    print(f"  q2 beyond gauge + resolvable ................. {q2_real}   (Δ={q2.get('delta',0):+.2f}, Cliff δ={q2.get('cliffs_delta',0):+.2f})")
    print(f"  q4 within gauge resolution ................... {q4_noise}   (Δ={q4.get('delta',0):+.2f}, Cliff δ={q4.get('cliffs_delta',0):+.2f})")
    if passed:
        print("\n  >>> PASS — the gauge resolves good from broken cleanly. Proceed, with the note below.")
        print(f"  NOTE: certifies GROSS resolution only (~{gb:.2f} pts, inflated by the broken configs).\n"
              "        Run --configs fp16,q8,q4 to measure the fine (frontier) resolution.")
    else:
        print("\n  >>> FAIL — gauge cannot cleanly separate broken from good; fix panel/rubric/trials.")
    return {"mode": "full", "passed": passed, "usable": usable, "guard_band": gb,
            "sentinel_real": sen_real, "q2_real": q2_real, "q4_within": q4_noise}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="fast: tiny model, fewer items/judges/trials")
    ap.add_argument("--model", default=None, help="MLX base model id (fp16/bf16)")
    ap.add_argument("--items", type=int, default=None)
    ap.add_argument("--judges", default=None, help="comma-separated Ollama judge models")
    ap.add_argument("--trials", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=80)
    ap.add_argument("--configs", default=None,
                    help="comma-separated subset of fp16,q8,q4,q2,sentinel (default: all five). "
                         "Use 'fp16,q8,q4' for a good-config-only resolution run.")
    ap.add_argument("--temp", type=float, default=0.7,
                    help="judge temperature; lower tightens repeatability (sharper guard band)")
    ap.add_argument("--regate", action="store_true",
                    help="re-apply the gate to the saved last_result.json (no model calls)")
    args = ap.parse_args()

    if args.regate:
        saved = json.load(open("shakedown/last_result.json"))
        gate_verdict(saved["gauge"], saved["comparisons"])
        return 0

    if args.smoke:
        model_id = args.model or "mlx-community/Qwen2.5-0.5B-Instruct-bf16"
        n_items  = args.items or 6
        judges   = (args.judges.split(",") if args.judges else ["gemma4:12b", "qwen3.5:27b", "hf.co/LiquidAI/LFM2-24B-A2B-GGUF:Q4_K_M"])
        trials   = args.trials or 3
    else:
        model_id = args.model or "mlx-community/Qwen2.5-1.5B-Instruct-bf16"
        n_items  = args.items or 12
        judges   = (args.judges.split(",") if args.judges else
                    ["gemma4:12b", "qwen3.5:27b", "qwen2.5-coder:32b",
                     "hf.co/LiquidAI/LFM2-24B-A2B-GGUF:Q4_K_M", "qwen3.6:35b-mlx"])
        trials   = args.trials or 3

    tasks = TASKS[:n_items]
    ALL_CONFIGS = {"fp16": (None, None), "q8": (8, 64), "q4": (4, 64), "q3": (3, 64),
                   "q2": (2, 64), "sentinel": (4, 64)}
    keys = args.configs.split(",") if args.configs else list(ALL_CONFIGS)
    CONFIGS = {k: ALL_CONFIGS[k] for k in keys}

    print(f"=== Step-1 shakedown ===\n model: {model_id}\n items: {n_items}  judges: {len(judges)} {judges}\n"
          f" trials: {trials}  configs: {list(CONFIGS)}\n")

    # 1) generate
    gens = {}   # (config, item_idx) -> text
    for cname, (bits, gs) in CONFIGS.items():
        t0 = time.time()
        model, tok = load_config(model_id, bits, gs)
        for i, task in enumerate(tasks):
            prompt = SENTINEL_PROMPT if cname == "sentinel" else task   # sentinel = off-topic
            gens[(cname, i)] = gen_mlx(model, tok, prompt, args.max_tokens)
        del model
        print(f" generated {cname:8s} ({time.time()-t0:.0f}s)")

    # 2) judge (blind: judges never see which config produced a response).
    # Judge-OUTERMOST so each (large) judge model loads into memory exactly once and
    # scores everything, instead of thrashing in/out per item.
    rows = []
    total = len(CONFIGS) * n_items * len(judges) * trials
    done = 0
    for jg in judges:
        t0 = time.time()
        for cname in CONFIGS:
            for i, task in enumerate(tasks):
                resp = gens[(cname, i)]
                for _ in range(trials):
                    s = judge_score(jg, task, resp, temperature=args.temp)
                    done += 1
                    if s is not None:
                        rows.append({"item": cname, "judge": jg, "score": s})
        print(f"  judged with {jg:42s} ({time.time()-t0:.0f}s, {done}/{total})", flush=True)

    # 3) gauge
    import msai_eval as msai
    print("\n" + "=" * 70 + "\nSTEP 1a — qualify the gauge\n" + "=" * 70)
    rel = msai.reliability(rows, level="ordinal")
    rel.summary()
    print("\n" + "=" * 70 + "\nSTEP 1b — acceptance test vs fp16\n" + "=" * 70)
    cmp = msai.compare(rows, baseline="fp16", level="ordinal")
    cmp.summary()

    # 4) the Step-1 gate (guard-band criterion). Raw rows are saved too, so we can pull
    #    e.g. the good-config-only resolution later without re-running the whole panel.
    res = gate_verdict(cmp.gauge, cmp.comparisons)
    json.dump({"gate": "guard_band", **res, "gauge": cmp.gauge,
               "comparisons": cmp.comparisons, "rows": rows},
              open("shakedown/last_result.json", "w"), indent=2, default=str)
    return 0 if res.get("passed", res.get("sharp_enough", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
