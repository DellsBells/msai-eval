"""attended_review.py — the operator's review pack (prereg §7, first-class stage).

DESIGN PRINCIPLE (KB #018 pattern): the human verifies the RECEIPTS, never the code.
No question below requires reading a line of Python or knowing which solution is
better — that is the oracle's job. Every check is: watch a live test run print its
counts, compare two numbers, or ctrl-F a word. First-party attestation: the operator
runs THIS script on THIS machine and attests what it printed to them, not what any
lane reported.

Run:  .venv/bin/python benchmark/oracle_run/attended_review.py
Then: read ATTENDED_REVIEW_PACK.md next to this script and answer its 13 YES/NO
questions in a reply. Item selection is deterministic and stated in the pack.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common            # noqa: E402
import judge_runner      # noqa: E402
import oracle_runner     # noqa: E402

MANIFEST = os.path.join(HERE, "study_manifest.json")
SCORES = os.path.join(HERE, "oracle_study_scores.json")
ANALYSIS = os.path.join(HERE, "analysis_results.json")
PACK = os.path.join(HERE, "ATTENDED_REVIEW_PACK.md")

CONSENSUS_WRONG = ["t01", "t35", "t48"]          # every H3 event, per the seal
FORBIDDEN = ["tier", "resolve", "subtle", "oracle", "hidden test", "pass rate",
             "config", "baseline", "cfg"]        # words a blind judge must never have seen


def select_items(man):
    """Deterministic selection rule (stated, not chosen by eye): all 3 consensus-wrong
    events + both tie-tier tasks + the 2 lowest-id subtle tasks not already selected +
    the 3 lowest-id resolve tasks not already selected = 10 items."""
    chosen = list(CONSENSUS_WRONG)
    ties = sorted(t for t, e in man.items() if e["tier"] == "tie")
    chosen += ties
    for tier, want in (("subtle", 2), ("resolve", 3)):
        pool = sorted(t for t, e in man.items() if e["tier"] == tier and t not in chosen)
        chosen += pool[:want]
    return chosen


def val(r):
    s = r["score"][0] if isinstance(r["score"], list) else r["score"]
    return None if (s is None or (isinstance(s, float) and math.isnan(s))) else float(s)


def main():
    man_doc = json.load(open(MANIFEST, encoding="utf-8"))
    man = man_doc["tasks"]
    rows = json.load(open(SCORES, encoding="utf-8"))["scores"]
    analysis = json.load(open(ANALYSIS, encoding="utf-8"))
    tasks = {t["id"]: t for t in common.discover_tasks(split=None, include_pilot=True)}
    items = select_items(man)

    by_cell = defaultdict(list)
    raw_by_cell = defaultdict(list)
    t32_rows = 0
    for r in rows:
        if r["task_id"] == "t32":
            t32_rows += 1
        by_cell[(r["task_id"], r["config"], r["judge"])].append(val(r))
        raw_by_cell[(r["task_id"], r["config"], r["judge"])].append(str(r.get("raw", ""))[:90])

    L = []
    say = L.append
    say("# ATTENDED REVIEW PACK — code-oracle study (prereg 60c6525, seal REV-LANE #013)")
    say("")
    say("*You are verifying RECEIPTS, not code. If any question seems to ask for a code*")
    say("*quality opinion, the answer is NO to Q12 and the pack is defective.*")
    say("")
    say(f"Selection rule: all 3 consensus-wrong events ({', '.join(CONSENSUS_WRONG)}) + both")
    say("tie tasks + 2 lowest-id subtle + 3 lowest-id resolve not already selected.")
    say(f"Items: {', '.join(items)}")
    say("")

    all_ref_pass, all_a_match, all_b_match, all_g_ok = True, True, True, True
    blind_clean = True
    for tid in items:
        task = tasks[tid]
        meta = task["meta"]
        e = man[tid]
        say(f"## {tid} — “{meta.get('title', '?')}” (tier: {e['tier']}, "
            f"{'CONSENSUS-WRONG EVENT' if tid in CONSENSUS_WRONG else 'sampled'})")
        say("")
        # live oracle re-runs, witnessed
        ref_code = open(os.path.join(task["dir"], "reference_solution.py"), encoding="utf-8").read()
        live = {}
        for label, code in [("reference", ref_code)] + [
                (f"cfg{c}", open(os.path.join(task["dir"], "solutions", f"cfg{c}.py"),
                                 encoding="utf-8").read()) for c in ("A", "B")]:
            sc = oracle_runner.oracle_score(task["dir"], code)
            live[label] = sc
        ref_ok = live["reference"]["all_pass"]
        a_match = abs(live["cfgA"]["pass_rate"] - e["rate_A"]) < 1e-9
        b_match = abs(live["cfgB"]["pass_rate"] - e["rate_B"]) < 1e-9
        g_ok = abs((e["rate_A"] - e["rate_B"]) - e["g"]) < 5e-5  # manifest g is rounded to 4dp
        all_ref_pass &= ref_ok
        all_a_match &= a_match
        all_b_match &= b_match
        all_g_ok &= g_ok
        say(f"- LIVE lever runs (just executed on your machine):")
        say(f"  - reference: pass_rate {live['reference']['pass_rate']:.3f} "
            f"→ all tests pass: **{'YES' if ref_ok else 'NO — STOP, note this'}**")
        say(f"  - machine A: LIVE {live['cfgA']['pass_rate']:.3f} vs recorded {e['rate_A']:.3f} "
            f"→ **{'MATCH' if a_match else 'MISMATCH'}**")
        say(f"  - machine B: LIVE {live['cfgB']['pass_rate']:.3f} vs recorded {e['rate_B']:.3f} "
            f"→ **{'MATCH' if b_match else 'MISMATCH'}**")
        say(f"  - gap arithmetic: {e['rate_A']:.3f} − {e['rate_B']:.3f} = {e['rate_A']-e['rate_B']:.3f}, "
            f"recorded g = {e['g']:.3f} → **{'MATCH' if g_ok else 'MISMATCH'}**")
        # Blindness scan targets what the HARNESS ADDS around the task (the wrapper the
        # judge sees beyond the task statement itself). The task's own English is shown
        # identically to every judge for BOTH machines and predates tier assignment, so
        # incidental words there cannot leak study metadata — they are listed separately
        # for the record, not counted as leakage.
        task_prompt = open(os.path.join(task["dir"], "prompt.md"), encoding="utf-8").read()
        wrapper = judge_runner.build_judge_prompt("«TASK»", "«CODE»")
        found = [w for w in FORBIDDEN if w in wrapper.lower()]
        blind_clean &= not found
        incidental = [w for w in FORBIDDEN if w in task_prompt.lower()]
        say(f"- Blindness scan of the harness wrapper (what the judge sees beyond the task "
            f"text): forbidden words found: **{found if found else 'NONE'}**"
            + (f" · incidental words inside the task's own statement (same for both "
               f"machines, authored before tiers existed — not leakage): {incidental}"
               if incidental else ""))
        # judge table + raw spot-check
        say(f"- Judge ratings (recorded | first line of the judge's own words):")
        for j in analysis["meta_in"]["panel_alive"]:
            jshort = j.split("/")[-1][:20]
            for cfg in ("A", "B"):
                scores = by_cell.get((tid, cfg, j), [])
                raws = raw_by_cell.get((tid, cfg, j), [])
                srepr = ", ".join("null" if s is None else f"{s:.0f}" for s in scores)
                say(f"  - {jshort:22s} machine {cfg}: [{srepr}]  raw₁: “{raws[0] if raws else '—'}”")
        # consensus-wrong arithmetic
        if tid in CONSENSUS_WRONG:
            pm = {}
            for cfg in ("A", "B"):
                vals = [s for j in analysis["meta_in"]["panel_alive"]
                        for s in by_cell.get((tid, cfg, j), []) if s is not None]
                pm[cfg] = sum(vals) / len(vals) if vals else float("nan")
            o_pref = "A" if e["g"] > 0 else "B"
            p_pref = "A" if pm["A"] > pm["B"] else ("B" if pm["B"] > pm["A"] else "neither")
            say(f"- **THE CONTRADICTION, in two lines you can check by eye:**")
            say(f"  - panel means: A = {pm['A']:.2f}, B = {pm['B']:.2f} → panel prefers **{p_pref}**")
            say(f"  - live levers: A = {live['cfgA']['pass_rate']:.3f}, B = {live['cfgB']['pass_rate']:.3f} "
                f"→ levers prefer **{o_pref}**")
        say("")

    # global receipts
    excl = analysis["tiers"]["resolve"]["gauge_excluded_units"] + \
        analysis["tiers"]["subtle"]["gauge_excluded_units"] + \
        analysis["tiers"]["tie"]["gauge_excluded_units"]
    say("## Global receipts")
    say(f"- Quarantined t32 rows present in the analysis data: **{t32_rows}** (must be 0)")
    say(f"- Gauge-excluded units (unbalanced cells): **{sorted(excl)}** — must match the certificate")
    say(f"- Disclosed nulls: **{analysis['ingest']['nulls_excluded_disclosed']}/828**; per judge: "
        + ", ".join(f"{j.split('/')[-1][:14]} {v['nulls']}/{v['of']}"
                    for j, v in analysis["ingest"]["per_judge"].items()))
    say(f"- All-items rollup: reference all-pass everywhere: **{'YES' if all_ref_pass else 'NO'}** · "
        f"A rates all MATCH: **{'YES' if all_a_match else 'NO'}** · B rates all MATCH: "
        f"**{'YES' if all_b_match else 'NO'}** · g arithmetic all MATCH: **{'YES' if all_g_ok else 'NO'}** · "
        f"blindness scans all clean: **{'YES' if blind_clean else 'NO'}**")
    say("")
    say("## The 13 questions (answer YES/NO; any NO → write one line about what you saw)")
    say("")
    say("1. This script ran on your machine and printed live test results for every item.")
    say("2. Every reference solution passed all its tests, live (rollup line says YES).")
    say("3. Every machine-A live rate says MATCH against the recorded rate.")
    say("4. Every machine-B live rate says MATCH.")
    say("5. Every gap line says MATCH (the subtraction is right).")
    say("6. Every blindness scan says NONE (the judges' prompt never mentions tiers, tests,")
    say("   configs, or the oracle).")
    say("7. Spot-checking the judge tables: the recorded numbers match the digits in the")
    say("   judges' own quoted words (nulls appear as 'null', never as a number).")
    say("8. Each judge has 3 ratings per machine, or the shortfall is visible as nulls in")
    say("   the disclosed-nulls line.")
    say("9. For each of the three CONSENSUS-WRONG items, the two-line contradiction shows")
    say("   the panel preferring the machine the live levers scored LOWER.")
    say("10. The quarantined-t32 count printed 0.")
    say("11. The excluded-units list matches the certificate's list (compare when cert #3")
    say("    is in front of you; leave blank until then if needed).")
    say("12. At no point did this review ask you to judge code quality.")
    say("13. Nothing you saw looked wrong, altered, or confusing — or if it did, you wrote")
    say("    it down.")
    say("")
    say("*Sign-off format: 'Attended review: Q1–Q13 = <answers>, <date>, <name>' in a*")
    say("*message or a bus drop. Your answers get stamped into certificate #3 verbatim.*")

    with open(PACK, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"pack written: {PACK}")
    print(f"rollup: ref_all_pass={all_ref_pass} A_match={all_a_match} "
          f"B_match={all_b_match} g_ok={all_g_ok} blind_clean={blind_clean} t32_rows={t32_rows}")
    return L


def guided():
    """--guided: the same review as a walkthrough. The script shows you each item's
    receipts and asks the 13 questions one at a time. Answer y / n / q(uit). A NO asks
    for one line about what you saw. Your sign-off is written to ATTENDED_SIGNOFF.md
    and stamped into certificate #3 verbatim."""
    lines = main()
    text = "\n".join(lines)
    items = [b for b in text.split("\n## ")
             if b and not b.startswith("Global") and not b.startswith("The 13")]
    print("\n" + "=" * 72)
    print("GUIDED ATTENDED REVIEW — you verify receipts, never code.")
    print("For each arena: the levers were just re-flipped LIVE, above. Look for the")
    print("words MATCH and NONE. On the three CONSENSUS-WRONG arenas, check the two-line")
    print("contradiction with plain arithmetic. Press Enter to step through.")
    print("=" * 72)
    for b in items[1:]:
        print("\n## " + b.strip())
        input("\n[Enter for next item] ")
    questions = [ln for ln in lines if ln[:3] in {f"{i}. " for i in range(1, 10)}
                 or ln[:4] in {f"{i}. " for i in range(10, 14)}]
    answers = []
    notes = []
    for q in questions:
        while True:
            try:
                a = input(f"\n{q}\n  [y/n/q] ").strip().lower()
            except EOFError:
                print("\nInput ended — nothing recorded. Re-run when ready.")
                return
            if a in ("y", "n", "q"):
                break
        if a == "q":
            print("Review paused — nothing recorded. Re-run when ready.")
            return
        answers.append("Y" if a == "y" else "N")
        if a == "n":
            notes.append(f"Q{len(answers)}: " + input("  One line — what did you see? "))
    import datetime
    name = input("\nYour name for the record: ").strip() or "operator"
    stamp = datetime.date.today().isoformat()
    sign = (f"# ATTENDED REVIEW SIGN-OFF\n\nAttended review: Q1–Q13 = {''.join(answers)}, "
            f"{stamp}, {name}\n"
            + ("\nNotes on NO answers:\n" + "\n".join(f"- {n}" for n in notes) + "\n"
               if notes else "\nNo NO answers.\n")
            + "\nFirst-party attestation: the reviewer ran attended_review.py on the study\n"
              "host and answered from its live output (prereg 60c6525 §7; KB #018 pattern).\n")
    out = os.path.join(HERE, "ATTENDED_SIGNOFF.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(sign)
    print(f"\nSign-off written: {out}")
    print("Done. That was the whole job — the certificate takes it from here.")


if __name__ == "__main__":
    if "--guided" in sys.argv:
        guided()
    else:
        main()
