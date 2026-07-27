"""certificate.py — render a GAUGE CERTIFICATE from a persisted frontier run.

The calibration certificate is metrology's load-bearing artifact: a standardized document
a decision-maker can hold, listing what the instrument can resolve, at what uncertainty,
under what conditions, with every limitation disclosed. This module renders one for an
LLM-as-judge panel, from persisted scores, through the SAME validated path as
frontier_reanalyze.py (compare() + four_state()) — presentation layer only, no new stats.

Honesty contract (inherited, printed, non-negotiable):
  - Precision/reproducibility only. NO ACCURACY CLAIMED — no traceable reference.
  - Consensus anchors are agreement, not correctness (shared bias is invisible to this gauge).
  - Every gauge warning is reproduced verbatim in the Disclosures section.

Usage:
  .venv/bin/python benchmark/certificate.py [scores.json] [--out CERT.md] \
      [--data-date YYYY-MM-DD] [--print]
  (defaults: frontier_api_scores.json -> CERTIFICATE_<id>.md next to it)

Hardening (cross-organ audit 2026-07-02): utf-8 + atomic writes (REV-006), argparse
(REV-006 --out bug), declared data-date instead of file mtime + stated k coverage basis
(REV-011), literal NO ACCURACY CLAIMED banner (REV-016), renderer version + results
digest pinned alongside the scores-hash certificate number (REV-020), evidential-status
disclosures for the findings that bear on this instance's basis (REV-001/005/015).

NOTE (done, commit B): the four-state/dof contract now lives in the package
(`msai_eval.resolution.four_state`) and compare() attaches a typed `resolution_verdict` key.
This renderer imports four_state from the package and still computes the table itself (same
call, same n/seed) so the certificate numbers reproduce bit-for-bit off the same code path.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elo_validation as ev                      # noqa: E402  (msai package + judge plumbing)
from msai_eval.resolution import four_state       # noqa: E402  (folded into the package, commit B)

SPEC_VERSION = "MSAI-GC/1.0-draft"
TIERS = ("resolve", "subtle", "tie")
ANCHOR = {
    "resolve": "RewardBench pairs, Arena-Elo gap-anchored (mean gap ~309 Elo)",
    "subtle":  "MT-Bench pairs, human preference margin ~0.68 (the keystone tier)",
    "tie":     "MT-Bench pairs, human preference margin ~0.33 (negative control)",
}
STATE_MEANING = {
    "RESOLVED":     "real gap; magnitude certified above the gauge's resolution",
    "AT-EDGE":      "real gap at the gauge's resolution edge; no side can be forced",
    "BELOW":        "statistically real, but below resolution — magnitude NOT certified",
    "WITHIN-NOISE": "not distinguishable from zero on this gauge",
}


def _pkg_version():
    try:
        from importlib.metadata import version
        return version("msai-eval")
    except Exception:
        try:
            import msai_eval
            return getattr(msai_eval, "__version__", "unknown")
        except Exception:
            return "unknown"


def _load(scores_path):
    with open(scores_path, encoding="utf-8") as f:
        d = json.load(f)
    by = defaultdict(list)
    n_null = 0
    for s in d["scores"]:
        if s["score"] is None:
            n_null += 1          # KB #018 exhibit: nulls are EXCLUDED and DISCLOSED,
            continue             # never coerced to a score or a failure.
        by[s["tier"]].append({"item": s["config"], "unit": f"{s['tier']}_{s['pair']}",
                              "judge": s["judge"], "score": s["score"]})
    return by, d.get("meta", {}), n_null


def _comp_name(c, i):
    for k in ("name", "source", "component", "label"):
        if c.get(k):
            return str(c[k])
    return f"component_{i}"


def _find_cliffs(cmp):
    for k, v in cmp.items():
        if "cliff" in k.lower() and isinstance(v, (int, float)):
            return v
        if "cliff" in k.lower() and isinstance(v, dict):
            for kk in ("delta", "value", "estimate"):
                if isinstance(v.get(kk), (int, float)):
                    return v[kk]
    return None


def analyze(by_tier):
    """Per tier: compare() -> four_state() under both dof modes. Same path as frontier_reanalyze."""
    out = {}
    for tier in TIERS:
        rows = by_tier.get(tier, [])
        if not rows:
            continue
        c = ev.msai.compare(rows, baseline="rejected", level="ordinal", resolution=1.0).to_dict()
        cmp = c["comparisons"]["chosen"]
        g = c.get("gauge") or {}
        rb = g.get("resolution_budget")
        entry = {"delta": cmp["delta"], "ci": cmp.get("ci"), "sig": bool(cmp.get("significant_adj")),
                 "cliffs": _find_cliffs(cmp), "gauge": g, "rb": rb, "qualified": bool(g.get("qualified"))}
        if entry["qualified"] and rb:
            entry["ws"] = four_state(entry["delta"], entry["ci"], rb, entry["sig"], dof_mode="ws")
            entry["dom"] = four_state(entry["delta"], entry["ci"], rb, entry["sig"], dof_mode="dominant")
        out[tier] = entry
    return out


def _resolve_scores_path(p):
    if p is None:
        return os.path.join(HERE, "frontier_api_scores.json")
    if not os.path.isabs(p) and not os.path.exists(p):
        cand = os.path.join(HERE, p)
        if os.path.exists(cand):
            return cand
    return p


def _atomic_write(path, text):
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def render(scores_path=None, out_path=None, data_date=None):
    scores_path = _resolve_scores_path(scores_path)
    with open(scores_path, "rb") as f:
        raw = f.read()
    cert_id = "MSAI-" + hashlib.sha256(raw).hexdigest()[:12].upper()
    by_tier, meta, n_null = _load(scores_path)
    res = analyze(by_tier)

    judges = meta.get("judges", {})
    n_scores = sum(len(v) for v in by_tier.values())
    measured = data_date or meta.get("date") or \
        "UNSTATED — supply --data-date (file metadata is not evidence; see run log)"
    issued = date.today().isoformat()
    J, R, n = len(judges), meta.get("R", "?"), meta.get("n", "?")

    L = []
    A = L.append
    A("# GAUGE CERTIFICATE — LLM-AS-JUDGE MEASUREMENT SYSTEM")
    A("")
    A(f"**Certificate no.** `{cert_id}` &nbsp;·&nbsp; **Issued** {issued} &nbsp;·&nbsp; "
      f"**Data of** {measured} &nbsp;·&nbsp; **Basis** {n_scores} blind ratings "
      f"({n_null} null-score rows excluded, disclosed) "
      f"(sha256-bound to `{os.path.basename(scores_path)}`) &nbsp;·&nbsp; "
      f"**Format** `{SPEC_VERSION}` (docs/CERTIFICATE_SPEC.md)")
    A("")
    A("> **NO ACCURACY CLAIMED.** This certificate states what the measurement system can")
    A("> **resolve** — its precision, reproducibility, and resolution under the stated conditions.")
    A("> **It does not state that the system's judgments are correct.** No traceable reference was")
    A("> supplied; accuracy without a traceable reference is undefined. High panel agreement is")
    A("> equally consistent with a correct rubric, a shared wrong rubric, or successful gaming —")
    A("> shared-bias detection is outside this gauge's scope, by construction.")
    A("")
    A("## 1. Measurement system under qualification")
    A("")
    A("| | |")
    A("|---|---|")
    A(f"| Instrument | Panel of {J} LLM judges, distinct provider lineages (see Disclosures: "
      f"training-data independence is NOT established) |")
    for k, v in judges.items():
        A(f"| &nbsp;&nbsp;— {k} | `{v}` |")
    A(f"| Procedure | Blind, self-contained 1–5 quality rating; one response per call; "
      f"opaque IDs; no pairwise exposure |")
    A(f"| Replication | R={R} independent re-scorings per response; temperature >0 "
      f"(per-provider details: `frontier_run_log.md`) |")
    A(f"| Measurand | Δ = mean(config) − mean(baseline), balanced crossed design, "
      f"per-pair `unit`; judge level main-effect cancels (delta basis) |")
    A(f"| Design | {n} pairs/tier × 2 configs × {J} judges × R={R} |")
    A("")
    A("## 2. Reference conditions (consensus anchors — NOT traceable references)")
    A("")
    for t in TIERS:
        if t in res:
            A(f"- **{t}** — {ANCHOR[t]}")
    A("")
    A("## 3. Results — resolution verdicts per tier")
    A("")
    A("State machine: WITHIN-NOISE / BELOW / AT-EDGE / RESOLVED. The band U carries its own")
    A("confidence interval (fiducial, from its effective dof); a significant Δ inside [U_lo, U_hi]")
    A("reads AT-EDGE — the gauge refuses to force a side it cannot support. Contract dof: WS νeff")
    A("(GUM); dominant-dof shown as conservative disclosure.")
    A("")
    A("**Two-band structure (REV-001):** the verdict gate — the band `U` in the table below — is the")
    A("gauge DISCRIMINATION band (Band B): a per-use expanded uncertainty (AIAG ndc family / JCGM 106")
    A("§8.3.3.2 w=rU form) that does NOT shrink with study size. The uncertainty of the ESTIMATED mean")
    A("difference (Band A, k·u(Δ̂), VIM §2.47) is a separate quantity that DOES shrink with N — the ± on")
    A("Δ, carried by the CI, never the gate. 'Statistically real but BELOW resolution' is the coherent")
    A("state where Band A excludes 0 yet |Δ| < Band B (a caliper can establish a 0.02 mm mean difference")
    A("from 1000 readings and still be unable to discriminate those two parts in the hand). An earlier")
    A("draft mislabeled Band B as the GUM U of the estimate and speculated BELOW/AT-EDGE might promote")
    A("under correction — wrong on both counts, corrected 2026-07-02 (commit A). Both bands now ride each")
    A("comparison as typed fields (`bands`, `resolution_verdict`); this table shows Band B, the gate.")
    A("")
    A("**Coverage basis (spec §4):** every U on this certificate is expanded at ~95 % coverage,")
    A("k = t(ν_eff) with ν_eff per Welch–Satterthwaite, JCGM 100:2008 §G.4.1 Eq. (G.2b);")
    A("per-tier k and ν_eff are printed below.")
    A("")
    A("**Decision rule as used (spec §6.7; ILAC-G8 §4.2.3 / ISO 17025 §7.1.3):** four-state per")
    A("spec §5; AT-EDGE zone = U's 95 % fiducial CI from ν_eff; state dof = WS ν_eff; analysis")
    A("knobs guard_k=2.0 (library default), resolution=1.0, level=ordinal. **Timing attested:**")
    A("a 20 %-of-band edge rule was pre-registered before scoring; the CI-based edge zone,")
    A("ratified after scores existed, superseded it. The three §3 verdicts are identical under")
    A("either rule on this data. Post-hoc rule evolution is disclosed, not hidden; no knob was")
    A("tuned against a verdict outcome (see frontier_run_log.md).")
    A("")
    A("| tier | Δ | Cliff's δ | U (k·u_c) | U 95% CI | νeff | P(\\|Δ\\|>U) | **verdict [WS]** | verdict [dom] |")
    A("|---|---|---|---|---|---|---|---|---|")
    for t in TIERS:
        e = res.get(t)
        if not e:
            continue
        if not e.get("ws"):
            A(f"| {t} | {e['delta']:+.2f} | — | — | — | — | — | GAUGE UNQUALIFIED | — |")
            continue
        w, dm = e["ws"], e["dom"]
        cl = f"{e['cliffs']:+.2f}" if e.get("cliffs") is not None else "—"
        A(f"| {t} | {e['delta']:+.2f} | {cl} | {w['U']:.2f} | [{w['U_lo']:.2f}, {w['U_hi']:.2f}] | "
          f"{w['nu_eff']:.1f} | {w['p_beyond']:.2f} | **{w['state']}** | {dm['state']} |")
    A("")
    for t in TIERS:
        e = res.get(t)
        if e and e.get("ws"):
            A(f"- **{t} → {e['ws']['state']}** — {STATE_MEANING[e['ws']['state']]}.")
            if e.get("dom") and e["dom"]["state"] != e["ws"]["state"]:
                A(f"  - *Caveat (travels with the claim): under the conservative dominant-dof rule "
                  f"this verdict reads **{e['dom']['state']}**. Quote both or quote neither.*")
    A("")
    A("## 4. Uncertainty budget (per tier)")
    A("")
    names = []
    for t in TIERS:
        rb = (res.get(t) or {}).get("rb")
        if rb:
            for i, c in enumerate(rb.get("components", [])):
                nm = _comp_name(c, i)
                if nm not in names:
                    names.append(nm)
    if names:
        hdr = "| component (u, 1σ) | " + " | ".join(t for t in TIERS if t in res) + " |"
        A(hdr)
        A("|---" * (1 + sum(1 for t in TIERS if t in res)) + "|")
        for nm in names:
            row = [nm]
            for t in TIERS:
                rb = (res.get(t) or {}).get("rb")
                val = "—"
                if rb:
                    for i, c in enumerate(rb.get("components", [])):
                        if _comp_name(c, i) == nm:
                            dof = c.get("dof")
                            try:
                                dof = f"{float(dof):.0f}" if dof is not None and float(dof) == float(dof) else "∞"
                            except (TypeError, ValueError, OverflowError):
                                dof = "∞"
                            val = f"{float(c['u']):.3f} (dof {dof})"
                            break
                row.append(val)
            A("| " + " | ".join(row) + " |")
        A("")
        for t in TIERS:
            rb = (res.get(t) or {}).get("rb")
            if rb:
                dom = rb.get("dominant")
                if isinstance(dom, dict):
                    dom = f"{dom.get('source', '?')} ({dom.get('pct', '?')}% of u_c²)"
                A(f"- **{t}**: u_c={float(rb['u_c']):.3f}, k={float(rb['k']):.2f}, U={float(rb['U']):.2f}; "
                  f"dominant lever: {dom}; "
                  f"grr_sd (delta basis)={float(rb.get('grr_sd_delta', float('nan'))):.3f} "
                  f"vs (full)={float(rb.get('grr_sd_full', float('nan'))):.3f}")
    A("")
    A("## 5. Disclosures and limitations (verbatim from the gauge, plus standing caveats)")
    A("")
    seen = set()
    for t in TIERS:
        e = res.get(t)
        if not e:
            continue
        for w in (e["gauge"].get("warnings") or []):
            key = (t, w[:60])
            if key not in seen:
                seen.add(key)
                A(f"- `[{t}]` {w}")
    if J < 5:
        A(f"- PROVISIONAL (spec §6.6): panel has {J} (<5) independent judges — RESOLVED/BELOW/"
          f"WITHIN-NOISE verdicts on this certificate are provisional; bands are unstable at this J.")
    A("- Pilot scale: n={}/tier; results are directional at this n.".format(n))
    A("- Ordinal 1–5 scores treated as interval for variance decomposition (disclosed approximation).")
    A("- Cross-anchor: resolve is Elo-gap-anchored; subtle/tie are human-margin-anchored.")
    A("- Anchors are human consensus — agreement, not ground truth.")
    A(f"- NULL PATH (KB #018 exhibit): {n_null} rating rows carried null scores and were")
    A("  EXCLUDED from analysis — disclosed here. Exclusion is never coercion: a null is")
    A("  not a low score and not a failure; it is an absence, and absences are counted.")
    A("- Scope: frozen-fixture (single rubric wording). A rubric-robust scope adds a measured")
    A("  paraphrase×condition term to the budget. NOTE (REV-015): the available paraphrase")
    A("  estimate (~30% of gauge noise) was measured on a DIFFERENT instrument (local pilot")
    A("  panel, temperature 0), not this frontier panel — it is indicative, not this gauge's value.")
    A("- EVIDENTIAL BASIS UNDER REVIEW (cross-organ audit 2026-07-02, REV-005): raw judge")
    A("  completions were NOT persisted for this run — the hash binds parser outputs, not the")
    A("  judges' text, and the run used a parser variant that differs from the project's")
    A("  ledger-validated parser. Scores cannot be re-audited from evidence without a re-run")
    A("  that persists raw completions and parses via the validated path. Until then, treat")
    A("  the verdict magnitudes as provisional.")
    A("- SHARED-EXPOSURE CAVEAT (REV-005): judged responses derive from public 2023-era")
    A("  benchmarks; all panel judges plausibly trained on these items and on published")
    A("  judge scorings of them. Shared exposure would deflate the between-judge term (this")
    A("  certificate's dominant lever) and tighten U. \"Distinct provider lineages\" does NOT")
    A("  establish training-data independence.")
    A("- BAND CONSTRUCTION UNDER REVIEW (REV-001): the printed U is under review as over-wide")
    A("  for the delta measurand (conservative). A corrected band can only tighten: RESOLVED")
    A("  verdicts are safe a fortiori; BELOW/AT-EDGE verdicts may promote on re-analysis.")
    A("- AT-EDGE on near-tie gaps is consistent with definitional uncertainty of the preference")
    A("  construct itself (panel diversity widens, not tightens, the band there); distinguishing")
    A("  construct ambiguity from shared-lineage bias requires a judge-independent reference.")
    A("")
    A("## 6. Qualification statement")
    A("")
    qual = [t for t in TIERS if (res.get(t) or {}).get("qualified")]
    A(f"The panel QUALIFIES as a comparison gauge on {len(qual)}/{len([t for t in TIERS if t in res])} "
      f"tiers under the stated conditions (balanced crossed design, genuine replication, finite guard")
    A(f"band). It resolves large quality gaps (resolve tier), correctly refuses magnitude claims on")
    A(f"gaps at or below its resolution, and reports its own resolution edge. **This certificate is")
    A(f"void for any use of the panel outside the stated conditions** (different rubric wording,")
    A(f"unbalanced designs, absolute-score thresholds, or accuracy claims).")
    A("")
    if meta.get("cost_usd"):
        A(f"*Run metadata: {meta.get('in_tokens', '?')} in / {meta.get('out_tokens', '?')} out tokens, "
          f"{meta.get('failures', '?')} API failures, ${meta['cost_usd']:.2f} total measurement cost.*")
    A("")
    results_digest = hashlib.sha256(
        "\n".join(l for l in L if l.startswith("| ")).encode("utf-8")).hexdigest()[:12].upper()
    ver = _pkg_version()
    A(f"*Renderer: msai-eval v{ver} · benchmark/certificate.py · results-digest "
      f"`sha256:{results_digest}` (binds this document's §3/§4 tables; the certificate no. binds")
    A(f"only the raw scores — same scores under changed gauge logic yield the same certificate no.")
    A(f"but a different results-digest).*")
    A("")
    A(f"*Generated from persisted scores; verify by re-running:*")
    A(f"`.venv/bin/python benchmark/certificate.py --data-date {data_date or 'YYYY-MM-DD'}`")
    A("")
    text = "\n".join(L)
    out_path = out_path or os.path.join(os.path.dirname(os.path.abspath(scores_path)),
                                        f"CERTIFICATE_{cert_id}.md")
    _atomic_write(out_path, text)
    return out_path, text


def main(argv=None):
    p = argparse.ArgumentParser(description="Render a gauge certificate from persisted scores.")
    p.add_argument("scores", nargs="?", default=None,
                   help="scores JSON (default: frontier_api_scores.json beside this script)")
    p.add_argument("--out", default=None, help="output path (default: CERTIFICATE_<id>.md)")
    p.add_argument("--data-date", default=None,
                   help="measurement date YYYY-MM-DD (REQUIRED for spec conformance; "
                        "file metadata is deliberately not used)")
    p.add_argument("--print", dest="do_print", action="store_true",
                   help="print the full certificate to stdout (utf-8 errors replaced)")
    a = p.parse_args(argv)
    path, text = render(a.scores, a.out, a.data_date)
    if a.do_print:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.write(text.encode(enc, errors="replace").decode(enc) + "\n")
    sys.stderr.write(f"[written: {path}]\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
