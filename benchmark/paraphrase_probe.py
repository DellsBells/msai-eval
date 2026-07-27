"""paraphrase_probe.py — Fable's K=3 pilot. Is paraphrase×condition variance MATERIAL (RESOLVED verdicts
exposed) or NEGLIGIBLE (disclose + done)?

Metrology (Fable, self-corrected + KB-grounded): paraphrase invariance is NOT repeatability (the prompt IS the
procedure, so rewording is a different method realization) — it's definitional uncertainty + method ruggedness,
a MISSING budget line item. Its MAIN effect cancels in the config-vs-baseline delta (same algebra as GLM's
judge level-shift); the ×CONDITION interaction (a rewording that flips which answer looks better) does NOT and
belongs in the delta band. Temp 0 isolates paraphrase from sampling noise. K=3 realizations vary wording /
order / format; NEVER the 1-5 anchors.

Exposure is asymmetric: a non-negative term can only WIDEN the band -> the 'below resolution' keystone is safe
(can only get more below); the RESOLVED tier is what a material term could flip. So we probe resolve + subtle.
"""
import json
import os
import sys
import urllib.request

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import elo_validation as ev

JUDGES = ["gemma4:12b", "gemma4:31b-mlx", "qwen3.5:27b", "qwen3.6:35b-mlx", "qwen2.5-coder:32b"]

# K=3 semantically-equivalent rubric realizations — vary wording / order / format, hold the 1-5 anchors fixed.
TEMPLATES = [
    "Rate the QUALITY of this answer to the prompt on a 1-5 scale (5=excellent, 1=poor). Reply with ONLY the "
    "digit.\n\nPROMPT: {p}\n\nANSWER: {r}\n\nQuality (1-5):",
    "On a scale from 1 (poor) to 5 (excellent), how good is this response to the question? Respond with just "
    "the number.\n\nQUESTION: {p}\n\nRESPONSE: {r}\n\nScore:",
    "You are grading answer quality. Output one integer 1-5 (1=poor, 5=excellent), digit only.\n\n[Task]\n{p}"
    "\n[Answer]\n{r}\n[Rating 1-5]:",
]


def score(model, template, prompt, resp):
    body = json.dumps({"model": model, "prompt": template.format(p=prompt, r=resp), "stream": False,
                       "think": False, "keep_alive": "10m",
                       "options": {"temperature": 0, "num_predict": 8}}).encode()
    try:
        out = json.loads(urllib.request.urlopen(urllib.request.Request(
            ev.OLLAMA, body, {"Content-Type": "application/json"}), timeout=300).read())
        return ev.parse_rating(out.get("response", ""))
    except Exception:
        return float("nan")


# current delta-gauge SD per tier (to judge whether the paraphrase term is material) — from the keystone run
try:
    kr = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keystone_result.json")))
except Exception:
    kr = {"tiers": {}}


def grr_delta(tier):
    rb = (kr.get("tiers", {}).get(tier, {}) or {}).get("resolution_budget") or {}
    return rb.get("grr_sd_delta"), (kr.get("tiers", {}).get(tier, {}) or {}).get("guard_band"), \
        (kr.get("tiers", {}).get(tier, {}) or {}).get("delta")


lad = ev.keystone_ladder(n_per_tier=6, seed=0)
print(f"paraphrase probe — K={len(TEMPLATES)} rubric realizations, temp 0, judges={JUDGES}\n")
for tier in [t for t in lad if t["name"] in ("resolve", "subtle")]:
    within_sd, per_tmpl = [], {ti: [] for ti in range(len(TEMPLATES))}
    for pair in tier["pairs"]:
        for j in JUDGES:
            dl = []
            for ti, tmpl in enumerate(TEMPLATES):
                sc, sr = score(j, tmpl, pair["prompt"], pair["chosen"]), score(j, tmpl, pair["prompt"], pair["rejected"])
                if np.isnan(sc) or np.isnan(sr):
                    continue
                dl.append(sc - sr)
                per_tmpl[ti].append((sc + sr) / 2.0)
            if len(dl) >= 2:
                within_sd.append(np.std(dl))            # SD of the DELTA across paraphrases (within pair,judge)
    sigma_pxc = float(np.mean(within_sd)) if within_sd else float("nan")
    tmpl_means = {ti: round(float(np.mean(v)), 2) for ti, v in per_tmpl.items() if v}
    grr_d, band, delta = grr_delta(tier["name"])
    print(f"=== {tier['name']} tier (n={len(tier['pairs'])}) ===")
    print(f"  paraphrase MAIN effect (mean score per template — should differ => paraphrases DO shift levels; "
          f"cancels in delta): {tmpl_means}")
    print(f"  sigma_paraphrase×condition (SD of chosen-rejected delta across templates) = {sigma_pxc:.3f}")
    if grr_d:
        widened = float(np.sqrt(grr_d ** 2 + sigma_pxc ** 2))
        new_band = (band / grr_d) * widened if grr_d > 0 else band   # scale band by the grr ratio
        print(f"  current grr_sd_delta={grr_d:.3f}, band={band:.3f}, |Δ|={abs(delta):.2f}")
        print(f"  + paraphrase term -> grr_sd_delta'={widened:.3f}, band'~{new_band:.3f}  "
              f"=> {tier['name']} would read {'RESOLVED' if abs(delta) > new_band else 'BELOW resolution'}")
        print(f"  MATERIAL? sigma_pxc/grr_sd_delta = {sigma_pxc / grr_d:.2f}  "
              f"({'NEGLIGIBLE' if sigma_pxc < 0.2 * grr_d else 'MATERIAL — RESOLVED verdicts need the wider band'})")
    print()
